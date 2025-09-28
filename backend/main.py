"""
FastAPI backend para o sistema MaisPAP
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.router import api_router
from app.core.config import settings

# Criar instância do FastAPI
app = FastAPI(
    title="papprefeito API",
    description="API REST para consulta de dados de financiamento APS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers da API
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "papprefeito API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler geral para exceções não tratadas"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno do servidor: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )