from fastapi import FastAPI
from routes import users, ejemplo

app = FastAPI()

app.include_router(users.router)
app.include_router(ejemplo.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}