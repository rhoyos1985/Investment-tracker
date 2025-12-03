from pydantic import BaseModel
from typing import Optional

class MonitoringSystem(BaseModel):
    memory_usage: float
    cpu_usage: float
    disk_usage: float

class ServicesDTO(BaseModel):
    database: Optional[str] = None
    redis: Optional[str] = None

class HealthDTO(BaseModel):
    app_name: str
    version: str
    environment: str
    status: str
    timestamp: str
    services: Optional[ServicesDTO] = None
    system_monitoring: Optional[MonitoringSystem] = None

    def update_service(self, service_name: str, status: str):
        if self.services is None:
            self.services = ServicesDTO()
        setattr(self.services, service_name, status)

