import time
from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class UseTimeMiddleware(BaseHTTPMiddleware):
    """ Middleware to measure request processing time """

    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """ Measure the time taken to process the request."""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time*1000:.3f}ms"
        return response
    
    @staticmethod
    def add_middleware(app: FastAPI) -> FastAPI:
        """ Add middleware to FastAPI application """
        app.add_middleware(UseTimeMiddleware)
        return app
