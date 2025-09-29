# Plano de Ajuste das Margens do Relatório PDF

## Contexto
- Relatórios PDF gerados a partir de `backend/app/services/relatorio_pdf.py` usam o template `backend/templates/relatorio_base.html` com estilos em `backend/templates/css/modern-cards.css`.
- O timbrado institucional (`backend/templates/images/Imagem Timbrado.png`) ocupa a faixa superior da página e parte do rodapé, sendo necessário garantir espaço livre para que o conteúdo não o sobreponha.

## Objetivo
- Reservar área suficiente no topo das páginas para preservar o timbrado e, simultaneamente, otimizar o espaço útil para o conteúdo do relatório.

## Medidas Propostas
1. Revisar o CSS atual (`modern-cards.css`) que define `@page { margin: 0; }` e `.page { padding: 20mm; }`, identificando classes específicas por página (`.page-1`, `.page-2`, etc.).
2. Dimensionar o timbrado: a imagem possui 2000 px de altura, com a faixa superior ocupando ~330 px (~16,5% da altura, equivalente a ≈45 mm em A4). Usaremos essa medida como margem de segurança para o topo.
3. Ajustar margens e padding:
   - Definir `@page { margin: 12mm 10mm 12mm 10mm; }` para introduzir margem superior sem comprometer laterais.
   - Aumentar `padding-top` para 45 mm na classe `.page` ou, se apenas a primeira página usar o timbrado completo, aplicar `padding-top: 45mm` somente em `.page-1` e manter ~25 mm nas demais.
   - Compensar espaço reduzindo `padding-bottom` para ~18 mm, garantindo maior área útil para o corpo do documento.
4. Ajustar espaçamentos internos: caso o primeiro bloco de conteúdo (ex.: `.financial-cards`) fique muito próximo do novo topo, aplicar `margin-top: 8mm` ou valor similar para preservar a hierarquia visual.
5. Testar variações caso existam páginas com menos conteúdo (assinaturas) para garantir consistência visual usando seletores como `.page-3`.

## Validação
- Regenerar o PDF com WeasyPrint e comparar com a versão anterior observando:
  - Timbrado totalmente visível e sem sobreposição de elementos.
  - Cards, gráficos e tabelas dentro da área útil ajustada.
  - Ganho perceptível de espaço inferior que compense a área reservada no topo.
- Executar checklist de testes visuais já descrito em `docs/gerador-pdf-documentacao.md`, adicionando a verificação específica das margens superiores.

## Documentação e Follow-up
- Atualizar `docs/gerador-pdf-documentacao.md` com os novos valores de margem/padding e o racional do cálculo (reserva de 45 mm).
- Registrar na documentação quaisquer ajustes adicionais realizados (por exemplo, aplicação de estilos diferenciados em páginas específicas).
- Após validação, comunicar à equipe de desenvolvimento e design para alinhamento e coletar feedback sobre a nova distribuição do espaço.
