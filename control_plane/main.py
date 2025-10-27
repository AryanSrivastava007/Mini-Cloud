from fastapi import FastAPI
from db import init_db
from routes import health, instances, agents, files

app = FastAPI(title="MiniCloud Control Plane")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(health.router)
app.include_router(instances.router)
app.include_router(agents.router)
app.include_router(files.router)
