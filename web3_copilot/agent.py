from typing import List
from pathlib import Path

import toml
import dotenv

from council.agents import Agent
from council.chains import Chain
from council.contexts import AgentContext, SkillContext, ChatHistory
from council.runners.budget import Budget, Consumption
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
        self.context = AgentContext(chat_history=ChatHistory())
        self.llm = OpenAILLM.from_env()
        self.init_skills()
        chains = self.init_chains()
        self.controller = LLMController(llm=self.llm, top_k_execution_plan=1)
        self.evaluator = LLMEvaluator(self.llm)
        self.agent = Agent(self.controller, chains, self.evaluator)

    def init_skills(self):
        # Skills for document retrieval
        self.doc_retrieval_skills = {}

        # TUTORIAL CODE GOES HERE

        # Skill to interact with LLM for document retrieval
        # TUTORIAL CODE GOES HERE

        # Skills for transaction debugger
        # TUTORIAL CODE GOES HERE

        # Skill to interact with LLM transaction debugger
        # TUTORIAL CODE GOES HERE

    def init_chains(self) -> List[Chain]:
        chains = []

        for index, doc_retrieval_skill in self.doc_retrieval_skills.items():
            chains.append(
                Chain(
                    name=f"{index}_doc_retrieval",
                    description=toml.load(
                        "./web3_copilot/templates/doc_retrieval/document_descriptions.toml"
                    )[index]["description"].format(index=index),
                    # TUTORIAL CODE GOES HERE
                    runners=[],
                )
            )

        txn_debugger_desc = "Provide more details about transactions such as why they failed or succeeded."
        chains.append(
            Chain(
                name="txn_debugger_chain",
                description=txn_debugger_desc,
                # TUTORIAL CODE GOES HERE
                runners=[],
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

        # TUTORIAL CODE GOES HERE

        messages = []
        return messages

    def interact(self, message):
        self.context.chatHistory.add_user_message(message)

        # TUTORIAL CODE GOES HERE

        return None
