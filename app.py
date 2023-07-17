from agent import DocRetrievalAgent
from council.agents import AgentResult
from flask import Flask, request

import json

app = Flask(__name__)

# TODO: better to have one instance or one per request?
agent = DocRetrievalAgent()


@app.route("/")
def index():
    return "Welcome to Web3 Copilot! Powered by Council AI from ChainML."


"""
Sample Request - 
{
    "prompt": "Why would one use the Cosmos SDK?"
}

Sample Response - 
{
    "best_message": {
        "data": null,
        "kind": "AGENT",
        "message": "One would use the Cosmos SDK because ..."
    },
    "messages": [
        {
            "message": {
                "data": null,
                "kind": "AGENT",
                "message": "One would use the Cosmos SDK because ..."
            },
            "score": 10
        }
    ]
}
"""
@app.route("/chat", methods=["POST"])
def chat():
    req_data = request.get_json()

    prompt = req_data["prompt"]
    print(prompt)

    agent_response = agent.interact(prompt)
    response = serialize_agent_response(agent_response)

    return response


def serialize_agent_response(agent_response: AgentResult):
    response = {
        "messages": [],
        "best_message": {}
    }

    for scored_msg in agent_response.messages:
        score = scored_msg.score
        message = to_json(scored_msg.message)

        response["messages"].append({
            "score": score,
            "message": message
        })

    best_message = agent_response.try_best_message.unwrap()
    response["best_message"] = to_json(best_message)

    return response


def to_json(obj):
    serialized = json.dumps(obj, default=lambda o: o.__dict__,
                      sort_keys=True, indent=4)

    return json.loads(serialized)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
