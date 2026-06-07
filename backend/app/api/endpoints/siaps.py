"""Endpoints SIAPS — classificação das equipes e lacuna financeira (gap).

Todos os endpoints exigem autenticação (registrado com ``_auth_required`` no router).
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.siaps_reference import (
    SIAPS_VALORES_VALIDADOS,
    quadrimestre_aplicavel,
)
from app.models.schemas import SiapsClassificacaoResponse, SiapsGapResponse
from app.services.api_client import saude_api_client
from app.services.municipios import municipio_service
from app.services.siaps_client import siaps_api_client
from app.services.siaps_gap import calcular_gaps
from app.utils.logger import logger

router = APIRouter()


def _validar_parametros(codigo_ibge: str, competencia: str) -> None:
    if not municipio_service.validate_codigo_ibge(codigo_ibge):
        raise HTTPException(
            status_code=400,
            detail="Código IBGE inválido. Deve ter pelo menos 6 dígitos numéricos",
        )
    if len(competencia) != 6 or not competencia.isdigit():
        raise HTTPException(
            status_code=400, detail="Competência deve estar no formato AAAAMM (6 dígitos)"
        )
    ano, mes = int(competencia[:4]), int(competencia[4:])
    if ano < 2020 or ano > 2030:
        raise HTTPException(status_code=400, detail="Ano deve estar entre 2020 e 2030")
    if mes < 1 or mes > 12:
        raise HTTPException(status_code=400, detail="Mês deve estar entre 01 e 12")


@router.get("/classificacao/{codigo_ibge}/{competencia}", response_model=SiapsClassificacaoResponse)
async def consultar_classificacao(
    codigo_ibge: str,
    competencia: str,
    quadrimestre: Optional[str] = Query(None, description="Override do quadrimestre (AAAAQN)"),
    force_refresh: bool = Query(False, description="Forçar nova consulta ignorando cache"),
):
    """Classificação SIAPS (CVAT + Qualidade) por equipe para o quadrimestre aplicável."""
    _validar_parametros(codigo_ibge, competencia)
    envelope = await siaps_api_client.consultar_para_competencia(
        codigo_ibge, competencia, quadrimestre=quadrimestre, force_refresh=force_refresh
    )
    if not envelope:
        quad = quadrimestre or quadrimestre_aplicavel(competencia)
        raise HTTPException(
            status_code=404,
            detail=f"Sem dados SIAPS para {codigo_ibge}/{quad}. "
                   f"O quadrimestre pode não estar publicado ainda.",
        )
    return envelope


@router.get("/gap/{codigo_ibge}/{competencia}", response_model=SiapsGapResponse)
async def consultar_gap(
    codigo_ibge: str,
    competencia: str,
    quadrimestre: Optional[str] = Query(None, description="Override do quadrimestre (AAAAQN)"),
    force_refresh: bool = Query(False, description="Forçar nova consulta ignorando cache"),
):
    """Lacuna financeira (vigente e potencial) derivada da classificação SIAPS.

    Cruza a classificação SIAPS com os dados de financiamento (estrato + pagamentos +
    resumos) e devolve as perdas posicionais alinhadas a ``resumosPlanosOrcamentarios``.
    """
    _validar_parametros(codigo_ibge, competencia)

    dados_fin = await saude_api_client.consultar_financiamento(codigo_ibge, competencia)
    if not dados_fin:
        raise HTTPException(
            status_code=404,
            detail="Sem dados de financiamento para a competência informada.",
        )

    envelope = await siaps_api_client.consultar_para_competencia(
        codigo_ibge, competencia, quadrimestre=quadrimestre, force_refresh=force_refresh
    )
    quad = quadrimestre or quadrimestre_aplicavel(competencia)
    if not envelope:
        raise HTTPException(
            status_code=404,
            detail=f"Sem dados SIAPS para {codigo_ibge}/{quad}.",
        )

    resultado = calcular_gaps(envelope, dados_fin)
    logger.info(
        "SIAPS gap %s/%s (quad %s): vigente=%.2f potencial=%.2f",
        codigo_ibge, competencia, quad,
        resultado["total_vigente"], resultado["total_potencial"],
    )
    return SiapsGapResponse(
        competencia=competencia,
        quadrimestre_aplicado=quad,
        estrato=resultado["estrato"],
        perda_por_recurso_vigente=resultado["perda_por_recurso_vigente"],
        perda_por_recurso_potencial=resultado["perda_por_recurso_potencial"],
        total_vigente=resultado["total_vigente"],
        total_potencial=resultado["total_potencial"],
        detalhe=resultado["detalhe"],
        valores_validados=SIAPS_VALORES_VALIDADOS,
    )
