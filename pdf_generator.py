"""
Sistema de Geração de Relatório PDF Financeiro
Gera relatórios PDF profissionais baseados no template Alcobaça
para análise financeira da APS municipal.
"""

import os
import io
import tempfile
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import numpy as np

try:
    from utils import format_currency, criar_tabela_total_por_classificacao, currency_to_float
    from consulta_dados import criar_grafico_piramide_mensal, criar_grafico_barras_horizontais, CORES_PADRAO
except ImportError:
    from .utils import format_currency, criar_tabela_total_por_classificacao, currency_to_float
    try:
        from .consulta_dados import criar_grafico_piramide_mensal, criar_grafico_barras_horizontais, CORES_PADRAO
    except ImportError:
        # Fallback case - definir cores padrão
        CORES_PADRAO = {
            'positivo': '#1E8449',
            'negativo': '#C0392B',
            'neutro': '#FFC300',
            'destaque': '#3498DB',
            'secundario': '#95A5A6',
            'sucesso': '#27AE60',
            'alerta': '#F39C12',
            'erro': '#E74C3C',
            'info': '#5DADE2'
        }
        criar_grafico_piramide_mensal = None
        criar_grafico_barras_horizontais = None


class PDFReportGenerator:
    """
    Gerador de relatórios PDF financeiros profissionais
    baseado no template Alcobaça para análise de APS municipal.
    """
    
    def __init__(self):
        """Inicializa o gerador de PDF com configurações padrão."""
        self.cores = {
            'azul_corporativo': HexColor('#1f4e79'),
            'cinza': HexColor('#666666'),
            'azul_claro': HexColor('#E6F2FF'),
            'branco': white,
            'preto': black
        }
        
        self.estilos = self._criar_estilos()
    
    def _criar_estilos(self) -> Dict[str, ParagraphStyle]:
        """Cria e retorna estilos personalizados para o PDF."""
        estilos_base = getSampleStyleSheet()
        estilos_customizados = {}
        
        # Título principal
        estilos_customizados['titulo_principal'] = ParagraphStyle(
            'titulo_principal',
            parent=estilos_base['Heading1'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=10,
            textColor=self.cores['azul_corporativo'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtítulo
        estilos_customizados['subtitulo'] = ParagraphStyle(
            'subtitulo',
            parent=estilos_base['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=15,
            textColor=self.cores['azul_corporativo'],
            fontName='Helvetica-Bold'
        )
        
        # Texto normal
        estilos_customizados['normal'] = ParagraphStyle(
            'normal',
            parent=estilos_base['Normal'],
            fontSize=11,
            spaceAfter=6,
            spaceBefore=3,
            textColor=self.cores['preto'],
            alignment=TA_JUSTIFY,
            leading=13
        )
        
        # Texto centralizado
        estilos_customizados['centro'] = ParagraphStyle(
            'centro',
            parent=estilos_customizados['normal'],
            alignment=TA_CENTER
        )
        
        # Texto para valores monetários
        estilos_customizados['valor'] = ParagraphStyle(
            'valor',
            parent=estilos_customizados['normal'],
            fontSize=12,
            textColor=self.cores['azul_corporativo'],
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
        )
        
        return estilos_customizados
    
    def _carregar_logo(self) -> Tuple[str, float, float]:
        """
        Carrega e prepara o logo da empresa.
        
        Returns:
            Tuple contendo caminho do logo, largura e altura
        """
        logo_path = os.path.join(os.path.dirname(__file__), 'logo_colorida_mg.png')
        
        if not os.path.exists(logo_path):
            # Fallback: criar um placeholder se o logo não existir
            return None, 0, 0
        
        try:
            # Carregar imagem para obter dimensões
            with PILImage.open(logo_path) as img:
                largura_original, altura_original = img.size
                
            # Calcular dimensões proporcionais (altura máxima 2cm)
            altura_max = 2 * cm
            fator_escala = altura_max / altura_original
            largura_final = largura_original * fator_escala
            altura_final = altura_max
            
            return logo_path, largura_final, altura_final
            
        except Exception as e:
            # Log do erro sem usar st.warning para evitar conflitos
            print(f"Aviso: Erro ao carregar logo: {e}")
            return None, 0, 0
    
    def _criar_cabecalho(self, municipio: str) -> list:
        """
        Cria o cabeçalho do relatório com logo e título.
        
        Args:
            municipio: Nome do município
            
        Returns:
            Lista de elementos do cabeçalho
        """
        elementos = []
        
        # Carregar logo
        logo_path, largura_logo, altura_logo = self._carregar_logo()
        
        if logo_path:
            # Criar tabela com logo e título
            logo_img = Image(logo_path, width=largura_logo, height=altura_logo)
            titulo = Paragraph(
                f"Relatório de Projeção Financeira<br/>Município de {municipio}",
                self.estilos['titulo_principal']
            )
            
            cabecalho_data = [[logo_img, titulo]]
            cabecalho_table = Table(cabecalho_data, colWidths=[4*cm, 14*cm])
            cabecalho_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            elementos.append(cabecalho_table)
        else:
            # Apenas título sem logo
            titulo = Paragraph(
                f"Relatório de Projeção Financeira - Município de {municipio}",
                self.estilos['titulo_principal']
            )
            elementos.append(titulo)
        
        elementos.append(Spacer(1, 1*cm))
        return elementos
    
    def _criar_secao_introducao(self) -> list:
        """
        Cria a seção de introdução do relatório.
        
        Returns:
            Lista de elementos da introdução
        """
        elementos = []
        
        # Título da seção
        elementos.append(Paragraph("Introdução", self.estilos['subtitulo']))
        
        # Texto de introdução baseado no template Alcobaça
        texto_introducao = """
        Este relatório apresenta uma análise detalhada da situação financeira atual e 
        projeções futuras para o financiamento da Atenção Primária à Saúde (APS) do 
        município. Os valores apresentados são baseados nos critérios de qualidade e 
        vínculo estabelecidos pelo Ministério da Saúde para as equipes de Saúde da 
        Família (eSF), equipes de Atenção Primária (eAP), equipes Multiprofissionais 
        (eMulti) e equipes de Saúde Bucal (eSB).
        
        A análise considera os diferentes cenários de classificação (Ótimo, Bom, 
        Suficiente e Regular) e seus impactos financeiros correspondentes, permitindo 
        uma visão estratégica para o planejamento e tomada de decisões municipais.
        """
        
        elementos.append(Paragraph(texto_introducao, self.estilos['normal']))
        elementos.append(Spacer(1, 0.5*cm))
        
        return elementos
    
    def _criar_secao_cenario_atual(self, dados: Dict[str, Any]) -> list:
        """
        Cria a seção do cenário atual com valores reais do município.
        
        Args:
            dados: Dados da API contendo informações do município
            
        Returns:
            Lista de elementos da seção
        """
        elementos = []
        
        # Título da seção
        elementos.append(Paragraph("Cenário Atual", self.estilos['subtitulo']))
        
        try:
            # Obter tabela de classificação
            tabela_classificacao = criar_tabela_total_por_classificacao(dados)
            
            # Extrair valor "Bom" (cenário atual)
            valor_bom_row = tabela_classificacao[tabela_classificacao['Classificação'] == 'Bom']
            if not valor_bom_row.empty:
                valor_atual_str = valor_bom_row['Valor Total'].iloc[0]
                valor_atual = currency_to_float(valor_atual_str)
                
                texto_cenario = f"""
                Com base na análise dos dados atuais do município, o valor mensal de 
                financiamento da APS está classificado como <b>"Bom"</b>, totalizando 
                <b>{valor_atual_str}</b> por mês.
                
                Este valor corresponde ao somatório dos componentes de qualidade e vínculo 
                das equipes credenciadas e homologadas no município, considerando as 
                classificações atuais de desempenho.
                """
            else:
                texto_cenario = """
                Os dados atuais do município indicam valores de financiamento baseados 
                na classificação atual das equipes de Atenção Primária à Saúde.
                """
            
            elementos.append(Paragraph(texto_cenario, self.estilos['normal']))
            
        except Exception as e:
            print(f"Aviso: Erro ao processar cenário atual: {e}")
            elementos.append(Paragraph(
                "Cenário atual baseado nos dados disponíveis do município.",
                self.estilos['normal']
            ))
        
        elementos.append(Spacer(1, 0.5*cm))
        return elementos
    
    def _criar_tabela_cenarios(self, dados: Dict[str, Any]) -> list:
        """
        Cria a tabela de cenários com diferentes classificações.
        
        Args:
            dados: Dados da API contendo informações do município
            
        Returns:
            Lista de elementos com a tabela
        """
        elementos = []
        
        # Título da seção
        elementos.append(Paragraph("Tabela de Cenários", self.estilos['subtitulo']))
        
        try:
            # Obter tabela de classificação
            tabela_classificacao = criar_tabela_total_por_classificacao(dados)
            
            # Preparar dados para a tabela PDF
            dados_tabela = [['Classificação', 'Valor Mensal', 'Valor Anual']]
            
            for _, row in tabela_classificacao.iterrows():
                classificacao = row['Classificação']
                valor_mensal = row['Valor Total']
                
                # Calcular valor anual
                try:
                    valor_numerico = currency_to_float(valor_mensal)
                    valor_anual = valor_numerico * 12
                    valor_anual_str = format_currency(valor_anual)
                except:
                    valor_anual_str = "N/A"
                
                dados_tabela.append([classificacao, valor_mensal, valor_anual_str])
            
            # Criar tabela
            tabela = Table(dados_tabela, colWidths=[4*cm, 5*cm, 5*cm])
            tabela.setStyle(TableStyle([
                # Estilo do cabeçalho
                ('BACKGROUND', (0, 0), (-1, 0), self.cores['azul_corporativo']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.cores['branco']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Estilo do corpo
                ('BACKGROUND', (0, 1), (-1, -1), self.cores['azul_claro']),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.cores['preto']),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Classificação centralizada
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Valores à direita
                
                # Bordas
                ('GRID', (0, 0), (-1, -1), 1, self.cores['azul_corporativo']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elementos.append(tabela)
            
        except Exception as e:
            print(f"Erro: Erro ao criar tabela de cenários: {e}")
            elementos.append(Paragraph(
                "Erro ao gerar tabela de cenários. Verifique os dados de entrada.",
                self.estilos['normal']
            ))
        
        elementos.append(Spacer(1, 0.5*cm))
        return elementos
    
    def _criar_secao_projecoes(self, dados: Dict[str, Any]) -> list:
        """
        Cria a seção de projeções de 12 meses.
        
        Args:
            dados: Dados da API contendo informações do município
            
        Returns:
            Lista de elementos da seção
        """
        elementos = []
        
        # Título da seção
        elementos.append(Paragraph("Projeções para 12 Meses", self.estilos['subtitulo']))
        
        try:
            # Obter tabela de classificação
            tabela_classificacao = criar_tabela_total_por_classificacao(dados)
            
            # Extrair valores para cálculos
            valor_bom = currency_to_float(
                tabela_classificacao[tabela_classificacao['Classificação'] == 'Bom']['Valor Total'].iloc[0]
            )
            valor_otimo = currency_to_float(
                tabela_classificacao[tabela_classificacao['Classificação'] == 'Ótimo']['Valor Total'].iloc[0]
            )
            valor_regular = currency_to_float(
                tabela_classificacao[tabela_classificacao['Classificação'] == 'Regular']['Valor Total'].iloc[0]
            )
            
            # Calcular projeções
            ganho_mensal = valor_otimo - valor_bom
            perda_mensal = valor_bom - valor_regular
            ganho_anual = ganho_mensal * 12
            perda_anual = perda_mensal * 12
            
            # Texto das projeções
            texto_projecoes = f"""
            <b>Cenário Otimista (Classificação "Ótimo"):</b><br/>
            • Ganho mensal estimado: <b>{format_currency(ganho_mensal)}</b><br/>
            • Ganho anual acumulado: <b>{format_currency(ganho_anual)}</b><br/><br/>
            
            <b>Cenário Pessimista (Classificação "Regular"):</b><br/>
            • Perda mensal estimada: <b>{format_currency(perda_mensal)}</b><br/>
            • Perda anual acumulada: <b>{format_currency(perda_anual)}</b><br/><br/>
            
            <b>Impacto Financeiro:</b><br/>
            A diferença entre o melhor e pior cenário pode resultar em uma variação 
            anual de até <b>{format_currency(ganho_anual + perda_anual)}</b>, demonstrando 
            a importância da manutenção e melhoria contínua dos indicadores de qualidade 
            e vínculo das equipes de APS.
            """
            
            elementos.append(Paragraph(texto_projecoes, self.estilos['normal']))
            
        except Exception as e:
            print(f"Aviso: Erro ao calcular projeções: {e}")
            elementos.append(Paragraph(
                "Projeções baseadas nos diferentes cenários de classificação disponíveis.",
                self.estilos['normal']
            ))
        
        elementos.append(Spacer(1, 0.5*cm))
        return elementos
    
    def _criar_secao_consideracoes(self) -> list:
        """
        Cria a seção de considerações finais.
        
        Returns:
            Lista de elementos da seção
        """
        elementos = []
        
        # Título da seção
        elementos.append(Paragraph("Considerações Finais", self.estilos['subtitulo']))
        
        # Texto das considerações finais baseado no template Alcobaça
        texto_consideracoes = """
        Os valores apresentados neste relatório são baseados nos critérios oficiais 
        do Ministério da Saúde e refletem o potencial financeiro da Atenção Primária 
        à Saúde do município. É importante destacar que:
        
        • Os valores podem sofrer alterações conforme atualizações das portarias ministeriais;
        • A melhoria dos indicadores de qualidade e vínculo resulta em incremento direto 
          dos recursos federais;
        • O acompanhamento contínuo dos indicadores é fundamental para maximizar o 
          financiamento;
        • Recomenda-se a implementação de estratégias de gestão focadas na qualidade 
          e fortalecimento do vínculo das equipes.
        
        Este relatório serve como ferramenta de apoio à gestão municipal, contribuindo 
        para decisões estratégicas baseadas em dados técnicos consistentes.
        """
        
        elementos.append(Paragraph(texto_consideracoes, self.estilos['normal']))
        elementos.append(Spacer(1, 1*cm))
        
        return elementos
    
    def _gerar_grafico_projecao_matplotlib(self, dados: Dict[str, Any]) -> Optional[bytes]:
        """
        Gera gráfico de projeção mensal usando matplotlib.
        
        Args:
            dados: Dados da API
            
        Returns:
            bytes: Dados da imagem PNG ou None
        """
        try:
            from utils import criar_tabela_total_por_classificacao, currency_to_float
            from datetime import datetime
            
            # Obter dados dos cenários
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
            
            # Calcular ganhos e perdas
            ganho_total = valor_otimo - valor_bom
            perda_total = valor_bom - valor_regular
            
            # Meses do ano
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            
            # Valores acumulados
            ganhos_acum = [ganho_total * (i+1) for i in range(12)]
            perdas_acum = [-perda_total * (i+1) for i in range(12)]
            
            # Criar figura matplotlib
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            fig.patch.set_facecolor('white')
            
            # Barras de ganho
            bars_ganho = ax.bar(meses, ganhos_acum, color='#1E8449', alpha=0.8, 
                              label='Ganhos Acumulados', width=0.6)
            
            # Barras de perda
            bars_perda = ax.bar(meses, perdas_acum, color='#C0392B', alpha=0.8, 
                              label='Perdas Acumuladas', width=0.6)
            
            # Linha de referência
            ax.axhline(y=0, color='#FFC300', linestyle='--', linewidth=2, 
                      label='Valor Atual', alpha=0.8)
            
            # Configurações do gráfico
            ax.set_title('Projeção Anual de Ganhos e Perdas', fontsize=14, 
                        fontweight='bold', color='#1f4e79', pad=20)
            ax.set_xlabel('Meses do Ano', fontsize=11, color='#2C3E50')
            ax.set_ylabel('Valor Acumulado (R$)', fontsize=11, color='#2C3E50')
            
            # Formatar eixo Y como moeda
            def format_currency_axis(x, pos):
                return f'R$ {x:,.0f}'
            
            from matplotlib.ticker import FuncFormatter
            ax.yaxis.set_major_formatter(FuncFormatter(format_currency_axis))
            
            # Legenda
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
            
            # Grid
            ax.grid(True, alpha=0.3)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar como bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', 
                       facecolor='white', edgecolor='none', dpi=150)
            buffer.seek(0)
            img_bytes = buffer.getvalue()
            buffer.close()
            plt.close(fig)
            
            return img_bytes
            
        except Exception as e:
            print(f"Erro ao gerar gráfico de projeção: {e}")
            return None
    
    def _gerar_grafico_barras_matplotlib(self, dados: Dict[str, Any]) -> Optional[bytes]:
        """
        Gera gráfico de barras horizontais usando matplotlib.
        
        Args:
            dados: Dados da API
            
        Returns:
            bytes: Dados da imagem PNG ou None
        """
        try:
            pagamentos = dados.get('pagamentos', [{}])[0]
            
            # Extrair dados das equipes
            equipes_dados = []
            
            # eSF
            vl_esf = pagamentos.get('vlQualidadeEsf', 0)
            if vl_esf > 0:
                equipes_dados.append({
                    'nome': 'eSF - Saúde da Família',
                    'valor': vl_esf,
                    'qtd': pagamentos.get('qtEsfHomologado', 0)
                })
            
            # eMulti
            vl_emulti = pagamentos.get('vlPagamentoEmultiQualidade', 0)
            if vl_emulti > 0:
                equipes_dados.append({
                    'nome': 'eMulti - Multiprofissionais',
                    'valor': vl_emulti,
                    'qtd': pagamentos.get('qtEmultiPagas', 0)
                })
            
            # eSB
            vl_esb = pagamentos.get('vlPagamentoEsb40hQualidade', 0)
            if vl_esb > 0:
                equipes_dados.append({
                    'nome': 'eSB - Saúde Bucal',
                    'valor': vl_esb,
                    'qtd': pagamentos.get('qtSbPagamentoModalidadeI', 0)
                })
            
            if not equipes_dados:
                return None
            
            # Preparar dados
            nomes = [eq['nome'] for eq in equipes_dados]
            valores = [eq['valor'] for eq in equipes_dados]
            cores = ['#1E8449', '#3498DB', '#5DADE2'][:len(valores)]
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
            fig.patch.set_facecolor('white')
            
            # Barras horizontais
            bars = ax.barh(nomes, valores, color=cores, alpha=0.8, height=0.6)
            
            # Adicionar valores nas barras
            for bar, valor in zip(bars, valores):
                width = bar.get_width()
                ax.text(width + max(valores) * 0.01, bar.get_y() + bar.get_height()/2, 
                       f'R$ {valor:,.0f}', ha='left', va='center', fontsize=10)
            
            # Configurações
            ax.set_title('Valores de Qualidade por Tipo de Equipe', 
                        fontsize=14, fontweight='bold', color='#1f4e79', pad=20)
            ax.set_xlabel('Valor Total (R$)', fontsize=11, color='#2C3E50')
            
            # Formatar eixo X
            def format_currency_axis(x, pos):
                return f'R$ {x:,.0f}'
            
            from matplotlib.ticker import FuncFormatter
            ax.xaxis.set_major_formatter(FuncFormatter(format_currency_axis))
            
            # Grid
            ax.grid(True, alpha=0.3, axis='x')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar como bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight',
                       facecolor='white', edgecolor='none', dpi=150)
            buffer.seek(0)
            img_bytes = buffer.getvalue()
            buffer.close()
            plt.close(fig)
            
            return img_bytes
            
        except Exception as e:
            print(f"Erro ao gerar gráfico de barras: {e}")
            return None
    
    def _salvar_bytes_como_imagem_temporaria(self, img_bytes: bytes, nome_arquivo: str) -> str:
        """
        Salva bytes de imagem em arquivo temporário.
        
        Args:
            img_bytes: Bytes da imagem PNG
            nome_arquivo: Nome do arquivo temporário
            
        Returns:
            String com caminho do arquivo temporário
        """
        if img_bytes is None:
            return None
            
        try:
            # Criar arquivo temporário
            temp_dir = tempfile.gettempdir()
            caminho_imagem = os.path.join(temp_dir, f"{nome_arquivo}.png")
            
            # Salvar bytes no arquivo
            with open(caminho_imagem, 'wb') as f:
                f.write(img_bytes)
            
            return caminho_imagem
            
        except Exception as e:
            print(f"Erro ao salvar imagem temporária: {e}")
            return None
    
    def _criar_secao_graficos(self, dados: Dict[str, Any]) -> list:
        """
        Cria a seção de gráficos do relatório.
        
        Args:
            dados: Dados da API contendo informações do município
            
        Returns:
            Lista de elementos da seção
        """
        elementos = []
        
        # Título da seção
        elementos.append(Paragraph("Análise Gráfica", self.estilos['subtitulo']))
        
        # Texto introdutório
        texto_intro = """
        Os gráficos a seguir apresentam uma visão visual das projeções financeiras 
        e distribuição de recursos por tipo de equipe, facilitando a análise e 
        tomada de decisões estratégicas.
        """
        elementos.append(Paragraph(texto_intro, self.estilos['normal']))
        elementos.append(Spacer(1, 0.3*cm))
        
        try:
            # Gráfico 1: Projeção Mensal usando matplotlib
            img_bytes_piramide = self._gerar_grafico_projecao_matplotlib(dados)
            if img_bytes_piramide:
                caminho_piramide = self._salvar_bytes_como_imagem_temporaria(
                    img_bytes_piramide, "projecao_mensal"
                )
                if caminho_piramide:
                    elementos.append(Paragraph("1. Projeção Anual de Ganhos e Perdas", 
                                             self.estilos['normal']))
                    
                    # Adicionar imagem do gráfico
                    img_piramide = Image(caminho_piramide, width=15*cm, height=9*cm)
                    elementos.append(img_piramide)
                    elementos.append(Spacer(1, 0.5*cm))
            
            # Gráfico 2: Barras Horizontais usando matplotlib
            img_bytes_barras = self._gerar_grafico_barras_matplotlib(dados)
            if img_bytes_barras:
                caminho_barras = self._salvar_bytes_como_imagem_temporaria(
                    img_bytes_barras, "valores_equipe"
                )
                if caminho_barras:
                    elementos.append(Paragraph("2. Valores de Qualidade por Tipo de Equipe", 
                                             self.estilos['normal']))
                    
                    # Adicionar imagem do gráfico
                    img_barras = Image(caminho_barras, width=15*cm, height=7.5*cm)
                    elementos.append(img_barras)
                    elementos.append(Spacer(1, 0.5*cm))
            
        except Exception as e:
            print(f"Erro ao gerar gráficos: {e}")
            elementos.append(Paragraph(
                "Gráficos não disponíveis devido a erro no processamento dos dados.",
                self.estilos['normal']
            ))
        
        return elementos
    
    def _criar_assinatura(self) -> list:
        """
        Cria a seção de assinatura do relatório.
        
        Returns:
            Lista de elementos da assinatura
        """
        elementos = []
        
        # Data atual
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        assinatura_texto = f"""
        <br/><br/>
        ____________________________________<br/>
        <b>Mais Gestor</b><br/>
        Alysson Ribeiro<br/>
        Data: {data_atual}
        """
        
        elementos.append(Paragraph(assinatura_texto, self.estilos['centro']))
        
        return elementos
    
    def gerar_relatorio_pdf(self, nome_municipio: str, dados_calculados: Dict[str, Any]) -> bytes:
        """
        Gera relatório PDF baseado no template Alcobaça.
        
        Args:
            nome_municipio: Nome do município para o relatório
            dados_calculados: Dados já processados da consulta
            
        Returns:
            bytes: Conteúdo do PDF para download
        """
        try:
            # Buffer de memória para o PDF
            buffer = io.BytesIO()
            
            # Criar documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2.5*cm,
                leftMargin=2.5*cm,
                topMargin=2.5*cm,
                bottomMargin=2.5*cm
            )
            
            # Lista de elementos do documento
            elementos = []
            
            # Adicionar seções do relatório
            elementos.extend(self._criar_cabecalho(nome_municipio))
            elementos.extend(self._criar_secao_introducao())
            elementos.extend(self._criar_secao_cenario_atual(dados_calculados))
            elementos.extend(self._criar_tabela_cenarios(dados_calculados))
            elementos.extend(self._criar_secao_graficos(dados_calculados))  # NOVO: Gráficos
            elementos.extend(self._criar_secao_projecoes(dados_calculados))
            elementos.extend(self._criar_secao_consideracoes())
            elementos.extend(self._criar_assinatura())
            
            # Construir PDF
            doc.build(elementos)
            
            # Retornar bytes do PDF
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Erro na geração do PDF: {e}")
            raise
    
    def criar_nome_arquivo(self, nome_municipio: str) -> str:
        """
        Cria nome padronizado para o arquivo PDF.
        
        Args:
            nome_municipio: Nome do município
            
        Returns:
            String com nome do arquivo
        """
        # Remover caracteres especiais e espaços
        municipio_limpo = ''.join(c for c in nome_municipio if c.isalnum() or c in (' ', '-'))
        municipio_limpo = municipio_limpo.replace(' ', '-').lower()
        
        # Data atual
        data_atual = datetime.now().strftime("%Y%m%d")
        
        return f"relatorio-financeiro-{municipio_limpo}-{data_atual}.pdf"


# Função de conveniência para uso direto
def gerar_relatorio_pdf(nome_municipio: str, dados_calculados: Dict[str, Any]) -> bytes:
    """
    Função de conveniência para gerar relatório PDF.
    
    Args:
        nome_municipio: Nome do município para o relatório
        dados_calculados: Dados já processados da consulta
        
    Returns:
        bytes: Conteúdo do PDF para download
    """
    gerador = PDFReportGenerator()
    return gerador.gerar_relatorio_pdf(nome_municipio, dados_calculados)