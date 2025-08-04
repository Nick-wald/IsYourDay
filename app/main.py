from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from .db_manager import create_db_and_tables
from .file.utils import init_file_storage
from .middleware import UseTimeMiddleware
from .auth.auth import auth
from .file.file import file_manager_router
from .isyourday.isyourday import is_your_day_router

from .settings import DOCS_TITLE, DOCS_DESCRIPTION, DOCS_TAG_METADATA

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event handler."""
    # Initialize resources here
    create_db_and_tables()
    init_file_storage()
    yield
    # Cleanup resources here

app = FastAPI(
    lifespan=lifespan,
    title=DOCS_TITLE,
    description=DOCS_DESCRIPTION,
    )

# Import Middlewares

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

UseTimeMiddleware.add_middleware(app)

# Import routers

app.include_router(auth)
app.include_router(file_manager_router)
app.include_router(is_your_day_router)
