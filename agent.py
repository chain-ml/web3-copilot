from typing import List
from pathlib import Path

import toml
import dotenv

from council.agents import Agent
from council.chains import Chain
from council.contexts import AgentContext, ChainContext, ChatHistory
from council.runners.budget import Budget, Consumption
from council.llm import OpenAILLMConfiguration, OpenAILLM, LLMMessage
from council.skills import LLMSkill, PromptToMessages
from council.prompt import PromptBuilder
from council.controllers import LLMController
from council.evaluators import LLMEvaluator

import constants
import logging

from config import Config
from retrieval import Retriever
from skills import DocRetrievalSkill, Web3DebuggerSkill
from utils import create_file_dict

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
        self.llm = OpenAILLM(config=OpenAILLMConfiguration.from_env())
        self.init_skills()
        chains = self.init_chains()
        self.controller = LLMController(llm=self.llm, top_k_execution_plan=1)
        self.evaluator = LLMEvaluator(self.llm)
        self.agent = Agent(self.controller, chains, self.evaluator)

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


        # Skills for web3 debugger
        self.web3_debugger_skill = Web3DebuggerSkill(
            config=self.config
        )

        # Skill to interact with LLM web3 debugger
        self.w3d_llm_skill = LLMSkill(
            llm=self.llm,
            system_prompt=self.load_system_prompt("web3_debugger"),
            context_messages=self.build_context_message
        )

    def init_chains(self) -> List[Chain]:
        chains = []

        for index, doc_retrieval_skill in self.doc_retrieval_skills.items():
            chains.append(
                Chain(
                    name=f"{index}_doc_retrieval",
                    description=toml.load(
                        "./templates/doc_retrieval/document_descriptions.toml"
                    )[index]["description"].format(index=index),
                    runners=[doc_retrieval_skill, self.dr_llm_skill],
                )
            )

        web3_debugger_desc = "Provide more details about transactions such as why they failed or succeeded."
        chains.append(
            Chain(
                name="web3_debugger_chain",
                description=web3_debugger_desc,
                runners=[self.web3_debugger_skill, self.w3d_llm_skill],
            )
        )

        return chains

    def load_system_prompt(self, skill: str):
        system_prompt_file = ""

        if skill == "web3_debugger":
            system_prompt_file = f"./templates/{skill}/system_prompt.jinja"
        else:
            system_prompt_file = f"./templates/{skill}/system_prompt.jinja"

        system_prompt = Path(system_prompt_file).read_text()
        return system_prompt

    def build_context_message(self, context: ChainContext) -> List[LLMMessage]:
        context_message_template = Path(
            "./templates/context_message_prompt.jinja"
        ).read_text()

        context_message_prompt = PromptToMessages(
            prompt_builder=PromptBuilder(context_message_template)
        )

        messages = context_message_prompt.to_user_message(context)
        return messages

    def interact(self, message):
        self.context.chatHistory.add_user_message(message)

        result = self.agent.execute(context=self.context, budget=Budget(
            60,
            limits=[
                Consumption(1, "call", "Web3DebuggerSkill"),
                Consumption(1, "token", "gpt-4-0613")
            ]
        ))
        return result
