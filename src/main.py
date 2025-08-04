from fastapi import FastAPI

from api.routers import app_data

app = FastAPI()
app.include_router(app_data.router)

@app.get("/")
def read_root():
    return {"message": "Hello, Docker World!"}