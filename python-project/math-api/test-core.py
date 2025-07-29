import asyncio
from dotenv import load_dotenv
from shared_core.db.oracle_db_client import OracleDBClient
from shared_core.di.container import container
from di_setup import register_dependencies

def load_test_env():
    load_dotenv(".env")

async def test_db_connection():
    load_test_env()
    register_dependencies()
    pool = await container.resolve(OracleDBClient)
    assert pool is not None, "Database connection pool should not be None"
    assert hasattr(pool, 'ping'), "Database connection pool should have a ping method"
    assert await pool.ping(), "Database ping should succeed"
    print("Database connection test passed.")


asyncio.run(test_db_connection())