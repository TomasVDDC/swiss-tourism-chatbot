from typing import Union
from fastapi import FastAPI, Request
import httpx
from dotenv import load_dotenv
import os
from mistralai import Mistral
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from mistral_calls_st_api import destination_function_calling
load_dotenv()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

ST_API_KEY = os.getenv("ST_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Shared state object
class SharedState:
    def __init__(self):
        self.places = None

shared_state = SharedState()


@app.get("/destinations/")
async def get_destinations():
    url = "https://opendata.myswitzerland.io/v1/destinations?expand=false"
    headers = {
        "accept": "application/json",
        "x-api-key": ST_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Check if the response contains an HTTP error status
        return response.json()  # Return the response as JSON data
    
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to fetch data from Switzerland API.")

@app.get("/chatprompt/", response_class=HTMLResponse)
async def get_completion(request: Request ,user_prompt: str):
    messages = [{"role": "user", "content": user_prompt}]
    messages, place_data = destination_function_calling(messages)
    shared_state.places = place_data
    
    model = "mistral-large-latest"
    client = Mistral(api_key=MISTRAL_API_KEY)


    response = client.chat.complete(
        model = model, 
        messages = messages
    )
    
    chat_message = response.choices[0].message.content
    
    server_response = templates.TemplateResponse(
        request=request, name="chat_response.html", context={"user_prompt": user_prompt, "chat_message": chat_message}
    )
    server_response.headers["HX-Trigger"] = "map"
    return server_response


@app.get("/", response_class=FileResponse)
async def serve_html():
    file_path = os.path.join(os.getcwd(), "./templates/index.html")  # Path to your HTML file
    return FileResponse(file_path)


@app.get("/get_places/")
async def get_places():
    print("places", shared_state.places)
    return JSONResponse(content = shared_state.places)

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

