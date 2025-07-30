import asyncio
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer
from contextlib import asynccontextmanager
from di_setup import register_dependencies
from shared_core.di.container import container
from shared_core.kafka.consumer.consumer import KafkaConsumer 
import os
from dotenv import load_dotenv

if os.environ.get("RUN_ENV") == "docker":
    load_dotenv(".env.docker")
else:
    load_dotenv(".env")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield
    await on_shutdown()

app = FastAPI(lifespan=lifespan)

# Store background task/future for clean shutdown on app.state
app.state.consumer_task = None

@app.get("/health")
async def health():
    return {"status": "UP"}

async def start_kafka_consumer():
    consumer = await container.resolve(KafkaConsumer)
    await consumer.start(max_retries = 10)
    await consumer.run()

async def on_startup():
    await register_dependencies()
    app.state.consumer_task = asyncio.create_task(start_kafka_consumer())
    

async def on_shutdown():
    if app.state.consumer_task:
        app.state.consumer_task.cancel()
        try:
            await app.state.consumer_task
        except asyncio.CancelledError:
            pass