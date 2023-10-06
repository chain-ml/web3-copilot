from typing import List
from pathlib import Path

import toml
import dotenv

from council.agents import Agent
from council.chains import Chain
from council.contexts import AgentContext, SkillContext
from council.filters import BasicFilter
from council.contexts import Budget, Consumption
from council.llm import OpenAILLM, LLMMessage
from council.skills import LLMSkill, PromptToMessages
from council.prompt import PromptBuilder
from council.controllers import LLMController
from council.evaluators import LLMEvaluator

from web3_copilot.common import constants
import logging

from web3_copilot.doc_retrieval.config import Config
from web3_copilot.doc_retrieval import Retriever
from web3_copilot.skills import DocRetrievalSkill, TransactionDebuggerSkill
from web3_copilot.common.utils import create_file_dict

dotenv.load_dotenv()

logging.getLogger("council").setLevel(logging.ERROR)


class Web3CopilotAgent:

    def __init__(self):
        # Initialize database dependencies
        self.config = Config(
            encoding_name=constants.ENCODING_NAME,
            embedding_model_name=constants.EMBEDDING_MODEL_NAME,
            cross_encoder_model_name=constants.CROSS_ENCODER_MODEL_NAME
        )
        self.db_client = self.config.initialize()
        self.retriever = Retriever(self.config)

        # Initialize agent
        self.llm = OpenAILLM.from_env()
        self.init_skills()
        chains = self.init_chains()
        self.controller = LLMController(chains=chains, llm=self.llm, response_threshold=5)
        self.evaluator = LLMEvaluator(self.llm)
        self.agent = Agent(self.controller, self.evaluator, filter=BasicFilter(), name="Web3Copilot")

    def init_skills(self):
        # Skills for document retrieval
        self.doc_retrieval_skills = {}

        indices = list(create_file_dict(constants.DATA_DIR).keys())
        for index in indices:
            self.doc_retrieval_skills[index] = DocRetrievalSkill(
                db_client=self.db_client,
                collection_name=index,
                retriever=self.retriever,
            )

        # Skill to interact with LLM for document retrieval
        self.dr_llm_skill = LLMSkill(
            llm=self.llm,
            system_prompt=self.load_system_prompt("doc_retrieval"),
            context_messages=self.build_context_message
        )

        # Skills for transaction debugger
        self.txn_debugger_skill = TransactionDebuggerSkill(
            config=self.config
        )

        # Skill to interact with LLM transaction debugger
        self.txn_debugger_llm_skill = LLMSkill(
            llm=self.llm,
            system_prompt=self.load_system_prompt("txn_debugger"),
            context_messages=self.build_context_message
        )

    def init_chains(self) -> List[Chain]:
        chains = []

        for index, doc_retrieval_skill in self.doc_retrieval_skills.items():
            chains.append(
                Chain(
                    name=f"{index}_doc_retrieval",
                    description=toml.load(
                        "./web3_copilot/templates/doc_retrieval/document_descriptions.toml"
                    )[index]["description"].format(index=index),
                    runners=[doc_retrieval_skill, self.dr_llm_skill],
                )
            )

        txn_debugger_desc = "Provide more details about transactions such as why they failed or succeeded."
        chains.append(
            Chain(
                name="txn_debugger_chain",
                description=txn_debugger_desc,
                runners=[self.txn_debugger_skill, self.txn_debugger_llm_skill],
            )
        )

        return chains

    def load_system_prompt(self, skill: str):
        system_prompt_file = ""

        if skill == "txn_debugger":
            system_prompt_file = f"./web3_copilot/templates/{skill}/system_prompt.jinja"
        else:
            system_prompt_file = f"./web3_copilot/templates/{skill}/system_prompt.jinja"

        system_prompt = Path(system_prompt_file).read_text()
        return system_prompt

    def build_context_message(self, context: SkillContext) -> List[LLMMessage]:
        context_message_template = Path(
            "./web3_copilot/templates/context_message_prompt.jinja"
        ).read_text()

        context_message_prompt = PromptToMessages(
            prompt_builder=PromptBuilder(context_message_template)
        )

        messages = context_message_prompt.to_user_message(context)
        return messages

    def interact(self, message):

        api_call_limit = Consumption(10, "call", "API_CALL")

        budget = Budget(
            60,
            limits=[
                api_call_limit,
            ]
        )

        context = AgentContext.from_user_message(message, budget)

        result = self.agent.execute(context=context)
        return result

    def render(self):
        return self.agent.render_as_json()
