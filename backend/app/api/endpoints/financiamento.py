"""
Endpoints para consulta de dados de financiamento
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from app.models.schemas import (
    FinanciamentoParams,
    ResponseBase,
    ErrorResponse
)
from app.services.api_client import saude_api_client
from app.services.municipios import municipio_service
from app.utils.logger import logger

router = APIRouter()

@router.get("/competencia/latest")
async def obter_ultima_competencia():
    """
    Retorna a última competência disponível no sistema

    Returns:
        dict: Competência no formato AAAAMM
    """
    try:
        competencia = saude_api_client.get_latest_competencia()
        return {
            "competencia": competencia,
            "ano": competencia[:4],
            "mes": competencia[4:],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter última competência: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao obter competência"
        )

@router.get("/dados/{codigo_ibge}/{competencia}")
async def consultar_dados_financiamento(
    codigo_ibge: str,
    competencia: str,
    force_refresh: bool = Query(False, description="Forçar nova consulta ignorando cache")
):
    """
    Consulta dados de financiamento para um município e competência específicos

    Args:
        codigo_ibge: Código IBGE do município (6 dígitos)
        competencia: Competência no formato AAAAMM
        force_refresh: Se True, força nova consulta ignorando cache

    Returns:
        dict: JSON bruto da API de financiamento
    """
    try:
        # Validar parâmetros
        if not municipio_service.validate_codigo_ibge(codigo_ibge):
            raise HTTPException(
                status_code=400,
                detail="Código IBGE inválido. Deve ter pelo menos 6 dígitos numéricos"
            )

        if len(competencia) != 6 or not competencia.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Competência deve estar no formato AAAAMM (6 dígitos)"
            )

        # Validar ano e mês da competência
        try:
            ano = int(competencia[:4])
            mes = int(competencia[4:])

            if ano < 2020 or ano > 2030:
                raise HTTPException(
                    status_code=400,
                    detail="Ano deve estar entre 2020 e 2030"
                )

            if mes < 1 or mes > 12:
                raise HTTPException(
                    status_code=400,
                    detail="Mês deve estar entre 01 e 12"
                )

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Competência inválida"
            )

        # Consultar dados
        logger.info(f"Consultando financiamento para {codigo_ibge}/{competencia}")
        dados = await saude_api_client.consultar_financiamento(codigo_ibge, competencia)

        if not dados:
            # Sugerir competência anterior quando não houver dados
            try:
                ano_int = int(competencia[:4])
                mes_int = int(competencia[4:])
                if mes_int == 1:
                    sugestao = f"{ano_int - 1}12"
                else:
                    sugestao = f"{ano_int}{mes_int - 1:02d}"
            except Exception:
                sugestao = None

            detalhe = (
                "Nenhum dado encontrado para os parâmetros informados"
                + (f". Dica: a competência selecionada pode não estar publicada ainda. "
                   f"Tente uma competência anterior{f' (ex.: {sugestao})' if sugestao else ''}." )
            )

            raise HTTPException(
                status_code=404,
                detail=detalhe
            )

        return dados

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao consultar dados de financiamento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao consultar dados de financiamento"
        )

@router.post("/dados/consultar")
async def consultar_dados_post(params: FinanciamentoParams):
    """
    Consulta dados de financiamento via POST

    Args:
        params: Parâmetros de consulta (código IBGE e competência)

    Returns:
        dict: JSON bruto da API de financiamento
    """
    try:
        dados = await saude_api_client.consultar_financiamento(
            params.codigo_ibge,
            params.competencia
        )

        if not dados:
            raise HTTPException(
                status_code=404,
                detail="Nenhum dado encontrado para os parâmetros informados"
            )

        return dados

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao consultar dados via POST: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao consultar dados"
        )

@router.get("/test-connection")
async def testar_conexao_api():
    """
    Testa a conectividade com a API externa do governo

    Returns:
        dict: Status da conexão
    """
    try:
        is_connected = await saude_api_client.test_connection()

        return {
            "connected": is_connected,
            "api_url": saude_api_client.base_url,
            "message": "Conexão OK" if is_connected else "Falha na conexão",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erro ao testar conexão: {str(e)}")
        return {
            "connected": False,
            "api_url": saude_api_client.base_url,
            "message": f"Erro no teste de conexão: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
