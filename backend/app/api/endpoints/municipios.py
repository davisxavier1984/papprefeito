"""
Endpoints para consulta de municípios e UFs
"""
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import UF, Municipio, ResponseBase, ErrorResponse
from app.services.municipios import municipio_service
from app.utils.logger import logger

router = APIRouter()

@router.get("/ufs", response_model=List[UF])
async def listar_ufs():
    """
    Lista todas as Unidades Federativas (UFs) do Brasil

    Returns:
        List[UF]: Lista de UFs com código, nome e sigla
    """
    try:
        ufs = municipio_service.get_ufs()
        if not ufs:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma UF encontrada"
            )
        return ufs
    except Exception as e:
        logger.error(f"Erro ao listar UFs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao consultar UFs"
        )

@router.get("/municipios/{uf}", response_model=List[Municipio])
async def listar_municipios_por_uf(uf: str):
    """
    Lista municípios de uma UF específica

    Args:
        uf: Sigla da UF (ex: 'MG', 'SP')

    Returns:
        List[Municipio]: Lista de municípios da UF
    """
    try:
        # Validar UF
        uf = uf.upper()
        if not municipio_service.validate_uf(uf):
            raise HTTPException(
                status_code=400,
                detail=f"UF '{uf}' é inválida"
            )

        municipios = municipio_service.get_municipios_por_uf(uf)
        if not municipios:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum município encontrado para a UF {uf}"
            )

        return municipios

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar municípios da UF {uf}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao consultar municípios"
        )

@router.get("/municipio/codigo/{codigo_ibge}", response_model=Municipio)
async def buscar_municipio_por_codigo(codigo_ibge: str):
    """
    Busca município pelo código IBGE

    Args:
        codigo_ibge: Código IBGE do município (6 dígitos)

    Returns:
        Municipio: Dados do município
    """
    try:
        # Validar código IBGE
        if not municipio_service.validate_codigo_ibge(codigo_ibge):
            raise HTTPException(
                status_code=400,
                detail="Código IBGE inválido. Deve ter pelo menos 6 dígitos numéricos"
            )

        municipio = municipio_service.get_municipio_por_codigo(codigo_ibge)
        if not municipio:
            raise HTTPException(
                status_code=404,
                detail=f"Município com código IBGE {codigo_ibge} não encontrado"
            )

        return municipio

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar município por código {codigo_ibge}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao buscar município"
        )

@router.get("/validate/uf/{uf}")
async def validar_uf(uf: str):
    """
    Valida se uma UF existe

    Args:
        uf: Sigla da UF

    Returns:
        dict: Resultado da validação
    """
    try:
        is_valid = municipio_service.validate_uf(uf)
        return {
            "uf": uf.upper(),
            "valid": is_valid,
            "message": "UF válida" if is_valid else "UF inválida"
        }
    except Exception as e:
        logger.error(f"Erro ao validar UF {uf}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao validar UF"
        )

@router.get("/validate/codigo-ibge/{codigo_ibge}")
async def validar_codigo_ibge(codigo_ibge: str):
    """
    Valida formato do código IBGE

    Args:
        codigo_ibge: Código IBGE a validar

    Returns:
        dict: Resultado da validação
    """
    try:
        is_valid = municipio_service.validate_codigo_ibge(codigo_ibge)
        return {
            "codigo_ibge": codigo_ibge,
            "valid": is_valid,
            "message": "Código IBGE válido" if is_valid else "Código IBGE inválido"
        }
    except Exception as e:
        logger.error(f"Erro ao validar código IBGE {codigo_ibge}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao validar código IBGE"
        )