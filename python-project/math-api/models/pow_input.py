from pydantic import BaseModel

class PowInput(BaseModel):
    base: float
    exponent: float