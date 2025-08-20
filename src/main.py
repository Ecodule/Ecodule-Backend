from fastapi import FastAPI

from api.routers import user

app = FastAPI()
app.include_router(user.router)

@app.get("/")
def read_root():
    return {"message": "Hello, Docker World!"}