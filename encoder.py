import logging
from typing import Any, Dict, List

from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer


class Encoder:
    def __init__(self, embedding_model: SentenceTransformer):
        self.embedding_model = embedding_model

    def encodeInCollection(
        self, data: List[Dict[str, Any]], collection: Collection, batch_size: int = 128
    ):
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            self._process_batch(batch, collection, (i // batch_size) + 1)

    def _process_batch(self, batch, collection, i):
        ids, texts, metadatas = [], [], []
        for doc in batch:
            doc_id, text, metadata = doc["id"], doc["text"], doc["metadata"]

            # Append to lists
            ids.append(doc_id)
            metadatas.append(metadata)
            texts.append(text)

        # Generate embeddings for the entire batch
        logging.info(f'message="encode batch {i}"')
        embeddings = self.embedding_model.encode(
            texts, convert_to_tensor=False
        ).tolist()

        # Store the batch to the database
        logging.info(f'message="add to collection batch {i}"')
        collection.add(
            documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids
        )
