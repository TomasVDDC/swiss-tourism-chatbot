import functools
import os
from mistralai import Mistral           
from dotenv import load_dotenv

load_dotenv() #load env variables
api_key = os.getenv("MISTRAL_API_KEY")


def sayHello(name: str):
    print("hello {}".format(name))

tools = [
    {
        "type": "function",
        "function": {
            "name": "sayHello",
            "description": "Given a name prints : hello <name>",
            "parameters": {
                "type": "object", 
                "properties": {
                    "name": {
                        "type": "string", 
                        "description": "The name of the person"
                    }
                }, 
                "required": ["name"]
            }
        }
    }
]

messages = [{"role": "user", "content": "Can you say hello to Tomas?"}]

model = "mistral-large-latest"

client = Mistral(api_key=api_key)
response = client.chat.complete(
    model = model,
    messages = messages,
    tools = tools,
    tool_choice = "any",
)

print(response)
