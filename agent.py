from typing import List
from string import Template
import toml

import dotenv

from council.core import Agent, AgentContext, Budget, ChatHistory, Chain, ChainContext
from council.core.budget import InfiniteBudget
from council.llm import OpenAIConfiguration, OpenAILLM, AzureLLM, AzureConfiguration, LLMMessage
from council.skill import LLMSkill
from council.controller import LLMController
from council.evaluator import BasicEvaluator, LLMEvaluator

import constants
from config import Config
from retrieval import Retriever
from skills import DocRetrievalSkill


dotenv.load_dotenv()

class DocRetrievalAgent:

    def __init__(self):
        # Initialize database dependencies
        self.config = Config(encoding_name=constants.ENCODING_NAME, embedding_model_name=constants.EMBEDDING_MODEL_NAME, cross_encoder_model_name=constants.CROSS_ENCODER_MODEL_NAME)
        self.db_client = self.config.initialize()
        self.retriever = Retriever(self.config)

        # Initialize agent
        self.context = AgentContext(chat_history=ChatHistory()) 
        self.llm = OpenAILLM(config=OpenAIConfiguration.from_env())
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
        self.uni_doc_retrieval_skill = DocRetrievalSkill(db_client=self.db_client, collection_name='uni', retriever=self.retriever)
        self.avax_doc_retrieval_skill = DocRetrievalSkill(db_client=self.db_client, collection_name='avax', retriever=self.retriever)
        self.atom_doc_retrieval_skill = DocRetrievalSkill(db_client=self.db_client, collection_name='atom', retriever=self.retriever)
        self.matic_doc_retrieval_skill = DocRetrievalSkill(db_client=self.db_client, collection_name='matic', retriever=self.retriever)

        # Skill to interact with LLM
        self.llm_skill = LLMSkill(llm=self.llm, system_prompt=self.system_prompt, context_messages=self.build_context_message)

    def init_chains(self) -> List[Chain]:
        self.uni_doc_retrieval_chain = Chain(
            name="uni_doc_retrieval",
            description="Retrieve information from Uniswap's official documentation that contains all information about Uniswap products.",
            runners=[self.uni_doc_retrieval_skill, self.llm_skill]
        )
        self.avax_doc_retrieval_chain = Chain(
            name="avax_doc_retrieval",
            description="Retrieve information from Avalanche's official documentation that contains the contents for the Avalanche Developer Documentation.",
            runners=[self.avax_doc_retrieval_skill, self.llm_skill]
        )
        self.atom_doc_retrieval_chain = Chain(
            name="atom_doc_retrieval",
            description="Retrieve information from Cosmos' official documentation that contains all information about Cosmos and the Cosmos SDK.",
            runners=[self.atom_doc_retrieval_skill, self.llm_skill]
        )
        self.matic_doc_retrieval_chain = Chain(
            name="matic_doc_retrieval",
            description="Retrieve information from Polygon's official documentation that contains all information about the Polygon project.",
            runners=[self.matic_doc_retrieval_skill, self.llm_skill]
        )

        return [
            self.uni_doc_retrieval_chain,
            self.avax_doc_retrieval_chain,
            self.atom_doc_retrieval_chain,
            self.avax_doc_retrieval_chain
        ]

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

"""
usage
"""
agent = DocRetrievalAgent()


def web3_copilot_chat(message):
    response = agent.interact(message)

    print("---begin agent response---")
    print(response.try_best_message.unwrap().message)
    print("---end agent response---")


project_questions = {
    "uni": [
        "What is Uniswap?",
        "What is soft governance in Uniswap?"
    ],
    "avax": [
        "How is Avalanche different from Ethereum?",
        "What is the X-Chain and how is it different from the C-Chain?"
    ],
    "atom": [
        "Why would one use the Cosmos SDK?",
        "How do I setup the keyring for my Cosmos Node?"
    ],
    "matic": [
        "Is polygon a layer 2 blockchain or a layer 1 blockchains?"
        "How do I bridge assets with supernets?"
    ]
}

for project in project_questions:
    print(f"---------------------Sending questions about {project}---------------------")

    for question in project_questions[project]:
        print(question)
        web3_copilot_chat(question)

    print(f"---------------------Done with {project} questions---------------------")

