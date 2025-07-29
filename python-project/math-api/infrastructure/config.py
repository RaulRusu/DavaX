from pydantic_settings import BaseSettings
from pydantic import Field

class ServiceConfig(BaseSettings):
    svc_name: str = Field(..., env="SVC_NAME")
    svc_host: str = Field(..., env="SVC_HOST")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"