from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from api.routes import chat_response, test_routes
from application.rag.pipeline import RAGPipeline
from infrastructure.di.decorators import bind
from infrastructure.vectorstore.indexer_worker import run_sync

from fastapi.middleware.cors import CORSMiddleware

load_dotenv(".env")

@bind(singleton=True)
def get_rag_pipeline() -> RAGPipeline:
    rag_pipeline = RAGPipeline()
    rag_pipeline.init_blocking()
    return rag_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_sync()
    #client = AsyncOpenAI()
    #await init_db()
    yield
    #await client.close()
    
app = FastAPI(lifespan=lifespan)
app.include_router(test_routes.router)
# app.include_router(crud.router, prefix="/api")
app.include_router(chat_response.router, prefix="/api")
#app.include_router(chat_api.router, prefix="/api")

origins = [
    "http://localhost:5173",  # React dev server
    "http://localhost:3000",  # (if you ever use CRA)
    # Add production URLs as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or ["*"] for all (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],  # Or specify ["GET", "POST", ...]
    allow_headers=["*"],
)