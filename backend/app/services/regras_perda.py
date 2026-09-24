"""
Motor de regras do preenchimento automático (story 3.3).

Estima o que o município **poderia ter** a partir do que o Ministério informa
(`pagamentos` + `resumosPlanosOrcamentarios`) e dos valores de referência vigentes.
Não grava nada: devolve, por plano, os componentes do cálculo para o usuário revisar.
Regras: docs/analises/regras-preenchimento-completo.md.
"""
import math
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from app.models.schemas import ComponenteSugestao, EstimativaEmulti, PlanoSugestao

Valores = Dict[str, Tuple[Decimal, str]]


def filtrar_resumos_municipais(resumos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Mesma regra do frontend: o array de perdas é posicional em relação a esta lista."""
    return [r for r in resumos
            if not r.get('dsEsferaAdministrativa') or r.get('dsEsferaAdministrativa') == 'MUNICIPAL']


def tipo_do_plano(nome: str) -> str:
    n = (nome or '').lower()
    if 'saúde da família' in n or 'saude da familia' in n or 'esf' in n.split():
        return 'esf'
    if 'bucal' in n:
        return 'sb'
    if 'agentes comunit' in n:
        return 'acs'
    if 'multiprofission' in n:
        return 'emulti'
    return 'outro'


def _n(p: Dict[str, Any], k: str) -> float:
    return float(p.get(k) or 0)


def _v(valores: Valores, chave: str) -> float:
    return float(valores[chave][0])


def _componente(id_: str, nome: str, quantidade: float, unitario: float, incluido: bool = True,
                editavel: bool = False, detalhe: Optional[str] = None,
                desconto: bool = False) -> ComponenteSugestao:
    """Componente do cálculo. `desconto` permite valor negativo (ex.: o que o município já recebe)."""
    return ComponenteSugestao(
        id=id_, nome=nome, quantidade=quantidade,
        valor_unitario=round(unitario if desconto else max(unitario, 0.0), 2),
        incluido=incluido, quantidade_editavel=editavel, detalhe=detalhe,
    )


def equipes_novas_padrao(faltam: int) -> int:
    """Padrão do usuário: até 2 faltando, todas; acima disso, um terço (para cima)."""
    return faltam if faltam <= 2 else math.ceil(faltam / 3)


def regra_esf(p: Dict[str, Any], valores: Valores) -> List[ComponenteSugestao]:
    vinc_otimo = _v(valores, 'esf_vinculo_otimo')
    qual_otimo = _v(valores, 'esf_qualidade_otimo')
    pagas = int(_n(p, 'qtEsfTotalPgto'))
    comps = []
    if pagas:
        ganho = max(vinc_otimo - _n(p, 'vlVinculoEsf') / pagas, 0) + max(qual_otimo - _n(p, 'vlQualidadeEsf') / pagas, 0)
        comps.append(_componente(
            'esf_otimo', 'Equipes pagas até ÓTIMO (vínculo + qualidade)', pagas, ganho,
            detalhe=f"{pagas} eSF pagas; classificação atual: vínculo {p.get('dsClassificacaoVinculoEsfEap') or '—'}, "
                    f"qualidade {p.get('dsClassificacaoQualidadeEsfEap') or '—'}",
        ))
    teto, cred = int(_n(p, 'qtTetoEsf')), int(_n(p, 'qtEsfCredenciado'))
    faltam = max(teto - cred, 0)
    estrato = (p.get('dsFaixaIndiceEquidadeEsfEap') or '').strip().split()[-1:]  # 'ESTRATO 2' -> ['2']
    chave_fixo = f"esf_fixo_estrato_{estrato[0]}" if estrato else ''
    fixo = _v(valores, chave_fixo) if chave_fixo in valores else (_n(p, 'vlFixoEsf') / pagas if pagas else 0)
    novas = equipes_novas_padrao(faltam)
    comps.append(_componente(
        'esf_novas', 'Equipes eSF novas até o teto', novas, fixo + vinc_otimo + qual_otimo,
        incluido=novas > 0, editavel=True,
        detalhe=f"Teto {teto}, credenciadas {cred}: faltam {faltam}. Padrão: "
                + ("todas" if faltam <= 2 else f"1/3 da diferença = {novas}"),
    ))
    comps.append(_componente(
        'esf_constante', 'Constante do usuário', 0, _v(valores, 'esf_constante_usuario'),
        editavel=True, detalhe="Informe quantas vezes somar, caso a caso",
    ))
    return comps


def regra_acs(p: Dict[str, Any], valores: Valores) -> List[ComponenteSugestao]:
    teto, pagos = int(_n(p, 'qtTetoAcs')), int(_n(p, 'qtAcsDiretoPgto'))
    cred = int(_n(p, 'qtAcsDiretoCredenciado'))
    return [_componente(
        'acs_teto', 'ACS até o teto', max(teto - pagos, 0), _v(valores, 'acs_valor'), editavel=True,
        detalhe=f"Teto {teto}, pagos {pagos}. Pela diferença credenciados − pagos seriam {max(cred - pagos, 0)}",
    )]


def regra_sb(p: Dict[str, Any], valores: Valores) -> List[ComponenteSugestao]:
    razao = _v(valores, 'sb_qualidade_otimo') / _v(valores, 'sb_qualidade_bom')
    n = int(_n(p, 'qtSbPagamentoModalidadeI') + _n(p, 'qtSbPagamentoModalidadeII'))
    comps = []
    qual_eq = _n(p, 'vlPagamentoEsb40hQualidade') / n if n else 0
    fixo_eq = _n(p, 'vlPagamentoEsb40h') / n if n else 0
    if n:
        comps.append(_componente(
            'sb_otimo', 'eSB pagas até qualidade ÓTIMO', n, qual_eq * razao - qual_eq,
            detalhe=f"{n} eSB 40h; qualidade paga {qual_eq:,.2f} por equipe",
        ))
    # Meta do usuário: uma eSB para cada eSF que o município teria (credenciadas + novas pelo
    # padrão da eSF). Explica 16 de 19 casos reconstruídos de 202512; o teto de eSB, só 6.
    cred = int(_n(p, 'qtSb40hCredenciada'))
    esf_cred = int(_n(p, 'qtEsfCredenciado'))
    esf_meta = esf_cred + equipes_novas_padrao(max(int(_n(p, 'qtTetoEsf')) - esf_cred, 0))
    faltam = max(esf_meta - cred, 0)
    if n:
        comps.append(_componente(
            'sb_novas', 'eSB novas (uma por eSF)', faltam, fixo_eq + qual_eq * razao, editavel=True,
            detalhe=f"Meta de {esf_meta} eSB (eSF credenciadas + novas); credenciadas {cred}: faltam {faltam}",
        ))
    pop = _n(p, 'qtPopulacao')
    if not _n(p, 'vlPagamentoSesb'):
        elegivel = 0 < pop <= _v(valores, 'sesb_populacao_max')
        comps.append(_componente(
            'sesb', 'SESB (Serviço de Especialidades em Saúde Bucal)', 1, _v(valores, 'sesb_custeio'),
            incluido=elegivel,
            detalhe=(f"População {pop:,.0f}: " + ("elegível" if elegivel else "acima do limite")
                     + ". Confira a cobertura mínima de 75% de saúde bucal"),
        ))
    comps.append(_componente(
        'uom', 'UOM (unidade odontológica móvel)', 1, _v(valores, 'uom_custeio'),
        incluido=False, editavel=True, detalhe="Opcional",
    ))
    faixas = [_v(valores, f'lrpd_faixa_{i}') for i in range(1, 5)]
    atual = _n(p, 'vlPagamentoLrpdMunicipal')
    proxima = next((f for f in faixas if f > atual + 0.01), None)
    if proxima is not None:
        comps.append(_componente(
            'lrpd', 'LRPD: implantar' if not atual else 'LRPD: próxima faixa', 1, proxima - atual,
            incluido=False, detalhe=f"Recebe {atual:,.2f}; próxima faixa {proxima:,.2f}. Opcional",
        ))
    return comps


def regra_emulti(est: EstimativaEmulti) -> List[ComponenteSugestao]:
    """eMulti pelos profissionais elegíveis do CNES (story 3.6): alvo − o que já recebe."""
    atuais = est.atuais
    return [
        _componente(
            'emulti_alvo', 'eMulti possíveis pelos profissionais elegíveis (Estratégica)',
            est.equipes_estimadas, est.custeio_modalidade['estrategica'], editavel=True,
            detalhe=(f"mín(eSF + eAP = {est.equipes_aps}; elegíveis ÷ {est.divisor} = "
                     f"{est.profissionais_elegiveis // est.divisor}; nutricionistas + psicólogos = "
                     f"{est.nutricionistas_psicologos})" + (f". {est.aviso}" if est.aviso else "")),
        ),
        _componente(
            'emulti_atual', 'Custeio que já recebe (desconta)', 1, -est.custeio_atual, desconto=True,
            detalhe=f"Atuais: {atuais['estrategica']} Estratégica, {atuais['complementar']} Complementar, "
                    f"{atuais['ampliada']} Ampliada",
        ),
    ]


def sugerir(dados: Dict[str, Any], valores: Valores,
            estimativa_emulti: Optional[EstimativaEmulti] = None) -> List[PlanoSugestao]:
    """Sugestão por plano, na mesma ordem posicional da tabela (planos municipais)."""
    pagamentos = dados.get('pagamentos') or []
    p = pagamentos[0] if pagamentos else {}
    ja_tem = set()
    planos = []
    for indice, resumo in enumerate(filtrar_resumos_municipais(dados.get('resumosPlanosOrcamentarios') or [])):
        nome = resumo.get('dsPlanoOrcamentario', '')
        tipo = tipo_do_plano(nome)
        # Um plano repetido (ex.: dois de Saúde Bucal) só recebe a regra na primeira ocorrência
        if tipo in ja_tem:
            tipo = 'outro'
        ja_tem.add(tipo)

        componentes: List[ComponenteSugestao] = []
        observacao = None
        if not p and tipo in ('esf', 'acs', 'sb'):
            tipo, observacao = 'outro', "Sem dados de pagamento do Ministério para calcular"
        if tipo == 'esf':
            componentes = regra_esf(p, valores)
        elif tipo == 'acs':
            componentes = regra_acs(p, valores)
        elif tipo == 'sb':
            componentes = regra_sb(p, valores)
        elif tipo == 'emulti':
            if estimativa_emulti:
                componentes = regra_emulti(estimativa_emulti)
            else:
                observacao = "Não foi possível consultar o CNES agora: o valor atual é mantido"
        else:
            observacao = observacao or "Sem regra: mantém o valor atual (preencha manualmente, se houver)"

        # Nunca negativo: quem já recebe mais que o alvo não tem perda
        total = max(round(sum(c.quantidade * c.valor_unitario for c in componentes if c.incluido), 2), 0.0)
        regra_id = ('emulti_estimativa_v1' if tipo == 'emulti' else f"{tipo}_v1") if componentes else None
        planos.append(PlanoSugestao(
            indice=indice, plano=nome, tipo=tipo, regra_id=regra_id,
            aplicavel=bool(componentes), componentes=componentes, total_sugerido=total,
            observacao=observacao,
        ))
    return planos
