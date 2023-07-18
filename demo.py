from agent import DocRetrievalAgent

"""
example usage
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
        "Is Polygon a layer 2 blockchain or a layer 1 blockchains?",
        "How do I bridge assets with supernets?"
    ]
}

for project in project_questions:
    print(f"------------------Sending questions about {project}------------------")

    for question in project_questions[project]:
        print(question)
        web3_copilot_chat(question)

    print(f"------------------Done with {project} questions------------------")

