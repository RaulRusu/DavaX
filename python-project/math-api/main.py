import os
from fastapi import FastAPI

from middelwares.request_record_middleware import request_record_middleware
from routes import test_routes
from routes import math_routes
from routes import health_routes

from contextlib import asynccontextmanager
from dotenv import load_dotenv

import di_setup
from infrastructure.log_utils.setup_logging import setup_logging, clear_logging

print("loading env", flush=True)
if os.environ.get("RUN_ENV") == "docker":
    load_dotenv(".env.docker")
else:
    load_dotenv(".env")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register dependencies for DI container
    await di_setup.register_dependencies()
    await setup_logging()
    yield
    await clear_logging()
    await di_setup.clear_dependencies()

app = FastAPI(lifespan=lifespan)

app.middleware("http")(request_record_middleware)
app.include_router(test_routes.router) 
app.include_router(math_routes.router, prefix="/math", tags=["math"])
app.include_router(health_routes.router, prefix="/health", tags=["health"])