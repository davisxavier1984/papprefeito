"""Métricas do painel de acerto do automático."""
from app.models.schemas import PlanoSugestao
from app.services.acerto import comparar, contar_preenchidos, metricas


def test_metricas_basicas():
    m = metricas([(100, 100), (120, 100), (0, 0), (50, 0), (0, 200)])
    assert m['registros'] == 5
    assert m['exatos'] == 2                 # (100,100) e (0,0)
    assert m['zero_certo'] == 3             # (100,100), (120,100), (0,0)
    assert m['com_valor'] == 3              # informado > 0: (100,100), (120,100), (0,200)
    assert m['dentro_25'] == 2              # entre os 3 com informado > 0: 0%, 20%, 100%
    assert m['erro_mediano'] == 0.2
    assert m['razao_soma'] == round(270 / 400, 4)
    assert m['alerta'] is True              # razão fora de [0,8; 1,25]


def test_metricas_sem_informado_nao_divide_por_zero():
    m = metricas([(0, 0), (10, 0)])
    assert m['com_valor'] == 0
    assert m['erro_mediano'] is None and m['razao_soma'] is None and m['alerta'] is False


def test_metricas_vazias():
    m = metricas([])
    assert m['registros'] == 0
    assert m['com_valor'] == 0


def _sug(tipo, total):
    return PlanoSugestao(indice=0, plano='p', tipo=tipo, aplicavel=True, total_sugerido=total)


def test_comparar_so_itens_manuais_e_por_tipo():
    entradas = [
        ([_sug('acs', 6484), _sug('esf', 24000)],
         [{'plano': 'Agentes Comunitários de Saúde', 'valor': 6484, 'origem': 'manual'},
          {'plano': 'Equipes de Saúde da Família - eSF e equipes de Atenção Primária - eAP', 'valor': 24000,
           'origem': 'regra'}]),
    ]
    pares = comparar(entradas)
    assert pares['acs'] == [(6484, 6484)]
    assert pares['esf'] == []                # item de origem regra não conta


def test_contar_preenchidos_demais_e_promocao():
    itens = [
        [{'plano': 'Demais programas, serviços e equipes da Atenção Primária à Saúde', 'valor': 19900, 'origem': 'manual'}],
        [{'plano': 'Demais programas, serviços e equipes da Atenção Primária à Saúde', 'valor': 0, 'origem': 'manual'},
         {'plano': 'Incentivo financeiro da APS - Promoção à saúde', 'valor': 5000, 'origem': 'manual'}],
    ]
    c = contar_preenchidos(itens)
    assert c['Demais programas'] == {'registros': 2, 'preenchidos': 1}
    assert c['Incentivo financeiro da APS - Promoção'] == {'registros': 1, 'preenchidos': 1}


def test_montar_acerto():
    from app.api.endpoints.preenchimento import montar_acerto
    entradas = [([_sug('acs', 6484)], [{'plano': 'Agentes Comunitários de Saúde', 'valor': 6484, 'origem': 'manual'}])]
    r = montar_acerto(entradas, [e[1] for e in entradas], '202512', sem_resposta=2)
    acs = next(p for p in r.planos if p.tipo == 'acs')
    assert (acs.registros, acs.exatos, acs.plano) == (1, 1, 'ACS')
    assert r.sem_resposta == 2 and r.desde == '202512'
    assert {m.plano for m in r.manuais} == {'Demais programas', 'Incentivo financeiro da APS - Promoção'}
