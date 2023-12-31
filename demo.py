from web3_copilot.agent import Web3CopilotAgent

agent = Web3CopilotAgent()


def web3_copilot_chat(message):
    response = agent.interact(message)

    print("---begin agent response---")
    print(response.try_best_message.unwrap_or("no agent message").message)
    print("---end agent response---")


def demo_doc_retrieval():
    print("------------------BEGIN: Doc Retrieval Skill Demo------------------")

    project_questions = {
        "uniswap": [
            "What is Uniswap?",
            "What is soft governance in Uniswap?"
        ],
        "avalanche": [
            "How is Avalanche different from Ethereum?",
            "What is the X-Chain and how is it different from the C-Chain?"
        ],
        "cosmos": [
            "Why would one use the Cosmos SDK?",
            "How do I setup the keyring for my Cosmos Node?"
        ],
        "polygon": [
            "Is Polygon a layer 2 blockchain or a layer 1 blockchains?",
            "What are Polygon supernets?"
        ]
    }

    for project in project_questions:
        print(f"------------------Sending questions about {project}------------------")

        for question in project_questions[project]:
            print(f"PROMPT: {question}\n")
            web3_copilot_chat(question)

        print(f"------------------Done with {project} questions------------------\n")

    print("------------------END: Doc Retrieval Skill Demo------------------\n")


def demo_txn_debugger():
    print("------------------BEGIN: Transaction Debugger Skill Demo------------------")

    prompts = [
        "Why did my txn fail - 0xf6870204a21b88e47e5bc788852905669c61419d676a9a18bfa5a96e9928f70c?",
        "What's happening in this tx - 0xf6870204a21b88e47e5bc788852905669c61419d676a9a18bfa5a96e9928f70c?"
    ]

    for prompt in prompts:
        print(f"PROMPT: {prompt}\n")
        web3_copilot_chat(prompt)

    print("------------------END: Transaction Debugger Skill Demo------------------\n")


demo_doc_retrieval()
demo_txn_debugger()

# print(f"\n{agent.render()}")
