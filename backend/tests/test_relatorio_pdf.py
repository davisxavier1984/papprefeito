"""Testes para utilitários de geração de relatório em PDF."""
from app.models.schemas import ResumoFinanceiro
from app.services.relatorio_pdf import compute_financial_summary, create_pdf_report


def test_compute_financial_summary_basic():
    resumos = [
        {"vlEfetivoRepasse": 1000.0},
        {"vlEfetivoRepasse": 500.0},
    ]
    perdas = [100.0, 50.0]

    resumo = compute_financial_summary(resumos, perdas)

    assert resumo.total_perda_mensal == 150.0
    assert resumo.total_diferenca_anual == 1800.0
    assert resumo.total_recebido == 1500.0
    assert resumo.percentual_perda_anual == 10.0


def test_compute_financial_summary_aligns_missing_losses():
    resumos = [
        {"vlEfetivoRepasse": 300.0},
        {"vlEfetivoRepasse": 200.0},
        {"vlEfetivoRepasse": 100.0},
    ]
    perdas = [10.0]

    resumo = compute_financial_summary(resumos, perdas)

    assert resumo.total_perda_mensal == 10.0
    assert resumo.total_diferenca_anual == 120.0


def test_create_pdf_report_returns_pdf_bytes():
    resumo = ResumoFinanceiro(
        total_perda_mensal=150.0,
        total_diferenca_anual=1800.0,
        percentual_perda_anual=10.0,
        total_recebido=1500.0,
    )

    pdf_bytes = create_pdf_report(
        municipio_nome='Cidade Teste',
        uf='MG',
        competencia='202401',
        resumo=resumo
    )

    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert pdf_bytes.startswith(b'%PDF')
    assert len(pdf_bytes) > 1000
