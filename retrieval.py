from typing import Any, Dict, List

from chromadb.api.models.Collection import Collection


import constants
from config import Config


class Retriever:
    def __init__(self, config: Config):
        self.embedding_encoder = config._embedding_encoder
        self.cross_encoder = config._cross_encoder_model
        self.tokenizer = config._tokenizer

    def retrieve_docs(self, query: str, collection: Collection) -> Dict[str, Any]:
        """Function to retrieve ranked results from database"""
        results = self._query_db(
            query=query, k=constants.NUM_RETRIEVED_DOCUMENTS, collection=collection
        )
        ranked_results = self._rank_results(
            query=query,
            db_results=results,
            num_results=constants.NUM_TOP_RANKED_DOCUMENTS,
        )
        documents = ranked_results["documents"][0]
        context = self._build_context(documents)

        return context

    def _query_db(self, query: str, k: int, collection: Collection) -> Dict[str, Any]:
        """Function to retrieve top K documents
        from the database based on similarity to the query."""
        # Calculate the embedding for the query
        embedded_query = self.embedding_encoder.encode(
            query, convert_to_tensor=False
        ).tolist()
        # Retrieve documenents from the database
        output = collection.query(query_embeddings=[embedded_query], n_results=k)

        return output

    def _rank_results(
        self, query: str, db_results: Dict[str, Any], num_results: int
    ) -> Dict[str, Any]:
        """Function to rank the documents retrieved from
         the database based on their relevance to
        the query using a cross-encoder and returning the top ranked documents."""

        ranked_results = {}

        # Calculate top-ranked documents
        documents = db_results["documents"][0]
        sentence_pairs = [[query, doc] for doc in documents]
        rankings = self.cross_encoder.predict(sentence_pairs)
        top_ranked_idx = rankings.argsort()[-num_results:][::-1]

        # Filter database results for rankings
        ranked_results["ids"] = [[db_results["ids"][0][i] for i in top_ranked_idx]]
        ranked_results["documents"] = [
            [db_results["documents"][0][i] for i in top_ranked_idx]
        ]
        ranked_results["metadatas"] = [
            [db_results["metadatas"][0][i] for i in top_ranked_idx]
        ]
        ranked_results["distances"] = [
            [db_results["distances"][0][i] for i in top_ranked_idx]
        ]

        return ranked_results
    
    def _build_context(self, documents: List[str]) -> str:
        """Function to convert the database results into a context for the prompt."""
        context = ""
        num_tokens = 0
        for doc in documents:
            doc += "\n\n"
            num_tokens += len(self.tokenizer.encode(doc))
            if num_tokens <= constants.CONTEXT_TOKEN_LIMIT:
                context += doc
            else:
                break

        return context
