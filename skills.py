from council.runners import Budget
from council.contexts import ChainContext, ChatMessage
from council.skills import SkillBase

from chromadb import Client

from config import Config
from retrieval import Retriever

import constants

import json
import re
import requests


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

    def execute(self, context: ChainContext, budget: Budget) -> ChatMessage:
        collection = self.db_client.get_or_create_collection(name=self.collection_name)
        query = context.chatHistory.messages[-1].message
        doc_context = self.retriever.retrieve_docs(query=query, collection=collection)

        return self.build_success_message(
            f"Results from {self.collection_name} in database retrieved\n{doc_context}",
            data=doc_context
        )


class Web3DebuggerSkill(SkillBase):
    """Skill to get details of EVM transactions such as receipts and traces"""

    def __init__(self, config: Config):
        super().__init__(name="web3_debugger")

        self.tokenizer = config._tokenizer
        self.config = config.get_web3_config()
        self.token_limit = constants.CONTEXT_TOKEN_LIMIT - 1000
        self.req_count = 0

    def execute(self, context: ChainContext, budget: Budget) -> ChatMessage:
        query = context.chat_history.last_message.message
        tx_hash = self.extract_tx_hash(query)

        url = self.config.get("rpc_url")
        headers = {
            "Content-Type": "application/json",
            "X-access-Key": self.config.get("tenderly_api_key")
        }
        data = json.dumps({
            "method": "tenderly_traceTransaction",
            "params": [tx_hash],
            "id": self.req_count,
            "jsonrpc": "2.0"
        })

        response = requests.post(url, headers=headers, data=data)

        tx_trace = response.json()["result"]

        # addresses = self.extract_all_addresses(json.dumps(tx_trace))
        addresses = self.extract_recipient_addresses(tx_trace)

        contracts = self.fetch_contracts(addresses)

        debug_context = {
            "transaction_trace": tx_trace,
            "contracts_source_code": contracts
        }
        # debug_context = json.dumps(tx_trace)

        self.req_count += 1

        return self.build_success_message(
            f"{debug_context}",
            data=debug_context
        )

    def fetch_contracts(self, addresses: list[str]):
        api_url = self.config.get("etherscan_api")
        api_key = self.config.get("block_explorer_api_key")

        contracts = {}
        seen = {}
        num_tokens = 0

        for address in addresses:
            url = (f"{api_url}"
                   f"?module=contract"
                   f"&action=getsourcecode"
                   f"&address={address}"
                   f"&apikey={api_key}")
            response = requests.get(url)

            if response.status_code < 400:
                result = response.json()["result"]
                details = []

                for res in result: # exclude unverified contracts
                    if res["ContractName"] not in seen and len(res["SourceCode"]) > 0:
                        num_tokens += len(self.tokenizer.encode(res["SourceCode"]))
                        if num_tokens <= self.token_limit:
                            details.append(res["SourceCode"])
                            seen["ContractName"] = True
                        else:
                            break

                contracts[address] = details

        return contracts

    def extract_recipient_addresses(self, trace) -> list[str]:
        addresses = []
        trace_steps = trace["trace"]
        seen = {}

        for step in trace_steps:
            to = step["to"]
            if to not in seen and "decodedInput" not in step:
                addresses.append(to)
                seen[to] = True

        return addresses

    def extract_all_addresses(self, query: str) -> list[str]:
        raw_pattern = r"0x[a-fA-F0-9]{40}"
        matches = re.findall(raw_pattern, query)

        addresses = filter(
            lambda addr: addr != "0x0000000000000000000000000000000000000000",
            matches
        )

        return addresses

    def extract_tx_hash(self, query: str) -> str:
        raw_pattern = r"0x[a-fA-F0-9]{64}"
        match = re.search(raw_pattern, query)

        pos = match.regs[0]
        tx_hash = query[pos[0]:pos[1]]

        return tx_hash
