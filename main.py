import json
import string
from typing import Annotated
from fastapi import FastAPI, HTTPException, Request, Form
import aiofiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import random
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/")
async def root(request: Request, long_url:Annotated[str, Form()]):
    short_url = "".join(
        [random.choice(string.ascii_letters+string.digits) for _ in range(5)]
        )
    async with aiofiles.open ("urls.json", "r") as f:
        existing_data = json.loads(await f.read())
    async with aiofiles.open("urls.json" , 'w') as f:
        existing_data[short_url] = long_url
        await f.write(json.dumps(existing_data))
    return {"message": f"Shortened URL is {short_url}"}


@app.get("/{short_url}")
async def convert_url(short_url: str):
    async with aiofiles.open ("urls.json", "r") as f:
        redirect_url = json.loads(await f.read()).get(short_url)
    if redirect_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    else:
        return RedirectResponse(redirect_url)   
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)