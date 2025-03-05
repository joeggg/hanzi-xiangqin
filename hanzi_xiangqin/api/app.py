import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from . import routes


async def time_request(request: Request, call_next: RequestResponseEndpoint) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logging.info("Time taken: %sms", 1000 * process_time)
    return response


def create_app() -> FastAPI:
    app = FastAPI(title="Hanzi Xiangqin API")
    app.include_router(routes.health.router)
    app.include_router(routes.tests.router)
    app.add_middleware(BaseHTTPMiddleware, dispatch=time_request)

    origins = ["http://localhost:3000", "*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex="192.168.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
