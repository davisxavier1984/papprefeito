"""
Preenchimento automático das perdas (story 3.3).

A sugestão só calcula: nada é gravado. O usuário revisa os componentes na tela e,
ao aplicar, os valores seguem pelo salvamento normal (upsert com itens de origem "regra").
"""
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_superuser, get_valores_service
from app.models.schemas import SugestaoResposta, User, ValorReferencia, ValorReferenciaCreate
from app.services.api_client import saude_api_client
from app.services.regras_perda import sugerir
from app.services.valores_referencia import ANO_CONFIRMADO_INICIAL, CATALOGO, VIGENCIA_INICIAL, ValoresReferenciaService
from app.utils.logger import logger

router = APIRouter()


@router.get("/{codigo_ibge}/{competencia}/sugestao", response_model=SugestaoResposta)
async def sugestao_preenchimento(
    codigo_ibge: str,
    competencia: str,
    valores_service: ValoresReferenciaService = Depends(get_valores_service),
):
    """Calcula o que o município poderia ter, por plano, sem gravar nada."""
    dados = await saude_api_client.consultar_financiamento(codigo_ibge, competencia)
    if not dados or not dados.get('resumosPlanosOrcamentarios'):
        raise HTTPException(status_code=404, detail="Sem dados de financiamento do Ministério para este município")

    valores = await valores_service.vigentes(competencia)
    faltando = [c for c in CATALOGO if c not in valores]
    if faltando:
        logger.error(f"Valores de referência ausentes para {competencia}: {faltando}")
        raise HTTPException(status_code=409, detail="Valores de referência não cadastrados para esta competência")

    planos = sugerir(dados, valores)
    mais_antiga = min(v for _, v in valores.values())
    mais_recente = max(v for _, v in valores.values())
    # Ano coberto pelos valores: os iniciais valem como conferidos para 2025
    ano_coberto = ANO_CONFIRMADO_INICIAL if mais_recente == VIGENCIA_INICIAL else mais_recente[:4]
    aviso = None
    if ano_coberto < competencia[:4]:
        aviso = (f"Não há valores de referência cadastrados para {competencia[:4]}; "
                 f"usando os de {ano_coberto}. Atualize em Valores de referência.")
    return SugestaoResposta(codigo_ibge=codigo_ibge, competencia=competencia, planos=planos,
                            vigencia_mais_antiga=mais_antiga, aviso=aviso)


def _publico(row) -> ValorReferencia:
    return ValorReferencia(id=row.id, chave=row.chave, descricao=CATALOGO.get(row.chave, (row.chave,))[0],
                           vigente_desde=row.vigente_desde, valor=float(row.valor), fonte=row.fonte)


@router.get("/valores-referencia", response_model=List[ValorReferencia])
async def listar_valores_referencia(
    valores_service: ValoresReferenciaService = Depends(get_valores_service),
):
    return [_publico(r) for r in await valores_service.listar()]


@router.post("/valores-referencia", response_model=ValorReferencia)
async def cadastrar_valor_referencia(
    dados: ValorReferenciaCreate,
    current_user: User = Depends(get_current_superuser),
    valores_service: ValoresReferenciaService = Depends(get_valores_service),
):
    """Cadastra o valor de uma chave a partir de uma competência (substitui se já houver)."""
    if dados.chave not in CATALOGO:
        raise HTTPException(status_code=400, detail="Chave desconhecida")
    row = await valores_service.cadastrar(dados.chave, dados.vigente_desde, Decimal(str(dados.valor)),
                                          dados.fonte, current_user.id)
    return _publico(row)


@router.delete("/valores-referencia/{id_}")
async def remover_valor_referencia(
    id_: int,
    current_user: User = Depends(get_current_superuser),
    valores_service: ValoresReferenciaService = Depends(get_valores_service),
):
    try:
        if not await valores_service.remover(id_):
            raise HTTPException(status_code=404, detail="Valor não encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "Removido"}
