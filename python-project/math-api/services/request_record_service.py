from fastapi import Depends
from models.request_record import RequestRecord
from stores.request_record_store import RequestRecordStore

class RequestRecordService:
    def __init__(self, request_record_store: RequestRecordStore):
        self.request_record_store = request_record_store

    async def record_request(self, api_key: str, endpoint: str, request_method: dict, request_input: dict, request_status: str):
        request = RequestRecord(
            api_key=api_key,
            endpoint=endpoint,
            request_method=request_method,
            request_input=request_input,
            request_status=request_status
        )

        await self.request_record_store.save(request)