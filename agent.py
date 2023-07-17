from typing import List
from string import Template
import toml

import dotenv

from council.agents import Agent
from council.chains import Chain
from council.contexts import AgentContext, ChainContext, ChatHistory
from council.runners.budget import InfiniteBudget
from council.llm import OpenAILLMConfiguration, OpenAILLM, AzureLLM, AzureLLMConfiguration, LLMMessage
from council.skills import LLMSkill
from council.controllers import LLMController
from council.evaluators import BasicEvaluator, LLMEvaluator

import constants
from config import Config
from retrieval import Retriever
from skills import DocRetrievalSkill
from utils import create_file_dict


dotenv.load_dotenv()

class DocRetrievalAgent:

    def __init__(self):
        # Initialize database dependencies
        self.config = Config(encoding_name=constants.ENCODING_NAME, embedding_model_name=constants.EMBEDDING_MODEL_NAME, cross_encoder_model_name=constants.CROSS_ENCODER_MODEL_NAME)
        self.db_client = self.config.initialize()
        self.retriever = Retriever(self.config)

        # Initialize agent
        self.context = AgentContext(chat_history=ChatHistory()) 
        self.llm = OpenAILLM(config=OpenAILLMConfiguration.from_env())
        # self.llm = AzureLLM(config=AzureConfiguration.from_env())
        self.load_prompts()
        self.init_skills()
        chains = self.init_chains()
        self.controller = LLMController(llm=self.llm, top_k_execution_plan=1)
        # self.evaluator = BasicEvaluator()
        self.evaluator = LLMEvaluator(self.llm)
        self.agent = Agent(self.controller, chains, self.evaluator)

    def load_prompts(self):
        self.system_prompt = toml.load("./templates/doc_retrieval_prompt.toml")['system_message']['prompt']
        self.prompt_template = Template(toml.load("./templates/doc_retrieval_prompt.toml")['main_prompt']['prompt'])

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

        # Skill to interact with LLM
        self.llm_skill = LLMSkill(
            llm=self.llm,
            system_prompt=self.system_prompt,
            context_messages=self.build_context_message
        )

    def init_chains(self) -> List[Chain]:
        chains = []

        for index, doc_retrieval_skill in self.doc_retrieval_skills.items():
            chains.append(
                Chain(
                    name=f"{index}_doc_retrieval",
                    description=toml.load(
                        "./templates/document_descriptions.toml"
                    )[index]["description"].format(index=index),
                    runners=[doc_retrieval_skill, self.llm_skill],
                )
            )
        return chains

    def build_context_message(self, context: ChainContext) -> List[LLMMessage]:
        doc_context = context.current.last_message().unwrap().data
        query = context.chatHistory.last_user_message().unwrap().message     

        prompt = self.prompt_template.substitute(context=doc_context, query=query)

        return [LLMMessage.user_message(prompt)]

    def interact(self, message):
        self.context.chatHistory.add_user_message(message)
        # result = self.agent.execute(context=self.context, budget=Budget(60))
        result = self.agent.execute(context=self.context, budget=InfiniteBudget())
        return result
