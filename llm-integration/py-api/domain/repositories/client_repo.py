from typing import Optional
from datetime import datetime, timezone

from domain.repositories.interfaces import IClientRepository
from domain.entities.client.client import Client

class InMemoryClientRepository(IClientRepository):
    def __init__(self):
        self.clients = {}

    async def create_client(self, client_id: str) -> Client:
        client = Client(id=client_id, created_at=datetime.now(timezone.utc))
        self.clients[client_id] = client
        return client

    async def get_client(self, client_id: str) -> Optional[Client]:
        return self.clients.get(client_id)
