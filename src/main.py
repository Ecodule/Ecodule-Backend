from fastapi import FastAPI

from api.routers import auth, user
from api.routers.secure import statistics
from api.routers.secure import user as secure_user

app = FastAPI()
app.include_router(user.router)
app.include_router(secure_user.router)
app.include_router(auth.router)
app.include_router(statistics.router)

@app.get("/")
def read_root():
    return {"message": "Hello, Docker World!"}