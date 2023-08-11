import logging
from typing import Union
import os

import chromadb
import tiktoken
from chromadb import PersistentClient, Settings
from sentence_transformers import CrossEncoder, SentenceTransformer
from tiktoken import Encoding

from web3_copilot.common import constants
from web3_copilot.common.utils import create_file_dict
from web3_copilot.doc_retrieval import Encoder
from web3_copilot.doc_retrieval import PdfExtractor


class Config:
    _embedding_encoder: Union[None, SentenceTransformer] = None
    _cross_encoder_model: Union[None, CrossEncoder] = None
    _tokenizer: Union[None, Encoding] = None

    def __init__(
        self,
        encoding_name: str,
        embedding_model_name: str,
        cross_encoder_model_name: str,
    ):
        self.encoding_name = encoding_name
        self.embedding_model_name = embedding_model_name
        self.cross_encoder_model_name = cross_encoder_model_name

    def initialize(self) -> PersistentClient():
        # Initialize retrieval and ranking models
        self._embedding_encoder = SentenceTransformer(self.embedding_model_name)
        self._cross_encoder_model = CrossEncoder(self.cross_encoder_model_name)

        # Initialize tokenizer
        self._tokenizer = tiktoken.get_encoding(self.encoding_name)

        # Initialize pdf text extractor
        self._pdf_extractor = PdfExtractor(
            self.embedding_model_name, max_chunk_size=constants.MAX_CHUNK_SIZE
        )

        # Initialize encoder
        self._encoder = Encoder(self._embedding_encoder)

        # Initialize database
        return self._init_database()

    def _init_database(self) -> PersistentClient():
        logging.info('message="initialize database started"')
        client = chromadb.PersistentClient(
            path=constants.DB_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )

        # Return data subdirectories to determine database indices to create
        file_dict = create_file_dict(constants.DATA_DIR)
        for index, files in file_dict.items():
            collection = client.get_or_create_collection(
                name=index, metadata={"hnsw:space": "cosine"}
            )
            # If the collection is empty, populate the database
            if collection.count() == 0:
                print(f"{index} has no collection, creating...")
                # Store text chunks for a directory
                data = []
                # Extract text from files
                for file in files:
                    chunks = self._pdf_extractor.extract_and_chunk(
                        os.path.join(constants.DATA_DIR, index, file)
                    )
                    data.extend(chunks)
                # Create document embeddings
                self._encoder.encodeInCollection(data, collection)
                print(f"created {index} collection")

        logging.info('message="database initialization completed"')
        return client



    @property
    def embedding_encoder(self):
        return self._embedding_encoder

    @property
    def cross_encoder_model(self):
        return self._cross_encoder_model

    @property
    def tokenizer(self):
        return self._tokenizer
