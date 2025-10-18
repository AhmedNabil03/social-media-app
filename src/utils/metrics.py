from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import re

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests', 
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request Latency', 
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP Errors',
    ['method', 'endpoint', 'exception_type']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    
    EXCLUDED_PATHS = {'/metrics', '/health', '/docs', '/redoc', '/openapi.json', '/favicon.ico'}
    
    def _normalize_path(self, path: str) -> str:

        if path in self.EXCLUDED_PATHS:
            return path
        
        parts = path.split('/')
        normalized = []
        
        for part in parts:
            if part.isdigit() or self._is_uuid(part):
                normalized.append('{id}')
            else:
                normalized.append(part)
        
        return '/'.join(normalized)
    
    @staticmethod
    def _is_uuid(value: str) -> bool:
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(value))
    
    async def dispatch(self, request: Request, call_next):
        
        endpoint = self._normalize_path(request.url.path)
        method = request.method
        
        start_time = time.time()
        
        status_code = 500
        exception_type = None
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
            
        except Exception as e:
            exception_type = type(e).__name__
            ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                exception_type=exception_type
            ).inc()
            raise
            
        finally:
            duration = time.time() - start_time
            
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()


def setup_metrics(app: FastAPI):

    app.add_middleware(PrometheusMiddleware)
    
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
