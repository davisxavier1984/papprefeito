
import asyncio
from pathlib import Path
from app.services.relatorio_pdf import create_pdf_report
from app.models.schemas import ResumoFinanceiro

async def main():
    # Sample data for the report
    municipio_nome = "Teste"
    uf = "MG"
    competencia = "202401"
    resumo = ResumoFinanceiro(
        total_perda_mensal=10000,
        total_diferenca_anual=120000,
        percentual_perda_anual=10,
        total_recebido=100000,
    )
    resumos_planos = [
        {
            "dsPlanoOrcamentario": "Equipes de Saúde da Família - eSF e equipes de Atenção Primária - eAP",
            "vlIntegral": 100000,
            "vlAjuste": 0,
            "vlDesconto": 0,
            "vlEfetivoRepasse": 100000,
        }
    ]

    # Generate the PDF report
    pdf_bytes = create_pdf_report(
        municipio_nome=municipio_nome,
        uf=uf,
        competencia=competencia,
        resumo=resumo,
        resumos_planos=resumos_planos,
    )

    # Save the PDF to a file
    output_path = Path(__file__).parent / "relatorio_detalhado_test.pdf"
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"PDF report saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
