"""
Endpoints para gerenciar edições de municípios no Appwrite
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query as QueryParam
from pydantic import BaseModel, Field

from app.services.edicoes_service import edicoes_service


router = APIRouter()


class EdicaoCreate(BaseModel):
    """Schema para criação/atualização de edição"""
    codigo_municipio: str = Field(..., description="Código IBGE do município")
    competencia: str = Field(..., description="Competência no formato AAAAMM", min_length=6, max_length=6)
    perca_recurso_mensal: List[float] = Field(..., description="Lista de valores de perda mensal por recurso")
    usuario_id: Optional[str] = Field(None, description="ID do usuário que fez a edição")

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_municipio": "3106200",
                "competencia": "202409",
                "perca_recurso_mensal": [0.0, 1500.50, 2000.00],
                "usuario_id": "user_123"
            }
        }


class EdicaoResponse(BaseModel):
    """Schema de resposta de edição"""
    id: str
    codigo_municipio: str
    competencia: str
    perca_recurso_mensal: List[float]
    usuario_id: Optional[str]
    created_at: str
    updated_at: str


class EdicoesListResponse(BaseModel):
    """Schema de resposta para lista de edições"""
    success: bool
    total: int
    documents: List[EdicaoResponse]


class MessageResponse(BaseModel):
    """Schema de resposta genérica"""
    success: bool
    message: str


@router.get("/edicoes", response_model=EdicoesListResponse, tags=["Edições"])
async def listar_edicoes(
    codigo_municipio: Optional[str] = QueryParam(None, description="Filtrar por código do município"),
    limit: int = QueryParam(100, ge=1, le=1000, description="Número máximo de resultados"),
    offset: int = QueryParam(0, ge=0, description="Offset para paginação")
):
    """
    Lista todas as edições de municípios ou filtra por município específico.

    - **codigo_municipio**: (Opcional) Código IBGE do município para filtrar
    - **limit**: Número máximo de resultados (padrão: 100)
    - **offset**: Offset para paginação (padrão: 0)
    """
    result = await edicoes_service.listar_edicoes(
        codigo_municipio=codigo_municipio,
        limit=limit,
        offset=offset
    )

    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Erro ao listar edições'))

    return result


@router.get("/edicoes/{codigo_municipio}/{competencia}", response_model=EdicaoResponse, tags=["Edições"])
async def get_edicao(
    codigo_municipio: str,
    competencia: str
):
    """
    Busca edição específica de um município por código e competência.

    - **codigo_municipio**: Código IBGE do município
    - **competencia**: Competência no formato AAAAMM (ex: 202409)
    """
    edicao = await edicoes_service.get_edicao(codigo_municipio, competencia)

    if not edicao:
        raise HTTPException(
            status_code=404,
            detail=f"Edição não encontrada para município {codigo_municipio} e competência {competencia}"
        )

    return edicao


@router.post("/edicoes", tags=["Edições"])
async def salvar_edicao(edicao: EdicaoCreate):
    """
    Salva ou atualiza edição de município.

    Se já existir uma edição para o município e competência informados, ela será atualizada.
    Caso contrário, uma nova edição será criada.

    - **codigo_municipio**: Código IBGE do município
    - **competencia**: Competência no formato AAAAMM
    - **perca_recurso_mensal**: Array de valores de perda mensal
    - **usuario_id**: (Opcional) ID do usuário que fez a edição
    """
    result = await edicoes_service.salvar_edicao(
        codigo_municipio=edicao.codigo_municipio,
        competencia=edicao.competencia,
        perca_recurso_mensal=edicao.perca_recurso_mensal,
        usuario_id=edicao.usuario_id
    )

    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=result.get('message', 'Erro ao salvar edição')
        )

    return result


@router.delete("/edicoes/{codigo_municipio}/{competencia}", response_model=MessageResponse, tags=["Edições"])
async def deletar_edicao(
    codigo_municipio: str,
    competencia: str
):
    """
    Deleta edição de município.

    - **codigo_municipio**: Código IBGE do município
    - **competencia**: Competência no formato AAAAMM
    """
    result = await edicoes_service.deletar_edicao(codigo_municipio, competencia)

    if not result['success']:
        raise HTTPException(
            status_code=404 if 'não encontrada' in result.get('message', '') else 500,
            detail=result.get('message', 'Erro ao deletar edição')
        )

    return result


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check do serviço de edições
    """
    return {
        "status": "healthy",
        "service": "edicoes",
        "appwrite_configured": True
    }
