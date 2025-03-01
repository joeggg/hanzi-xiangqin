from fastapi import FastAPI

from . import routes


def create_app() -> FastAPI:
    app = FastAPI(title="Hanzi Xiangqin API")
    app.include_router(routes.health.router)

    return app
