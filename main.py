from typing import Union

from fastapi import FastAPI, Request
import httpx
from dotenv import load_dotenv
import os
from mistralai import Mistral
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

load_dotenv()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

ST_API_KEY = os.getenv("ST_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

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
    model = "mistral-large-latest"

    client = Mistral(api_key=MISTRAL_API_KEY)

    chat_response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
    )
    chat_message = chat_response.choices[0].message.content
    
    return templates.TemplateResponse(
        request=request, name="chat_response.html", context={"user_prompt": user_prompt, "chat_message": chat_message}
    )

@app.get("/", response_class=FileResponse)
async def serve_html():
    file_path = os.path.join(os.getcwd(), "./templates/index.html")  # Path to your HTML file
    return FileResponse(file_path)

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

