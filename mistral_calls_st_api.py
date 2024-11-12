from dotenv import load_dotenv
import os
from mistralai import Mistral
import httpx
import json
import functools

load_dotenv()

ST_API_KEY = os.getenv("ST_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")



def call_destinations_api(place_type : str):
    url = "https://opendata.myswitzerland.io/v1/destinations?facet.filter=placetypes%3A{}".format(place_type)
    headers = {
        "accept": "application/json",
        "x-api-key": ST_API_KEY
    }
    
    try:
        with httpx.Client() as client:
            response =  client.get(url, headers=headers)
            print(response)
            response.raise_for_status()  # Check if the response contains an HTTP error status
        return response.json()  # Return the response as JSON data
    
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to fetch data from Switzerland API.")
    
names_to_functions = { "call_destinations_api": call_destinations_api }

tools = [
    {
        "type": "function",
        "function": {
            "name": "call_destinations_api",
            "description": "Given a destination type it returns destinations of that type in switzerland",
            "parameters": {
                "type": "object", 
                "properties": {
                    "place_type": {
                        "type": "string", 
                        "description": "The type of activity"
                    }
                }, 
                "required": ["place_type"]
            }
        }
    }
]

messages = [{"role": "user", "content": "Can you show me mountains in switzerland?"}]

model = "mistral-large-latest"

client = Mistral(api_key=MISTRAL_API_KEY)
response = client.chat.complete(
    model = model,
    messages = messages,
    tools = tools,
    tool_choice = "any",
)

tool_call = response.choices[0].message.tool_calls[0]
function_name = tool_call.function.name
function_params = json.loads(tool_call.function.arguments)

print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)

#calls sayHello with the parameters from the user
response_dict = names_to_functions[function_name](**function_params)


data = response_dict["data"]
for mountain in data:
    print(mountain["name"])
    print(mountain["geo"]["latitude"])    
    print(mountain["geo"]["longitude"])    


