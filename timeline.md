Título do Prompt: Geração de Gráfico de Decisão Estratégica para Interface de Impressão
Objetivo Principal:
Desenvolver um script Python utilizando Streamlit e Plotly para gerar um painel de visualização de alto impacto. O componente principal será um gráfico de linha do tempo que ilustra uma decisão estratégica e seus dois possíveis resultados financeiros. O design deve ser "dramático" e otimizado para ser impresso diretamente da interface web do Streamlit.

Público-Alvo da Visualização:
Gestores de alto nível (prefeitos, diretores). A clareza, o impacto visual e a comunicação inequívoca da escolha são mais importantes do que a densidade de dados.

Tecnologias Requeridas:

Linguagem: Python

Bibliotecas: streamlit, plotly

Dados a Serem Utilizados:

Valores Financeiros:

'Ótimo': 12.500.000

'Bom': 10.000.000

'Regular': 7.500.000

Mapeamento de Níveis para o Eixo Y:

'Regular': 1

'Bom': 2

'Ótimo': 3

Rótulos do Eixo X:

'Situação Atual'

'Projeção 2026'

Requisitos Detalhados de Implementação (Passo a Passo):

Configuração da Aplicação Streamlit:

A página deve ter layout="wide" e um título principal apropriado, como "Encruzilhada Financeira: O Futuro do Município em 2026".

Criação da Figura Plotly:

Inicialize um objeto go.Figure.

Ponto de Partida:

Plote um único marcador grande (size=25) na coordenada ('Situação Atual', 'Bom').

O marcador deve ser da cor #FFC300 (amarelo/laranja) com uma borda preta para destaque.

Setas Direcionais:

Utilize fig.add_annotation para desenhar as setas.

Seta Otimista: Crie uma seta que parte de ('Situação Atual', 'Bom') e aponta para ('Projeção 2026', 'Ótimo'). A seta deve ser grossa (arrowwidth=4), verde (#1E8449), e ter uma ponta de seta proeminente (arrowhead=2, arrowsize=1.5).

Seta de Risco: Crie uma seta similar partindo de ('Situação Atual', 'Bom') e apontando para ('Projeção 2026', 'Regular'). A seta deve ser vermelha (#C0392B).

Anotações de Valor e Contexto:

Rótulo do Ponto de Partida: Adicione um texto acima do marcador inicial contendo "Bom" e o valor formatado ("R$ 10.00 Milhões").

Rótulo do Cenário Ótimo: Crie uma caixa de texto (bgcolor='#1E8449', texto branco) à direita do final da seta verde. O texto deve conter "Resultado Ótimo" e o valor formatado ("R$ 12.50 Milhões") em negrito e com fonte grande (size=16).

Rótulo do Cenário Regular: Crie uma caixa de texto similar (bgcolor='#C0392B', texto branco) à direita do final da seta vermelha com o texto "Resultado Regular" e o valor formatado ("R$ 7.50 Milhões").

Requisitos de Layout e Estilo ("Drama Cinematográfico"):

Template: Use o template='plotly_white' para um fundo limpo e ideal para impressão.

Legenda: A legenda deve ser removida (showlegend=False), pois as anotações já explicam os elementos.

Título: Centralizado, em negrito e com fonte grande (size=24).

Eixos:

O eixo Y deve exibir os rótulos de texto "Regular", "Bom", "Ótimo" em negrito.

O eixo X deve ter os rótulos "Situação Atual" e "Projeção 2026" em negrito.

Remova as linhas e os "tracinhos" dos eixos (showline=False, tick_params=False) para um visual mais limpo.

Dimensões e Margens: O gráfico deve ter uma altura fixa (height=600) e uma margem direita aumentada (margin=dict(r=250)) para garantir que as caixas de texto não sejam cortadas.

Saída Final Esperada:
Um único e completo script Python (.py) que gera a aplicação Streamlit com o gráfico Plotly configurado conforme todas as especificações acima. O código deve ser limpo, bem comentado e pronto para execução.