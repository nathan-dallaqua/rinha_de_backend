from pydantic import BaseModel

class LoadBalancer(BaseModel):
    hostname: str
    port: int
