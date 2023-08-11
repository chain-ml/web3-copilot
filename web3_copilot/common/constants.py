DATA_DIR = "./web3_copilot/doc_retrieval/data/generated_pdfs"
DB_PERSIST_DIR = "./web3_copilot/doc_retrieval/data/database/chromadb/"
SOURCE_DOCS = "./web3_copilot/doc_retrieval/data/source_docs"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
ENCODING_NAME = "cl100k_base"

CONTEXT_TOKEN_LIMIT = 8000
NUM_RETRIEVED_DOCUMENTS = 50
NUM_TOP_RANKED_DOCUMENTS = 10
MAX_CHUNK_SIZE = 256

PROJECT_REPOS = {
    "uniswap": "https://github.com/Uniswap/docs.git",
    "avalanche": "https://github.com/ava-labs/avalanche-docs.git",
    "cosmos": "https://github.com/cosmos/cosmos-sdk.git",
    "polygon": "https://github.com/0xPolygon/wiki.git"
}
