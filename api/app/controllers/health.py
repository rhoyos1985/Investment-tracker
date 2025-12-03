import psutil
from fastapi import APIRouter, Depends, Response
from prometheus_client import generate_latest
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.util.enums.environment import Api_Environment
from app.infrastructure.settings.api_settings import settings
from app.infrastructure.settings.redis_client import redis_instance
from app.util.enums.health import DatabaseQuery
from app.util.functions.api_datetime import api_datetime
from app.util.dtos.health import HealthDTO, MonitoringSystem
from app.util.mappers.api_response import ApiResponse
from app.util.constants import api_endpoint_info
from app.handlers.error.response_error_exception import ResponseErrorException
from app.infrastructure.database.adapters.postgres_db import get_conection_database
    
router = APIRouter()

@router.get("/health", 
            tags=["Health"],
            summary="Checks all the api services",
            response_model=ApiResponse[HealthDTO])
def health_check(db: Session = Depends(get_conection_database)):
    checks: HealthDTO = HealthDTO(
        app_name= settings.APP_NAME,
        version= settings.APP_VERSION,
        status= "running",
        timestamp=api_datetime.get_datetime_now()  + "Z",
        environment= settings.ENVIRONMENT,
        services=None,
        system_monitoring=None
    )

    try:
        db.execute(text(DatabaseQuery.HEALTH_SELECT))
        checks.update_service(service_name="database", status="healthy")  

        if settings.ENVIRONMENT == Api_Environment.DEV:
            checks.system_monitoring = MonitoringSystem(
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(interval=1),
                disk_usage=psutil.disk_usage('/').percent
            )
    except Exception as e:
        checks.update_service(service_name="database", status=f"unhealthy: {str(e)}")
    
    # Check Redis
    try:
        redis_instance.redis_client.ping()
        checks.update_service(service_name="redis", status="healthy")
    except Exception as e:
        checks.update_service(service_name="redis", status=f"unhealthy: {str(e)}")

    return ApiResponse[HealthDTO](api_message="Services status",api_data=checks)
    
@router.get("/api-errors/{error_type}",
            summary="Check the error handling mechanism",
            responses=api_endpoint_info.API_ERROR_DESCRIPTION,
        )
def health_check_custom_error(error_type: str):
    from app.util.constants.error_types import ERROR_TYPES
    if error_type in ERROR_TYPES:
         raise ERROR_TYPES[error_type]()
    else:
        raise ResponseErrorException.not_found("The specified error type does not exist.")

@router.get("/metrics", summary="Expose basic metrics for monitoring")
async def metrics_endpoint():
    metrics_data = generate_latest()
    return ApiResponse[str](api_message="Metrics data", api_data=metrics_data.decode('utf-8'))
