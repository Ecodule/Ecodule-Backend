from fastapi import FastAPI

from api.routers import auth, user, statistics

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(statistics.router)

@app.get("/")
def read_root():
    return {"message": "Hello, Docker World!"}