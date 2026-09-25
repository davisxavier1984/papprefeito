"""Testes do motor de regras do preenchimento automático (story 3.3).

Os dados de pagamento são os da API do Ministério para 290240, competência 202512;
o usuário havia informado eSF = 24.000,00 e Saúde Bucal = 12.710,22.
"""
from decimal import Decimal

from app.services.regras_perda import equipes_novas_padrao, sugerir
from app.services.valores_referencia import CATALOGO

VALORES = {k: (Decimal(v[1]), "202405") for k, v in CATALOGO.items()}

PAGAMENTO_290240 = {
    'qtEsfTotalPgto': 6, 'vlVinculoEsf': 36000, 'vlQualidadeEsf': 36000, 'qtTetoEsf': 6,
    'qtEsfCredenciado': 6, 'dsFaixaIndiceEquidadeEsfEap': 'ESTRATO 2', 'vlFixoEsf': 96000,
    'dsClassificacaoVinculoEsfEap': 'BOM', 'dsClassificacaoQualidadeEsfEap': 'BOM',
    'qtTetoAcs': 29, 'qtAcsDiretoPgto': 44, 'qtAcsDiretoCredenciado': 44,
    'qtSbPagamentoModalidadeI': 6, 'qtSbPagamentoModalidadeII': 0,
    'vlPagamentoEsb40hQualidade': 16530.78, 'vlPagamentoEsb40h': 36126,
    'qtSb40hCredenciada': 6, 'qtTetoSb40h': 6, 'qtPopulacao': 11409,
    'vlPagamentoSesb': 0, 'vlPagamentoLrpdMunicipal': 11250,
}

RESUMOS = [
    {'dsPlanoOrcamentario': 'Equipes de Saúde da Família - eSF e equipes de Atenção Primária - eAP', 'dsEsferaAdministrativa': 'MUNICIPAL'},
    {'dsPlanoOrcamentario': 'Atenção à Saúde Bucal', 'dsEsferaAdministrativa': 'MUNICIPAL'},
    {'dsPlanoOrcamentario': 'Equipes Multiprofissionais - eMulti', 'dsEsferaAdministrativa': 'MUNICIPAL'},
    {'dsPlanoOrcamentario': 'Agentes Comunitários de Saúde', 'dsEsferaAdministrativa': 'MUNICIPAL'},
    {'dsPlanoOrcamentario': 'Demais programas, serviços e equipes da Atenção Primária à Saúde', 'dsEsferaAdministrativa': 'MUNICIPAL'},
    {'dsPlanoOrcamentario': 'Incentivo estadual', 'dsEsferaAdministrativa': 'ESTADUAL'},
]


def _planos(pagamento=PAGAMENTO_290240):
    return {p.tipo: p for p in sugerir({'pagamentos': [pagamento], 'resumosPlanosOrcamentarios': RESUMOS}, VALORES)}


def test_esf_reproduz_valor_informado_pelo_usuario():
    assert _planos()['esf'].total_sugerido == 24000.00  # 6 eSF × (2.000 vínculo + 2.000 qualidade)


def test_saude_bucal_reproduz_valor_informado_pelo_usuario():
    # 6 eSB × 918,37 (BOM → ÓTIMO) + SESB 7.200 (11.409 hab., não recebe)
    assert abs(_planos()['sb'].total_sugerido - 12710.22) <= 0.05


def test_opcionais_de_saude_bucal_nao_entram_por_padrao():
    comps = {c.id: c for c in _planos()['sb'].componentes}
    assert not comps['uom'].incluido
    assert not comps['lrpd'].incluido
    assert comps['lrpd'].valor_unitario == 6750.00  # 11.250 → 18.000


def test_acs_usa_credenciados_menos_pagos_e_nunca_negativo():
    acs = _planos()['acs']  # 44 credenciados, 44 pagos, teto 29
    assert acs.total_sugerido == 0
    assert acs.regra_id == 'acs_v2'
    p = dict(PAGAMENTO_290240, qtAcsDiretoCredenciado=50)
    assert _planos(p)['acs'].total_sugerido == 6 * 3242.00
    p = dict(PAGAMENTO_290240, qtAcsDiretoCredenciado=40)  # menos credenciados que pagos
    assert _planos(p)['acs'].total_sugerido == 0


def test_acs_teto_fica_desmarcado_e_nao_conta_duas_vezes():
    p = dict(PAGAMENTO_290240, qtAcsDiretoCredenciado=50, qtTetoAcs=60)
    comps = {c.id: c for c in _planos(p)['acs'].componentes}
    assert comps['acs_credenciados'].incluido and comps['acs_credenciados'].quantidade == 6
    assert not comps['acs_teto'].incluido and comps['acs_teto'].quantidade == 10  # 60 − 50
    assert _planos(p)['acs'].total_sugerido == 6 * 3242.00


def test_acs_caso_real_do_historico():
    # 292070 (Maraú) 202512: 46 credenciados, 39 pagos, teto 64; o consultor informou 22.694,00
    p = dict(PAGAMENTO_290240, qtAcsDiretoCredenciado=46, qtAcsDiretoPgto=39, qtTetoAcs=64)
    assert _planos(p)['acs'].total_sugerido == 22694.00


def test_sesb_nao_entra_acima_de_20_mil_habitantes_nem_se_ja_recebe():
    comps = {c.id: c for c in _planos(dict(PAGAMENTO_290240, qtPopulacao=25000))['sb'].componentes}
    assert not comps['sesb'].incluido
    comps = {c.id: c for c in _planos(dict(PAGAMENTO_290240, vlPagamentoSesb=7200))['sb'].componentes}
    assert 'sesb' not in comps


def test_planos_sem_regra_e_esfera_estadual():
    planos = sugerir({'pagamentos': [PAGAMENTO_290240], 'resumosPlanosOrcamentarios': RESUMOS}, VALORES)
    assert len(planos) == 5  # o plano estadual não entra (posições iguais às da tabela)
    tipos = {p.tipo: p for p in planos}
    assert not tipos['emulti'].aplicavel
    assert not tipos['outro'].aplicavel


def test_padrao_de_equipes_novas():
    assert [equipes_novas_padrao(n) for n in (0, 1, 2, 3, 4, 11, 23)] == [0, 1, 2, 1, 2, 4, 8]
