import functools
import os
import json
from mistralai import Mistral           
from dotenv import load_dotenv

load_dotenv() #load env variables
api_key = os.getenv("MISTRAL_API_KEY")


def sayHello(name: str):
    print("hello {}".format(name))

names_to_functions = { "sayHello":sayHello }
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

tool_call = response.choices[0].message.tool_calls[0]
function_name = tool_call.function.name
function_params = json.loads(tool_call.function.arguments)

print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)

#calls sayHello with the parameters from the user
names_to_functions[function_name](**function_params)
