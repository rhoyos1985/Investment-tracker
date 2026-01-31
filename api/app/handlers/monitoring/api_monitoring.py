import time
import traceback
from app.handlers.error.testerror import UnifiedValidationException
from prometheus_client import Counter, Histogram, Gauge
from fastapi import Request
from fastapi.exception_handlers import http_exception_handler
from app.util.mappers.logger_mapper import LoggerMapper
from app.handlers.error.response_error_exception import ResponseErrorException
from app.util.dtos.extra_logger_information import HttpProcessInformation
from app.infrastructure.settings.logger import logger
from app.infrastructure.settings.api_settings import settings

# Métricas Prometheus
REQUEST_COUNT = Counter(
    'request_count', 
    'App Request Count',
    ['app_name', 'method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds', 
    'Request latency',
    ['app_name', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

MARKET_API_CALLS = Counter(
    'market_api_calls',
    'Number of market API calls',
    ['api_provider', 'status']
)

class APIMonitoring:
    def __init__(self, app_name: str = "portfolio_tracker"):
        self.app_name = settings.APP_NAME
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
       
        try:
            print("Monitoring API request...")
            response = await call_next(request)
            print("API request processed.")
            process_time = time.time() - start_time
        
            REQUEST_LATENCY.labels(
                app_name=self.app_name,
                endpoint=request.url.path
            ).observe(process_time)
        
            REQUEST_COUNT.labels(
                app_name=self.app_name,
                method=request.method,
                endpoint=request.url.path,
                http_status=response.status_code
            ).inc()
            
            latency = str(f"{process_time:.4f}s")
            client_host = request.client.host if request.client else "unknown"
            request_information = HttpProcessInformation(
                method=request.method, url=str(request.url), 
                client_host=client_host, 
                user_agent= request.headers.get("user-agent", ""),
                status=response.status_code, 
                latency_ms=latency
            ) 
            extra_data = LoggerMapper(extra_data=request_information).to_log_format()
            logger.info("📊 Monitoring api request", extra=extra_data)
        
            return response
        except ResponseErrorException:
            # Re-raise to let FastAPI's exception handler process it
            raise
        except Exception as e:
            logger.error("❌ Error in API monitoring middleware", extra={"error": str(e), "stack_trace": traceback.format_exc()})
            raise e

# Middleware para inyectar en FastAPI
api_monitoring = APIMonitoring()
