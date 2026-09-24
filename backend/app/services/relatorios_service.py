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


def montar_itens_lote(planos: List[Any]) -> List[Any]:
    """Converte os planos sugeridos em `ItemPerda` para o lote (função pura, sem rede/banco).

    Planos aplicáveis mantêm a regra (ou estimativa, no caso da eMulti). Planos sem regra
    também são gravados com origem "regra" — o zero foi uma decisão do sistema, não uma
    ausência de preenchimento do consultor — usando o `regra_id` sinalizador `sem_regra_v1`.
    """
    from app.models.schemas import ItemPerda

    return [
        ItemPerda(
            plano=p.plano,
            valor=p.total_sugerido if p.aplicavel else 0.0,
            origem='estimativa' if p.tipo == 'emulti' else 'regra',
            regra_id=p.regra_id if p.aplicavel else 'sem_regra_v1',
            valor_sugerido=p.total_sugerido if p.aplicavel else 0.0,
        )
        for p in planos
    ]


async def preencher_por_regras(codigo_ibge: str, competencia: str, usuario_id: Optional[str]) -> bool:
    """Calcula as perdas pelas regras da story 3.3 (valores padrão) e salva com origem "regra".

    Usado no lote para municípios sem perdas salvas. Inclui a eMulti estimada pelo CNES
    (se o CNES falhar, ela fica zerada); planos sem regra ficam zerados, mas com origem
    "regra" (decisão do sistema, não ausência de preenchimento do consultor).
    Retorna False se não houver dados do Ministério.
    """
    # Imports locais: evitam ciclo com os serviços de banco
    from app.core.database import async_session
    from app.models.schemas import MunicipioEditadoCreate
    from app.services.emulti_estimativa import estimar_ou_none
    from app.services.historico_perdas import HistoricoPerdasService
    from app.services.regras_perda import sugerir
    from app.services.valores_referencia import ValoresReferenciaService

    dados = await saude_api_client.consultar_financiamento(codigo_ibge, competencia)
    if not dados or not dados.get('resumosPlanosOrcamentarios'):
        return False
    async with async_session() as session:
        valores = await ValoresReferenciaService(session).vigentes(competencia)
        planos = sugerir(dados, valores, await estimar_ou_none(codigo_ibge, competencia, valores, dados))
        itens = montar_itens_lote(planos)
        perdas = [item.valor for item in itens]
        salvo = municipio_editado_service.upsert_editado(MunicipioEditadoCreate(
            codigo_ibge=codigo_ibge, competencia=competencia, perda_recurso_mensal=perdas, itens=itens))
        if not salvo:
            raise RuntimeError("falha ao salvar as perdas calculadas")
        await HistoricoPerdasService(session).registrar(codigo_ibge, competencia, 'upsert', perdas, itens, usuario_id)
    return True
