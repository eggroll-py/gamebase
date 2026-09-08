from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.scheduler import start_scheduler, stop_scheduler
from app.routers import prices

@asynccontextmanager
async def lifespan(app:FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(lifespan=lifespan)
app.include_router(prices.router)