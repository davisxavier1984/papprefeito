"""
Preparação e renderização dos relatórios PDF, compartilhadas entre as rotas
individuais (/relatorios/pdf e /relatorios/pdf-detalhado) e a geração em lote.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.services.api_client import saude_api_client
from app.services.municipios_editados import municipio_editado_service
from app.services.relatorio_pdf import compute_financial_summary, create_pdf_report, create_detailed_pdf_report

TIPO_PREFEITO = "prefeito"
TIPO_DETALHADO = "detalhado"
TIPOS = (TIPO_PREFEITO, TIPO_DETALHADO)


class DadosNaoEncontrados(Exception):
    """A API do Ministério não devolveu dados de financiamento."""


@dataclass
class DadosRelatorio:
    resumos: List[Dict[str, Any]]
    pagamentos: List[Dict[str, Any]]
    resumo: Any  # ResumoFinanceiro
    tem_perdas_salvas: bool


async def preparar_dados(codigo_ibge: str, competencia: str) -> DadosRelatorio:
    """Consulta o Ministério e combina com as perdas salvas (mesma lógica das rotas individuais)."""
    dados = await saude_api_client.consultar_financiamento(codigo_ibge, competencia)
    if not dados or not dados.get('resumosPlanosOrcamentarios'):
        raise DadosNaoEncontrados(
            "Não foi possível localizar dados de financiamento para gerar o relatório"
        )

    resumos = dados.get('resumosPlanosOrcamentarios', [])
    editado = municipio_editado_service.get_editado(codigo_ibge, competencia)
    perdas = editado.perda_recurso_mensal if editado else [0.0] * len(resumos)

    return DadosRelatorio(
        resumos=resumos,
        pagamentos=dados.get('pagamentos', []),
        resumo=compute_financial_summary(resumos, perdas),
        tem_perdas_salvas=editado is not None,
    )


def renderizar_pdf(
    tipo: str,
    dados: DadosRelatorio,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
) -> bytes:
    """Gera o PDF do tipo pedido. É síncrono e pesado (WeasyPrint)."""
    if tipo == TIPO_PREFEITO:
        return create_pdf_report(
            municipio_nome=municipio_nome,
            uf=uf,
            competencia=competencia,
            resumo=dados.resumo,
            resumos_planos=dados.resumos,
        )
    if tipo == TIPO_DETALHADO:
        return create_detailed_pdf_report(
            municipio_nome=municipio_nome,
            uf=uf,
            competencia=competencia,
            resumo=dados.resumo,
            pagamentos=dados.pagamentos,
        )
    raise ValueError(f"Tipo de relatório desconhecido: {tipo}")
