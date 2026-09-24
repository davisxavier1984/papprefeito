"""Municípios parecidos: mesma medida da simulação de 24/09/2026."""
from app.services.parecidos import Perfil, distancia, mediana, parecidos, perfil

DEMAIS = 'Demais programas'


def _resposta(pop, equipes, uf='BA', demais=0.0, nome='X'):
    return {
        'pagamentos': [{'qtPopulacao': pop, 'qtEsfTotalPgto': equipes, 'qtEapTotalPgto': 0,
                        'sgUf': uf, 'noMunicipio': nome}],
        'resumosPlanosOrcamentarios': [
            {'dsPlanoOrcamentario': 'Demais programas, serviços e equipes da Atenção Primária à Saúde',
             'dsEsferaAdministrativa': 'MUNICIPAL', 'vlIntegral': demais},
            {'dsPlanoOrcamentario': 'Demais programas, serviços e equipes da Atenção Primária à Saúde',
             'dsEsferaAdministrativa': 'ESTADUAL', 'vlIntegral': 999999},
        ],
    }


def _itens(valor, origem='manual'):
    return [{'plano': 'Demais programas, serviços e equipes da Atenção Primária à Saúde',
             'valor': valor, 'origem': origem}]


def test_perfil_le_populacao_equipes_e_so_resumos_municipais():
    p = perfil(_resposta(10000, 4, demais=500, nome='Boninal'))
    assert (p.populacao, p.equipes, p.uf, p.municipio) == (10000, 4, 'BA', 'Boninal')
    assert sum(p.recebe.values()) == 500


def test_perfil_incompleto_e_none():
    assert perfil({'pagamentos': [], 'resumosPlanosOrcamentarios': []}) is None
    assert perfil({'pagamentos': [{'qtPopulacao': 0}]}) is None
    assert perfil({'pagamentos': [{'qtPopulacao': -5000}]}) is None


def test_distancia_penaliza_outra_uf_e_cresce_com_a_populacao():
    a = perfil(_resposta(10000, 4))
    assert distancia(a, perfil(_resposta(10000, 4)), DEMAIS) == 0
    assert distancia(a, perfil(_resposta(10000, 4, uf='SP')), DEMAIS) == 0.5
    assert distancia(a, perfil(_resposta(20000, 4)), DEMAIS) < distancia(a, perfil(_resposta(200000, 4)), DEMAIS)


def test_parecidos_so_manual_positivo_outro_municipio_e_ordenado():
    alvo = perfil(_resposta(10000, 4))
    hist = [
        ('111111', '202606', perfil(_resposta(10000, 4)), _itens(19900)),
        ('222222', '202606', perfil(_resposta(50000, 4)), _itens(27300)),
        ('333333', '202606', perfil(_resposta(10000, 4)), _itens(5000, origem='regra')),  # não é do consultor
        ('444444', '202606', perfil(_resposta(10000, 4)), _itens(0)),                    # consultor pôs zero
        ('555555', '202606', perfil(_resposta(10000, 4)), _itens(60000)),               # mesmo município do alvo
        ('666666', '202606', perfil(_resposta(900000, 90)), _itens(107200)),
    ]
    ex = parecidos('555555', alvo, hist, DEMAIS, k=3)
    assert [e.codigo_ibge for e in ex] == ['111111', '222222', '666666']
    assert mediana(ex) == 27300


def test_mediana_vazia():
    assert mediana([]) is None


def test_montar_parecidos_usa_posicao_dos_planos_municipais():
    from app.api.endpoints.preenchimento import montar_parecidos
    dados = {
        'pagamentos': [{'qtPopulacao': 10000, 'qtEsfTotalPgto': 4, 'sgUf': 'BA', 'noMunicipio': 'Alvo'}],
        'resumosPlanosOrcamentarios': [
            {'dsPlanoOrcamentario': 'Equipes de Saúde da Família - eSF e equipes de Atenção Primária - eAP',
             'dsEsferaAdministrativa': 'MUNICIPAL', 'vlIntegral': 1},
            {'dsPlanoOrcamentario': 'Demais programas, serviços e equipes da Atenção Primária à Saúde',
             'dsEsferaAdministrativa': 'MUNICIPAL', 'vlIntegral': 0},
            {'dsPlanoOrcamentario': 'Incentivo financeiro da APS - Promoção à saúde',
             'dsEsferaAdministrativa': 'MUNICIPAL', 'vlIntegral': 0},
        ],
    }
    hist = [('111111', '202606', perfil(_resposta(10000, 4, nome='Boninal')), _itens(19900))]
    r = montar_parecidos('999999', '202606', dados, hist)
    assert [(p.indice, p.mediana) for p in r.planos] == [(1, 19900), (2, None)]
    assert r.planos[0].exemplos[0].municipio == 'Boninal'
