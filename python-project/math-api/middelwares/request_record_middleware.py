from fastapi import Request
from services import service_provider

EXCLUDED_PATHS = ["/docs", "/openapi.json", "/health"] 

async def request_record_middleware(request: Request, call_next):
    api_key = request.headers.get("x-api-key") or None
    method = request.method
    url = request.url.path
    request_body = await request.json() if request.method in ["POST", "PUT", "PATCH"] else {}
    response = await call_next(request)

    if url in EXCLUDED_PATHS:
        return response

    record_service = await service_provider.get_request_record_service()
    await record_service.record_request(
        api_key=api_key,
        endpoint=url,
        request_method=method,
        request_input=request_body,
        request_status="success" if response.status_code == 200 else "error"
    )
    
    return response
