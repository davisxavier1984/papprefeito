"""
Endpoints para gerenciamento de dados editados de municípios
"""
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    MunicipioEditado,
    MunicipioEditadoCreate,
    MunicipioEditadoUpdate,
    ResponseBase
)
from app.services.municipios_editados import municipio_editado_service
from app.services.municipios import municipio_service
from app.utils.logger import logger

router = APIRouter()

@router.get("/", response_model=List[MunicipioEditado])
async def listar_municipios_editados():
    """
    Lista todos os municípios com dados editados

    Returns:
        List[MunicipioEditado]: Lista de municípios editados
    """
    try:
        editados = municipio_editado_service.get_all_editados()
        return editados
    except Exception as e:
        logger.error(f"Erro ao listar municípios editados: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao listar dados editados"
        )

@router.get("/{codigo_ibge}/{competencia}", response_model=MunicipioEditado)
async def obter_municipio_editado(codigo_ibge: str, competencia: str):
    """
    Obtém dados editados de um município específico

    Args:
        codigo_ibge: Código IBGE do município
        competencia: Competência no formato AAAAMM

    Returns:
        MunicipioEditado: Dados editados do município
    """
    try:
        # Validar parâmetros
        if not municipio_service.validate_codigo_ibge(codigo_ibge):
            raise HTTPException(
                status_code=400,
                detail="Código IBGE inválido"
            )

        if len(competencia) != 6 or not competencia.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Competência deve estar no formato AAAAMM"
            )

        editado = municipio_editado_service.get_editado(codigo_ibge, competencia)
        if not editado:
            raise HTTPException(
                status_code=404,
                detail="Dados editados não encontrados para este município/competência"
            )

        return editado

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter dados editados: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao obter dados editados"
        )

@router.post("/", response_model=MunicipioEditado, status_code=status.HTTP_201_CREATED)
async def criar_municipio_editado(municipio_data: MunicipioEditadoCreate):
    """
    Cria novos dados editados para um município

    Args:
        municipio_data: Dados do município a criar

    Returns:
        MunicipioEditado: Dados editados criados
    """
    try:
        # Validar parâmetros
        if not municipio_service.validate_codigo_ibge(municipio_data.codigo_ibge):
            raise HTTPException(
                status_code=400,
                detail="Código IBGE inválido"
            )

        # Verificar se já existe
        existing = municipio_editado_service.get_editado(
            municipio_data.codigo_ibge,
            municipio_data.competencia
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Dados editados já existem para este município/competência"
            )

        editado = municipio_editado_service.create_editado(municipio_data)
        if not editado:
            raise HTTPException(
                status_code=500,
                detail="Erro ao criar dados editados"
            )

        return editado

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar dados editados: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao criar dados editados"
        )

@router.put("/{codigo_ibge}/{competencia}", response_model=MunicipioEditado)
async def atualizar_municipio_editado(
    codigo_ibge: str,
    competencia: str,
    update_data: MunicipioEditadoUpdate
):
    """
    Atualiza dados editados de um município

    Args:
        codigo_ibge: Código IBGE do município
        competencia: Competência no formato AAAAMM
        update_data: Dados para atualização

    Returns:
        MunicipioEditado: Dados editados atualizados
    """
    try:
        # Validar parâmetros
        if not municipio_service.validate_codigo_ibge(codigo_ibge):
            raise HTTPException(
                status_code=400,
                detail="Código IBGE inválido"
            )

        editado = municipio_editado_service.update_editado(
            codigo_ibge,
            competencia,
            update_data
        )
        if not editado:
            raise HTTPException(
                status_code=404,
                detail="Dados editados não encontrados para atualização"
            )

        return editado

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar dados editados: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao atualizar dados editados"
        )

@router.delete("/{codigo_ibge}/{competencia}")
async def deletar_municipio_editado(codigo_ibge: str, competencia: str):
    """
    Remove dados editados de um município

    Args:
        codigo_ibge: Código IBGE do município
        competencia: Competência no formato AAAAMM

    Returns:
        dict: Confirmação da remoção
    """
    try:
        # Validar parâmetros
        if not municipio_service.validate_codigo_ibge(codigo_ibge):
            raise HTTPException(
                status_code=400,
                detail="Código IBGE inválido"
            )

        success = municipio_editado_service.delete_editado(codigo_ibge, competencia)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Dados editados não encontrados para remoção"
            )

        return {
            "message": "Dados editados removidos com sucesso",
            "codigo_ibge": codigo_ibge,
            "competencia": competencia
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar dados editados: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao deletar dados editados"
        )

@router.post("/upsert", response_model=MunicipioEditado)
async def upsert_municipio_editado(municipio_data: MunicipioEditadoCreate):
    """
    Cria ou atualiza dados editados (upsert)

    Args:
        municipio_data: Dados do município

    Returns:
        MunicipioEditado: Dados editados salvos
    """
    try:
        # Validar parâmetros
        if not municipio_service.validate_codigo_ibge(municipio_data.codigo_ibge):
            raise HTTPException(
                status_code=400,
                detail="Código IBGE inválido"
            )

        editado = municipio_editado_service.upsert_editado(municipio_data)
        if not editado:
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar dados editados"
            )

        return editado

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer upsert dos dados editados: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao salvar dados editados"
        )