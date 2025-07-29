from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from security.api_key import get_api_key
from services.health_service import HealthService
from services import service_provider

router = APIRouter()

@router.get("")
async def health_check(
        health_service: HealthService = Depends(service_provider.get_health_service)):
    
    # Check if the service is healthy
    health_status = await health_service.check_health()
    return JSONResponse(content=health_status, status_code=200)
    