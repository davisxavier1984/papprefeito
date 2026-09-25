"""Endpoints para geração de relatórios em PDF."""
from io import BytesIO

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.core.dependencies import get_current_authorized_user
from app.models.schemas import (
    LoteConferenciaItem,
    LoteConferenciaRequest,
    LoteRequest,
    LoteStatus,
    RelatorioPDFRequest,
    User,
)
from app.services.relatorios_lote import conferir, gerenciador_lotes
from app.services.relatorios_service import (
    TIPO_DETALHADO,
    TIPO_PREFEITO,
    DadosNaoEncontrados,
    preparar_dados,
    renderizar_pdf,
)
from app.utils.logger import logger


router = APIRouter()


@router.post("/pdf")
async def gerar_relatorio_pdf(request: RelatorioPDFRequest):
    """Gera e retorna o relatório financeiro em PDF para download."""
    try:
        try:
            dados = await preparar_dados(request.codigo_ibge, request.competencia)
        except DadosNaoEncontrados as exc:
            raise HTTPException(status_code=404, detail=str(exc))

        pdf_bytes = renderizar_pdf(
            TIPO_PREFEITO, dados, request.municipio_nome, request.uf, request.competencia
        )

        file_name = f"relatorio_{request.codigo_ibge}_{request.competencia}.pdf"

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao gerar relatório PDF: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao gerar o relatório PDF"
        )


@router.post("/pdf-detalhado")
async def gerar_relatorio_detalhado_pdf(request: RelatorioPDFRequest):
    """Gera e retorna o relatório financeiro DETALHADO em PDF para download."""
    try:
        logger.info(
            f"Iniciando geração de relatório detalhado - "
            f"Município: {request.municipio_nome}/{request.uf}, "
            f"Código IBGE: {request.codigo_ibge}, Competência: {request.competencia}"
        )

        try:
            dados = await preparar_dados(request.codigo_ibge, request.competencia)
        except DadosNaoEncontrados as exc:
            logger.warning(
                f"Dados de financiamento não encontrados - "
                f"Código IBGE: {request.codigo_ibge}, Competência: {request.competencia}"
            )
            raise HTTPException(status_code=404, detail=str(exc))

        if not dados.pagamentos:
            logger.warning(
                f"Nenhum dado de pagamento encontrado nos dados da API - "
                f"Código IBGE: {request.codigo_ibge}, Competência: {request.competencia}"
            )

        # Gerar PDF detalhado com dados de pagamento
        pdf_bytes = renderizar_pdf(
            TIPO_DETALHADO, dados, request.municipio_nome, request.uf, request.competencia
        )

        file_name = f"relatorio_detalhado_{request.codigo_ibge}_{request.competencia}.pdf"

        logger.info(
            f"Relatório detalhado gerado com sucesso - "
            f"Código IBGE: {request.codigo_ibge}, Arquivo: {file_name}"
        )

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(
            f"Erro de validação ao gerar relatório detalhado - "
            f"Código IBGE: {request.codigo_ibge}: {exc}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Erro na validação dos dados: {str(exc)}"
        )
    except Exception as exc:
        logger.error(
            f"Erro inesperado ao gerar relatório PDF detalhado - "
            f"Código IBGE: {request.codigo_ibge}, Competência: {request.competencia}: {exc}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao gerar o relatório PDF detalhado. Verifique os logs para mais detalhes."
        )


# ================================
# RELATÓRIOS EM LOTE (stories 3.4 e 3.5)
# ================================

@router.post("/lote/conferencia", response_model=List[LoteConferenciaItem])
async def conferir_lote(request: LoteConferenciaRequest):
    """Situação das perdas salvas de cada município antes de gerar o lote."""
    return conferir(request.competencia, request.municipios)


@router.post("/lote", response_model=LoteStatus, status_code=202)
async def criar_lote(
    request: LoteRequest,
    current_user: User = Depends(get_current_authorized_user),
):
    """Inicia a geração em segundo plano. Acompanhe por GET /relatorios/lote/{id}."""
    return gerenciador_lotes.criar(request, current_user.id).status_publico()


@router.get("/lote/{lote_id}", response_model=LoteStatus)
async def status_lote(
    lote_id: str,
    current_user: User = Depends(get_current_authorized_user),
):
    lote = gerenciador_lotes.obter(lote_id, current_user.id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return lote.status_publico()


@router.get("/lote/{lote_id}/download")
async def baixar_lote(
    lote_id: str,
    current_user: User = Depends(get_current_authorized_user),
):
    lote = gerenciador_lotes.obter(lote_id, current_user.id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    if lote.status != 'concluido':
        raise HTTPException(status_code=409, detail="O lote ainda não terminou")
    return FileResponse(
        lote.zip_path,
        media_type="application/zip",
        filename=f"relatorios_{lote.pedido.competencia}.zip",
    )
