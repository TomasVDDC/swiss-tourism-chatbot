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
            "description": "Given a destination type it returns destinations of that type in switzerland. Make the name plurial",
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

def extract_place_data(response_dict):
    data = response_dict["data"]
    place_data = []

    for place_type in data:
        place_info = {
            "name": place_type["name"],
            "latitude": place_type["geo"]["latitude"],
            "longitude": place_type["geo"]["longitude"]
        }
        place_data.append(place_info)

    return place_data

def destination_function_calling(messages):

    model = "mistral-large-latest"

    client = Mistral(api_key=MISTRAL_API_KEY)
    response = client.chat.complete(
        model = model,
        messages = messages,
        tools = tools,
        tool_choice = "any",
    )
    messages.append(response.choices[0].message)
    
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_params = json.loads(tool_call.function.arguments)

    print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)

    response_dict = names_to_functions[function_name](**function_params)

    data = response_dict["data"]
    print("*")
    for place_type in data:

        print(place_type["name"])
        print(place_type["geo"]["latitude"])    
        print(place_type["geo"]["longitude"])
        
    place_data = extract_place_data(response_dict)
    place_data_string = json.dumps(place_data)
    messages.append({"role":"tool", "name":function_name, "content":place_data_string, "tool_call_id":tool_call.id})
    
    return messages, place_data

# place_data = destination_function_calling("I have heard there are quite a few nice mountains in switzerland")
# print(place_data)
