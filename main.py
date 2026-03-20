from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import router

app = FastAPI()

app.include_router(router)

@app.get("/")
def home():
    return {"message": "App is working"}

app.mount("/ui", StaticFiles(html=True), name="static")