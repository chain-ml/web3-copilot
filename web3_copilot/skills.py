from council.contexts import Budget, Consumption
from council.contexts import ChainContext, ChatMessage
from council.skills import SkillBase

from chromadb import Client

from web3_copilot.doc_retrieval.config import Config
from web3_copilot.doc_retrieval import Retriever

from web3_copilot.common import constants

import json
import re
import requests

from dotenv import find_dotenv, get_key


class DocRetrievalSkill(SkillBase):
    """Skill to retrieve documents from database and build context"""

    def __init__(self,
                 db_client: Client,
                 collection_name: str,
                 retriever: Retriever):
        super().__init__(name="doc_retrieval")
        self.db_client = db_client
        self.collection_name = collection_name
        self.retriever = retriever

    def execute(self, context: ChainContext) -> ChatMessage:
        collection = self.db_client.get_or_create_collection(name=self.collection_name)
        query = context.chat_history.last_message.message
        doc_context = self.retriever.retrieve_docs(query=query, collection=collection)

        return self.build_success_message(
            f"Results from {self.collection_name} in database retrieved\n{doc_context}",
            data=doc_context
        )


class TransactionDebuggerSkill(SkillBase):
    """Skill to explain details of EVM transactions such as receipts and traces"""

    def __init__(self, config: Config):
        super().__init__(name="txn_debugger")

        self.tokenizer = config._tokenizer
        self.config = self._get_config()
        self.token_limit = constants.CONTEXT_TOKEN_LIMIT - 1000
        self.req_count = 0

    def _get_config(self):
        env_path = find_dotenv()

        web3_config = {
            "rpc_url": get_key(env_path, "ETH_MAINNET_URL"),
            "tenderly_api_key": get_key(env_path, "TENDERLY_API_KEY"),
            "block_explorer_api_key": get_key(env_path, "ETHERSCAN_API_KEY"),
            "etherscan_api": get_key(env_path, "ETHERSCAN_API"),
        }

        return web3_config

    def execute(self, context: ChainContext) -> ChatMessage:
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
        context.budget.add_consumption(1, "call", "API_CALL")

        tx_trace = response.json()["result"]

        addresses = self.extract_recipient_addresses(tx_trace)

        contracts = self.fetch_contracts(addresses, context.budget)

        debug_context = {
            "transaction_trace": tx_trace,
            "contracts_source_code": contracts
        }

        self.req_count += 1

        return self.build_success_message(
            f"{debug_context}",
            data=debug_context
        )

    def fetch_contracts(self, addresses: list[str], budget: Budget):
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
            budget.add_consumption(1, "call", "API_CALL")

            if response.status_code < 400:
                result = response.json()["result"]
                details = []

                # exclude unverified contracts
                for res in result:
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
