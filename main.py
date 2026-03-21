from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.router_roles import router_roles
from routes.router_perfiles import router_perfiles
from routes.router_usuarios import router_usuarios
from routes.router_reportes import router_reportes
from routes.router_auth import router_auth
from middlewares.cors import add_cors

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Smart Trash Backend", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al backend de Smart Trash"}

add_cors(app)

app.include_router(router_auth)
app.include_router(router_roles)
app.include_router(router_perfiles)
app.include_router(router_usuarios)
app.include_router(router_reportes)