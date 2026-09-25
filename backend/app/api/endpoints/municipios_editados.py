"""
Endpoints para gerenciamento de dados editados de municípios
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_authorized_user, get_historico_service
from app.models.schemas import (
    HistoricoPerda,
    MunicipioEditado,
    MunicipioEditadoCreate,
    MunicipioEditadoUpdate,
    ResponseBase,
    User,
    validate_codigo_ibge_uf,
)
from app.services.historico_perdas import HistoricoPerdasService
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
async def criar_municipio_editado(
    municipio_data: MunicipioEditadoCreate,
    current_user: User = Depends(get_current_authorized_user),
    historico: HistoricoPerdasService = Depends(get_historico_service),
):
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

        # Restringe edição a UFs permitidas (bloqueia, não apenas loga)
        if not validate_codigo_ibge_uf(municipio_data.codigo_ibge):
            raise HTTPException(
                status_code=403,
                detail="UF não permitida para edição"
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

        await historico.registrar(
            editado.codigo_ibge, editado.competencia, "create",
            editado.perda_recurso_mensal, editado.itens, current_user.id,
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
    update_data: MunicipioEditadoUpdate,
    current_user: User = Depends(get_current_authorized_user),
    historico: HistoricoPerdasService = Depends(get_historico_service),
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

        await historico.registrar(
            editado.codigo_ibge, editado.competencia, "update",
            editado.perda_recurso_mensal, editado.itens, current_user.id,
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
async def deletar_municipio_editado(
    codigo_ibge: str,
    competencia: str,
    current_user: User = Depends(get_current_authorized_user),
    historico: HistoricoPerdasService = Depends(get_historico_service),
):
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

        anterior = municipio_editado_service.get_editado(codigo_ibge, competencia)
        success = municipio_editado_service.delete_editado(codigo_ibge, competencia)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Dados editados não encontrados para remoção"
            )

        # Guarda no histórico os valores que foram removidos
        await historico.registrar(
            codigo_ibge, competencia, "delete",
            anterior.perda_recurso_mensal if anterior else [],
            anterior.itens if anterior else None, current_user.id,
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
async def upsert_municipio_editado(
    municipio_data: MunicipioEditadoCreate,
    current_user: User = Depends(get_current_authorized_user),
    historico: HistoricoPerdasService = Depends(get_historico_service),
):
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

        # Restringe edição a UFs permitidas (bloqueia, não apenas loga)
        if not validate_codigo_ibge_uf(municipio_data.codigo_ibge):
            raise HTTPException(
                status_code=403,
                detail="UF não permitida para edição"
            )

        editado = municipio_editado_service.upsert_editado(municipio_data)
        if not editado:
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar dados editados"
            )

        await historico.registrar(
            editado.codigo_ibge, editado.competencia, "upsert",
            editado.perda_recurso_mensal, editado.itens, current_user.id,
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

@router.get("/{codigo_ibge}/{competencia}/historico", response_model=List[HistoricoPerda])
async def historico_municipio_editado(
    codigo_ibge: str,
    competencia: str,
    historico: HistoricoPerdasService = Depends(get_historico_service),
):
    """Histórico append-only das gravações de perdas do município na competência."""
    return await historico.listar(codigo_ibge, competencia)
