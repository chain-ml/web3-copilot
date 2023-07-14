from council.core.budget import Budget
from council.core.execution_context import ChainContext, SkillMessage
from council.core.skill_base import SkillBase

from chromadb import Client

from retrieval import Retriever


class DocRetrievalSkill(SkillBase):
    """Skill to retrieve documents from database and build context"""
    def __init__(self,
                 db_client: Client,
                 collection_name: str,
                 retriever: Retriever):
        super().__init__(name="document_retrieval") 
        self.db_client = db_client
        self.collection_name = collection_name
        self.retriever = retriever

    def execute(self, context: ChainContext, budget: Budget) -> SkillMessage:

        collection = self.db_client.get_or_create_collection(name=self.collection_name)
        query = context.chatHistory.messages[-1].message
        context = self.retriever.retrieve_docs(query=query, collection=collection)

        return self.build_success_message(
            f"Results from {self.collection_name} in database retrieved",
            data=context
        )
    