"""Endpoints para geração de relatórios em PDF."""
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import RelatorioPDFRequest
from app.services.api_client import saude_api_client
from app.services.municipios_editados import municipio_editado_service
from app.services.relatorio_pdf import compute_financial_summary, create_pdf_report
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

        pdf_bytes = create_pdf_report(
            municipio_nome=request.municipio_nome,
            uf=request.uf,
            competencia=request.competencia,
            resumo=resumo
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
