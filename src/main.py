from fastapi import FastAPI

from api.routers import user, statistics

app = FastAPI()
app.include_router(user.router)
app.include_router(statistics.router)

@app.get("/")
def read_root():
    return {"message": "Hello, Docker World!"}