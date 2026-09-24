"""Montagem dos itens do lote (preenchimento automático sem regra, story acerto)."""
from app.models.schemas import PlanoSugestao
from app.services.relatorios_service import montar_itens_lote


def _plano(tipo, aplicavel, total=0.0, regra_id=None, plano='p'):
    return PlanoSugestao(indice=0, plano=plano, tipo=tipo, aplicavel=aplicavel,
                         total_sugerido=total, regra_id=regra_id)


def test_plano_sem_regra_grava_origem_regra_com_sem_regra_v1():
    itens = montar_itens_lote([_plano('outro', aplicavel=False, plano='Demais programas')])
    assert len(itens) == 1
    item = itens[0]
    assert item.origem == 'regra'
    assert item.regra_id == 'sem_regra_v1'
    assert item.valor == 0.0
    assert item.valor_sugerido == 0.0


def test_plano_com_regra_mantem_origem_regra_e_valor_sugerido():
    itens = montar_itens_lote([_plano('acs', aplicavel=True, total=6484.0, regra_id='acs_v2', plano='ACS')])
    item = itens[0]
    assert item.origem == 'regra'
    assert item.regra_id == 'acs_v2'
    assert item.valor == 6484.0
    assert item.valor_sugerido == 6484.0


def test_plano_emulti_usa_origem_estimativa():
    itens = montar_itens_lote([_plano('emulti', aplicavel=True, total=1000.0, regra_id='emulti_v1', plano='eMulti')])
    item = itens[0]
    assert item.origem == 'estimativa'
    assert item.regra_id == 'emulti_v1'
    assert item.valor_sugerido == 1000.0


def test_perdas_correspondem_ao_valor_de_cada_item():
    itens = montar_itens_lote([
        _plano('acs', aplicavel=True, total=100.0, regra_id='acs_v2', plano='ACS'),
        _plano('outro', aplicavel=False, plano='Demais programas'),
    ])
    assert [i.valor for i in itens] == [100.0, 0.0]
