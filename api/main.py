from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import search
from .routers import assistant
from .routers import registry

app = FastAPI(
    title="Windows Policy Intelligence API",
    description="Search and analyze Microsoft Group Policy (ADMX/ADML) definitions.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(assistant.router)
app.include_router(registry.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Windows Policy Intelligence API. Visit /docs for Swagger UI."}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred.", "details": str(exc)},
    )
