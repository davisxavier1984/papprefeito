"""
Sistema Simplificado de Geração de Relatório PDF Financeiro
Versão minimalista com formatação precisa e limpa.
"""

import os
import io
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from PIL import Image as PILImage

try:
    from utils import format_currency, criar_tabela_total_por_classificacao, currency_to_float
except ImportError:
    from .utils import format_currency, criar_tabela_total_por_classificacao, currency_to_float


class PDFReportGenerator:
    """
    Gerador simplificado de relatórios PDF financeiros.
    Focado em formatação precisa e layout limpo.
    """
    
    def __init__(self):
        """Inicializa o gerador com configurações básicas."""
        # Sistema de cores simplificado - apenas 4 cores essenciais
        self.cores = {
            'azul_principal': HexColor('#1f4e79'),    # Azul corporativo
            'verde_positivo': HexColor('#27AE60'),    # Verde para valores positivos
            'vermelho_alerta': HexColor('#E74C3C'),   # Vermelho para alertas
            'cinza_neutro': HexColor('#666666'),      # Cinza para textos secundários
        }
        
        self.estilos = self._criar_estilos()
    
    def _criar_estilos(self) -> Dict[str, ParagraphStyle]:
        """Cria 4 estilos tipográficos essenciais."""
        estilos_base = getSampleStyleSheet()
        estilos = {}
        
        # Título principal (18pt, azul, negrito)
        estilos['titulo'] = ParagraphStyle(
            'titulo',
            parent=estilos_base['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=6,
            textColor=self.cores['azul_principal'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtítulo (14pt, azul, negrito)
        estilos['subtitulo'] = ParagraphStyle(
            'subtitulo',
            parent=estilos_base['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=10,
            textColor=self.cores['azul_principal'],
            fontName='Helvetica-Bold'
        )
        
        # Texto normal (12pt, preto)
        estilos['normal'] = ParagraphStyle(
            'normal',
            parent=estilos_base['Normal'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=3,
            textColor=black,
            alignment=TA_JUSTIFY,
            leading=15
        )
        
        # Destaque (14pt, verde, negrito) para valores importantes
        estilos['destaque'] = ParagraphStyle(
            'destaque',
            parent=estilos_base['Normal'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=5,
            textColor=self.cores['verde_positivo'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        return estilos
    
    def _carregar_logo(self) -> tuple:
        """Carrega o logo com dimensões simples."""
        logo_path = os.path.join(os.path.dirname(__file__), 'logo_colorida_mg.png')
        
        if not os.path.exists(logo_path):
            return None, 0, 0
        
        try:
            with PILImage.open(logo_path) as img:
                largura_original, altura_original = img.size
            
            # Logo pequeno: altura fixa 1.5cm
            altura_final = 1.5 * cm
            fator_escala = altura_final / altura_original
            largura_final = largura_original * fator_escala
            
            return logo_path, largura_final, altura_final
            
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            return None, 0, 0
    
    def _criar_cabecalho(self, municipio: str, uf: str) -> list:
        """Cria cabeçalho simples com logo e título."""
        elementos = []
        
        logo_path, largura_logo, altura_logo = self._carregar_logo()
        
        if logo_path:
            # Cabeçalho com logo e título em linha
            logo_img = Image(logo_path, width=largura_logo, height=altura_logo)
            titulo = Paragraph(
                f"Relatório Financeiro - {municipio} - {uf}",
                self.estilos['titulo']
            )
            
            # Tabela simples: logo à esquerda, título à direita
            cabecalho_data = [[logo_img, titulo]]
            cabecalho_table = Table(cabecalho_data, colWidths=[4*cm, 14*cm])
            cabecalho_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elementos.append(cabecalho_table)
        else:
            # Título simples sem logo
            titulo = Paragraph(
                f"Relatório Financeiro - {municipio} - {uf}",
                self.estilos['titulo']
            )
            elementos.append(titulo)
        
        elementos.append(Spacer(1, 0.5*cm))
        return elementos
    
    def _criar_introducao(self) -> list:
        """Cria introdução básica."""
        elementos = []
        
        elementos.append(Paragraph("Introdução", self.estilos['subtitulo']))
        
        texto = """
        Este relatório apresenta a análise financeira da Atenção Primária à Saúde (APS) 
        do município, baseada nos critérios de qualidade e vínculo estabelecidos pelo 
        Ministério da Saúde. Os valores consideram diferentes cenários de classificação 
        e seus impactos financeiros correspondentes.
        """
        
        elementos.append(Paragraph(texto, self.estilos['normal']))
        elementos.append(Spacer(1, 0.5*cm))
        
        return elementos
    
    def _criar_cenario_atual(self, dados: Dict[str, Any]) -> list:
        """Cria seção do cenário atual."""
        elementos = []
        
        elementos.append(Paragraph("Cenário Atual", self.estilos['subtitulo']))
        
        try:
            tabela_classificacao = criar_tabela_total_por_classificacao(dados)
            valor_bom_row = tabela_classificacao[tabela_classificacao['Classificação'] == 'Bom']
            
            if not valor_bom_row.empty:
                valor_atual = valor_bom_row['Valor Total'].iloc[0]
                
                texto = f"""
                O município atualmente possui classificação "Bom" com valor mensal de 
                <b>{valor_atual}</b>. Este valor representa o financiamento atual baseado 
                nas equipes credenciadas e homologadas.
                """
            else:
                texto = "Dados do cenário atual baseados nas informações disponíveis."
            
            elementos.append(Paragraph(texto, self.estilos['normal']))
            
        except Exception as e:
            print(f"Erro ao processar cenário atual: {e}")
            elementos.append(Paragraph(
                "Cenário atual baseado nos dados do município.",
                self.estilos['normal']
            ))
        
        elementos.append(Spacer(1, 0.5*cm))
        return elementos
    
    def _criar_tabela_cenarios(self, dados: Dict[str, Any]) -> list:
        """Cria tabela simples de cenários."""
        elementos = []
        
        elementos.append(Paragraph("Cenários de Financiamento", self.estilos['subtitulo']))
        
        try:
            tabela_classificacao = criar_tabela_total_por_classificacao(dados)
            
            # Dados da tabela: [Classificação, Valor Mensal, Valor Anual]
            dados_tabela = [['Classificação', 'Valor Mensal', 'Valor Anual']]
            
            for _, row in tabela_classificacao.iterrows():
                classificacao = row['Classificação']
                valor_mensal = row['Valor Total']
                
                try:
                    valor_numerico = currency_to_float(valor_mensal)
                    valor_anual = valor_numerico * 12
                    valor_anual_str = format_currency(valor_anual)
                except:
                    valor_anual_str = "N/A"
                
                dados_tabela.append([classificacao, valor_mensal, valor_anual_str])
            
            # Tabela simples com bordas
            tabela = Table(dados_tabela, colWidths=[4*cm, 5*cm, 5*cm])
            tabela.setStyle(TableStyle([
                # Cabeçalho
                ('BACKGROUND', (0, 0), (-1, 0), self.cores['azul_principal']),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                
                # Corpo
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, self.cores['cinza_neutro']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elementos.append(tabela)
            
        except Exception as e:
            print(f"Erro ao criar tabela: {e}")
            elementos.append(Paragraph(
                "Erro ao gerar tabela de cenários.",
                self.estilos['normal']
            ))
        
        elementos.append(Spacer(1, 0.8*cm))
        return elementos
    
    def _criar_projecoes(self, dados: Dict[str, Any]) -> list:
        """Cria seção de projeções."""
        elementos = []
        
        elementos.append(Paragraph("Projeções Anuais", self.estilos['subtitulo']))
        
        try:
            tabela_classificacao = criar_tabela_total_por_classificacao(dados)
            
            valor_bom = currency_to_float(
                tabela_classificacao[tabela_classificacao['Classificação'] == 'Bom']['Valor Total'].iloc[0]
            )
            valor_otimo = currency_to_float(
                tabela_classificacao[tabela_classificacao['Classificação'] == 'Ótimo']['Valor Total'].iloc[0]
            )
            valor_regular = currency_to_float(
                tabela_classificacao[tabela_classificacao['Classificação'] == 'Regular']['Valor Total'].iloc[0]
            )
            
            ganho_anual = (valor_otimo - valor_bom) * 12
            perda_anual = (valor_bom - valor_regular) * 12
            
            # Texto com valores destacados
            texto_projecoes = f"""
            <b>Cenário Otimista:</b> Alcançando classificação "Ótimo", o município pode 
            ganhar <b>{format_currency(ganho_anual)}</b> anuais em financiamento adicional.
            
            <b>Cenário Pessimista:</b> Caindo para classificação "Regular", o município 
            perderia <b>{format_currency(perda_anual)}</b> anuais.
            
            <b>Diferença Total:</b> A variação entre o melhor e pior cenário pode alcançar 
            <b>{format_currency(ganho_anual + perda_anual)}</b> anuais.
            """
            
            elementos.append(Paragraph(texto_projecoes, self.estilos['normal']))
            
        except Exception as e:
            print(f"Erro ao calcular projeções: {e}")
            elementos.append(Paragraph(
                "Projeções baseadas nos cenários de classificação disponíveis.",
                self.estilos['normal']
            ))
        
        elementos.append(Spacer(1, 0.8*cm))
        return elementos
    
    def _criar_consideracoes(self) -> list:
        """Cria considerações finais."""
        elementos = []
        
        elementos.append(Paragraph("Considerações Finais", self.estilos['subtitulo']))
        
        texto = """
        Os valores apresentados são baseados nos critérios oficiais do Ministério da Saúde 
        e refletem o potencial financeiro real da APS municipal. A melhoria dos indicadores 
        de qualidade e vínculo resulta em incremento direto dos recursos federais.
        
        Recomenda-se o acompanhamento contínuo dos indicadores e implementação de estratégias 
        focadas na qualidade para maximizar o financiamento disponível.
        """
        
        elementos.append(Paragraph(texto, self.estilos['normal']))
        elementos.append(Spacer(1, 1*cm))
        
        return elementos
    
    def _criar_assinatura(self) -> list:
        """Cria assinatura simples."""
        elementos = []
        
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        assinatura = f"""
        <br/><br/>
        ____________________________________<br/>
        <b>Mais Gestor</b><br/>
        Alysson Ribeiro<br/>
        Data: {data_atual}
        """
        
        elementos.append(Paragraph(assinatura, self.estilos['normal']))
        
        return elementos
    
    def gerar_relatorio_pdf(self, nome_municipio: str, uf: str, dados_calculados: Dict[str, Any]) -> bytes:
        """
        Gera relatório PDF simplificado.
        
        Args:
            nome_municipio: Nome do município
            uf: UF do município 
            dados_calculados: Dados da API
            
        Returns:
            bytes: Conteúdo do PDF
        """
        try:
            buffer = io.BytesIO()
            
            # Documento com margens padrão
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2.5*cm,
                leftMargin=2.5*cm,
                topMargin=2.5*cm,
                bottomMargin=2.5*cm
            )
            
            # Elementos do documento
            elementos = []
            
            # Adicionar todas as seções
            elementos.extend(self._criar_cabecalho(nome_municipio, uf))
            elementos.extend(self._criar_introducao())
            elementos.extend(self._criar_cenario_atual(dados_calculados))
            elementos.extend(self._criar_tabela_cenarios(dados_calculados))
            elementos.extend(self._criar_projecoes(dados_calculados))
            elementos.extend(self._criar_consideracoes())
            elementos.extend(self._criar_assinatura())
            
            # Construir PDF
            doc.build(elementos)
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Erro na geração do PDF: {e}")
            raise
    
    def criar_nome_arquivo(self, nome_municipio: str) -> str:
        """Cria nome do arquivo PDF."""
        municipio_limpo = ''.join(c for c in nome_municipio if c.isalnum() or c in (' ', '-'))
        municipio_limpo = municipio_limpo.replace(' ', '-').lower()
        data_atual = datetime.now().strftime("%Y%m%d")
        return f"relatorio-financeiro-{municipio_limpo}-{data_atual}.pdf"


# Função de conveniência
def gerar_relatorio_pdf(nome_municipio: str, uf: str, dados_calculados: Dict[str, Any]) -> bytes:
    """
    Função de conveniência para gerar relatório PDF.
    
    Args:
        nome_municipio: Nome do município
        uf: UF do município
        dados_calculados: Dados da API
        
    Returns:
        bytes: Conteúdo do PDF
    """
    gerador = PDFReportGenerator()
    return gerador.gerar_relatorio_pdf(nome_municipio, uf, dados_calculados)