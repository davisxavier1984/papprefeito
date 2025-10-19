"""Endpoints para geração de relatórios em PDF."""
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import RelatorioPDFRequest
from app.services.api_client import saude_api_client
from app.services.municipios_editados import municipio_editado_service
from app.services.relatorio_pdf import compute_financial_summary, create_pdf_report, create_detailed_pdf_report
from app.utils.logger import logger


router = APIRouter()


@router.post("/pdf")
async def gerar_relatorio_pdf(request: RelatorioPDFRequest):
    """Gera e retorna o relatório financeiro em PDF para download."""
    try:
        dados = await saude_api_client.consultar_financiamento(
            request.codigo_ibge,
            request.competencia
        )

        if not dados or not dados.get('resumosPlanosOrcamentarios'):
            raise HTTPException(
                status_code=404,
                detail="Não foi possível localizar dados de financiamento para gerar o relatório"
            )

        resumos = dados.get('resumosPlanosOrcamentarios', [])
        editado = municipio_editado_service.get_editado(
            request.codigo_ibge,
            request.competencia
        )
        percas = editado.perca_recurso_mensal if editado else [0.0] * len(resumos)

        resumo = compute_financial_summary(resumos, percas)

        # Passar também os resumos de planos orçamentários para a página 4
        pdf_bytes = create_pdf_report(
            municipio_nome=request.municipio_nome,
            uf=request.uf,
            competencia=request.competencia,
            resumo=resumo,
            resumos_planos=resumos
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

        dados = await saude_api_client.consultar_financiamento(
            request.codigo_ibge,
            request.competencia
        )

        if not dados or not dados.get('resumosPlanosOrcamentarios'):
            logger.warning(
                f"Dados de financiamento não encontrados - "
                f"Código IBGE: {request.codigo_ibge}, Competência: {request.competencia}"
            )
            raise HTTPException(
                status_code=404,
                detail="Não foi possível localizar dados de financiamento para gerar o relatório"
            )

        resumos = dados.get('resumosPlanosOrcamentarios', [])
        pagamentos = dados.get('pagamentos', [])

        if not pagamentos:
            logger.warning(
                f"Nenhum dado de pagamento encontrado nos dados da API - "
                f"Código IBGE: {request.codigo_ibge}, Competência: {request.competencia}"
            )

        editado = municipio_editado_service.get_editado(
            request.codigo_ibge,
            request.competencia
        )
        percas = editado.perca_recurso_mensal if editado else [0.0] * len(resumos)

        resumo = compute_financial_summary(resumos, percas)

        # Gerar PDF detalhado com dados de pagamento
        pdf_bytes = create_detailed_pdf_report(
            municipio_nome=request.municipio_nome,
            uf=request.uf,
            competencia=request.competencia,
            resumo=resumo,
            pagamentos=pagamentos
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
