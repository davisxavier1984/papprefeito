"""
Preenchimento automático das perdas (story 3.3).

A sugestão só calcula: nada é gravado. O usuário revisa os componentes na tela e,
ao aplicar, os valores seguem pelo salvamento normal (upsert com itens de origem "regra").
"""
from decimal import Decimal
from typing import List

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_current_superuser, get_respostas_service, get_valores_service
from app.models.schemas import (
    AcertoResposta,
    EstimativaEmulti,
    ExemploParecido,
    MetricasPlano,
    ParecidosResposta,
    PlanoParecidos,
    PreenchidosPlano,
    SugestaoResposta,
    User,
    ValorReferencia,
    ValorReferenciaCreate,
)
from app.services import emulti_estimativa
from app.services.acerto import PLANOS_ACERTO, comparar, contar_preenchidos, metricas
from app.services.municipios_editados import municipio_editado_service
from app.services.parecidos import PREFIXOS_PARECIDOS, mediana, parecidos, perfil
from app.services.relatorios_service import DadosNaoEncontrados
from app.services.api_client import saude_api_client
from app.services.regras_perda import filtrar_resumos_municipais, sugerir
from app.services.respostas_ministerio import RespostasMinisterioService
from app.services.valores_referencia import ANO_CONFIRMADO_INICIAL, CATALOGO, VIGENCIA_INICIAL, ValoresReferenciaService
from app.utils.logger import logger

router = APIRouter()


def _itens(editado) -> List[dict]:
    """Converte os itens de um MunicipioEditado em dicts (aceita Pydantic ou dict)."""
    return [i.model_dump() if hasattr(i, 'model_dump') else dict(i) for i in (editado.itens or [])]


def _tem_manual_parecidos(itens: List[dict]) -> bool:
    """True se algum item de origem manual com valor > 0 estiver em Demais ou Promoção."""
    for item in itens:
        nome = item.get('plano') or ''
        if (any(nome.startswith(p) for p in PREFIXOS_PARECIDOS)
                and item.get('origem', 'manual') == 'manual' and item.get('valor')):
            return True
    return False


def montar_parecidos(codigo_ibge: str, competencia: str, dados: dict, historico) -> ParecidosResposta:
    """Para cada plano municipal de 'Demais' ou 'Promoção', os municípios parecidos preenchidos à mão."""
    alvo = perfil(dados)
    planos: List[PlanoParecidos] = []
    for indice, resumo in enumerate(filtrar_resumos_municipais(dados.get('resumosPlanosOrcamentarios') or [])):
        nome = resumo.get('dsPlanoOrcamentario') or ''
        prefixo = next((p for p in PREFIXOS_PARECIDOS if nome.startswith(p)), None)
        if not prefixo:
            continue
        exemplos = parecidos(codigo_ibge, alvo, historico, prefixo) if alvo else []
        planos.append(PlanoParecidos(indice=indice, plano=nome, mediana=mediana(exemplos),
                                     exemplos=[ExemploParecido(**vars(e)) for e in exemplos]))
    return ParecidosResposta(codigo_ibge=codigo_ibge, competencia=competencia, planos=planos)


def montar_acerto(entradas, itens_por_registro, desde: str, sem_resposta: int) -> AcertoResposta:
    """Métricas de acerto do automático (por plano) e quanto o consultor preencheu à mão."""
    pares = comparar(entradas)
    planos = [MetricasPlano(tipo=tipo, plano=rotulo, **metricas(pares[tipo]))
              for tipo, (rotulo, _) in PLANOS_ACERTO.items()]
    manuais = [PreenchidosPlano(plano=p, **c) for p, c in contar_preenchidos(itens_por_registro).items()]
    return AcertoResposta(desde=desde, planos=planos, manuais=manuais, sem_resposta=sem_resposta)


@router.get("/acerto", response_model=AcertoResposta)
async def acerto_automatico(
    desde: str = Query("202512", pattern=r"^\d{6}$"),
    current_user: User = Depends(get_current_superuser),
    valores_service: ValoresReferenciaService = Depends(get_valores_service),
    respostas_service: RespostasMinisterioService = Depends(get_respostas_service),
):
    """Quanto a regra atual se aproxima do que o consultor informou à mão (só leitura)."""
    editados = [e for e in municipio_editado_service.get_all_editados() if e.competencia >= desde and e.itens]
    chaves = [(e.codigo_ibge[:6], e.competencia) for e in editados]
    respostas = await respostas_service.listar(chaves)
    valores_por_comp: dict = {}
    entradas, sem_resposta = [], 0
    for e in editados:
        dados = respostas.get((e.codigo_ibge[:6], e.competencia))
        if not dados or not dados.get('pagamentos'):
            sem_resposta += 1
            continue
        if e.competencia not in valores_por_comp:
            valores_por_comp[e.competencia] = await valores_service.vigentes(e.competencia)
        try:
            sugestoes = sugerir(dados, valores_por_comp[e.competencia])
        except Exception as exc:
            logger.warning(f"Não foi possível sugerir para {e.codigo_ibge}/{e.competencia}: {exc}")
            sem_resposta += 1
            continue
        entradas.append((sugestoes, _itens(e)))
    return montar_acerto(entradas, [_itens(e) for e in editados], desde, sem_resposta)


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

    estimativa = await emulti_estimativa.estimar_ou_none(codigo_ibge, competencia, valores, dados)
    planos = sugerir(dados, valores, estimativa)
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


@router.get("/{codigo_ibge}/{competencia}/parecidos", response_model=ParecidosResposta)
async def municipios_parecidos(
    codigo_ibge: str,
    competencia: str,
    respostas_service: RespostasMinisterioService = Depends(get_respostas_service),
):
    """Como o consultor preencheu Demais e Promoção em municípios parecidos (só leitura)."""
    codigo_ibge = codigo_ibge[:6]
    dados = await respostas_service.obter(codigo_ibge, competencia)
    if not dados:
        dados = await saude_api_client.consultar_financiamento(codigo_ibge, competencia)
    if not dados or not dados.get('resumosPlanosOrcamentarios'):
        raise HTTPException(status_code=404, detail="Sem dados de financiamento do Ministério para este município")
    # Só os editados que têm chance de contribuir: item manual com valor > 0 em Demais/Promoção
    candidatos = [e for e in municipio_editado_service.get_all_editados()
                  if e.itens and _tem_manual_parecidos(_itens(e))]
    chaves = [(e.codigo_ibge[:6], e.competencia) for e in candidatos]
    respostas = await respostas_service.listar(chaves)
    historico = []
    for e in candidatos:
        resposta = respostas.get((e.codigo_ibge[:6], e.competencia))
        if not resposta:
            continue
        try:
            perf = perfil(resposta)
        except Exception as exc:
            logger.warning(f"Não foi possível calcular o perfil de {e.codigo_ibge}/{e.competencia}: {exc}")
            continue
        if perf:
            historico.append((e.codigo_ibge[:6], e.competencia, perf, _itens(e)))
    return montar_parecidos(codigo_ibge, competencia, dados, historico)


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


# ================================
# ESTIMATIVA eMULTI (story 3.6)
# ================================

@router.get("/emulti/{codigo_ibge}/{competencia}/estimativa", response_model=EstimativaEmulti)
async def estimativa_emulti(
    codigo_ibge: str,
    competencia: str,
    divisor: Optional[int] = Query(None, ge=1, le=50, description="Profissionais elegíveis por equipe"),
    valores_service: ValoresReferenciaService = Depends(get_valores_service),
):
    """Estima as eMulti possíveis pelos profissionais elegíveis do CNES. Não grava nada."""
    valores = await valores_service.vigentes(competencia)
    try:
        return await emulti_estimativa.estimar(codigo_ibge, competencia, valores, divisor)
    except DadosNaoEncontrados as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except KeyError:
        raise HTTPException(status_code=409, detail="Valores de referência da eMulti não cadastrados")
    except Exception as exc:
        logger.error(f"Erro na estimativa eMulti de {codigo_ibge}/{competencia}: {exc}", exc_info=True)
        raise HTTPException(status_code=502, detail="Não foi possível consultar o CNES agora. Tente novamente.")
