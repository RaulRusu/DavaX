from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse

from models.pow_input import PowInput
from security.api_key import get_api_key
from services.request_record_service import RequestRecordService
from services.math_service import MathService
from services import service_provider

router = APIRouter(
    dependencies=[Depends(get_api_key)],
)

@router.post("/pow")
async def pow_handler(
        pow_input: PowInput,
        math_service: MathService = Depends(service_provider.get_math_service)):
    result = math_service.pow(pow_input.base, pow_input.exponent)
    return JSONResponse(
        content={
            "base": pow_input.base,
            "exponent": pow_input.exponent,
            "result": result
        })

@router.get("/fibo/{n}")
async def fibo_handler(
        n: int,
        math_service: MathService = Depends(service_provider.get_math_service)):
    result = math_service.nth_fibo_number(n)

    return JSONResponse(
        content={
            "n": n,
            "result": result
        })

@router.get("/factorial/{number}")
async def factorial_handler(
        number: int,
        math_service: MathService = Depends(service_provider.get_math_service)):
    result = math_service.factorial(number)
    return JSONResponse(
        content={
            "number": number,
            "result": result
        })
