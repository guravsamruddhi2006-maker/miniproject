"""
FastAPI Application Entrypoint.
Initializes app, CORS middleware, and mounts API routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.audit import router as audit_router

app = FastAPI(
    title="Human-in-the-Loop Financial Filing Auditor API",
    description="Agentic AI backend for financial filing extraction, validation, and human review.",
    version="0.1.0",
)

# CORS configuration allowing local frontend development
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(audit_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Human-in-the-Loop Financial Filing Auditor API is running",
        "docs_url": "/docs",
        "phase": "Phase 1 - Scaffolding & Foundation",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "auditor-backend"}
