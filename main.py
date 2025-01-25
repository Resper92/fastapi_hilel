import json
import string
from typing import Annotated
from fastapi import FastAPI, HTTPException, Request, Form
import aiofiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import random
import uvicorn
import motor.motor_asyncio

db_client = motor.motor_asyncio.AsyncIOMotorClient("localhost", 27017, username="root", password="example")
app_db = db_client["shortener"]
colection = app_db["urls"]

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
    await colection.insert_one({"short_url": short_url, "long_url": long_url})
    return {"message": f"Shortened URL is {short_url}"}


@app.get("/{short_url}")
async def convert_url(short_url: str):
    colection_data = await colection.find_one({"short_url": short_url})
    redirect_url = colection_data.get("long_url") if colection_data else None
    colection_data = await colection.update_one({"short_url": short_url}, {"$inc": {"count": 1}})
    if redirect_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    else:
        return RedirectResponse(redirect_url)   
    
@app.get("/{short_url}/stats")
async def stats(request: Request, short_url: str ):
    colection_data = await colection.find_one({"short_url": short_url})
    if colection_data is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return templates.TemplateResponse(request=request, name="stats.html", context={"url_data": colection_data})

@app.post("/{short_url}/stats")
async def edit_stats(request: Request,short_url: str, long_url: Annotated[str, Form()]):
    await colection.update_one({"short_url": short_url}, {"$set": {"long_url": long_url}})
    colection_data = await colection.find_one({"short_url": short_url})
    return templates.TemplateResponse(request=request, name="stats.html", context={"url_data": colection_data})
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)