# ÉPICO BROWNFIELD: Preenchimento automático das perdas e relatórios em lote

**ID:** EPIC-AUTO-003
**Status:** Em andamento: 3.0 feita, 3.1 feita (ver `docs/analises/regras-perda-ministerio.md`)
**Prioridade:** Alta
**Branch de origem do planejamento:** `chore/limpeza-seguranca`

---

## 🎯 EPIC GOAL

O usuário deixa de **calcular e digitar** a "Perda Recurso Mensal". O sistema calcula as perdas a partir dos dados do Ministério da Saúde, com regras estimadas das respostas que o usuário já deu. Além disso, o usuário passa a poder **selecionar vários municípios e gerar vários relatórios de uma vez**.

## 👤 CONTEXTO DO USUÁRIO

- Hoje o sistema tem **um único usuário real** preenchendo (ver seção "Evidências").
- Para cada município e competência, esse usuário consulta os dados, calcula fora do sistema a perda de cada plano orçamentário, digita na `FinancialTable` e gera o PDF, **um município por vez**.
- O volume é concentrado em lotes: 85 edições em jan/2026 e 53 em out/2025, sobretudo em BA e SE. Ou seja, ele trabalha em lote, mas o sistema obriga a fazer um por vez.

## 📊 EVIDÊNCIAS (levantamento de 24/09/2026)

Script de leitura: `backend/scripts/analise_perdas_informadas.py`, que roda sobre `backend/municipios_editados.json`.

| | |
|---|---|
| Registros | 241 (209 municípios, 8 competências) |
| Perda mensal somada | R$ 114,96 mi |
| Mediana por município | R$ 125 mil/mês |
| UFs | BA 121, SE 75, outras 45 |

Padrões por posição do array (posição = ordem de `resumosPlanosOrcamentarios`):

| Plano | Preenchido | Padrão | Hipótese de regra |
|---|---|---|---|
| eSF/eAP | 96% | 47% múltiplo de R$ 4 mil | (equipes credenciadas − pagas) × valor por equipe, ou diferença de classificação de qualidade/vínculo |
| Saúde Bucal | 94% | 77% com centavos | Diferença calculada sobre valores oficiais (proporcional) |
| **eMulti** | 86% | **74% múltiplo de R$ 12 mil** | (eMulti credenciadas − pagas) × R$ 12k / 24k / 36k por modalidade |
| **ACS** | 29% | **58% múltiplo de R$ 3.242** | (ACS credenciados/teto − pagos) × R$ 3.242 |
| Demais / Manutenção / Promoção | ≤ 15% | sem padrão | Continua manual |

Outros achados:
- Nenhum município repete os mesmos valores de um mês para o outro. "Copiar o mês anterior" não serve como sugestão.
- Outliers para conferir:
  - `292740`: 18 mi/mês;
  - `354780` e `351880`: cerca de 9 mi/mês;
  - `293070_202509`: R$ 0,01;
  - `261120_202508`: R$ 21;
  - a chave `2910859_202509` tem código IBGE de 7 dígitos.
- **Bug que distorce os dados:** o autosave envia o estado anterior à última edição (ver story 3.0).

## 🔍 ESTADO ATUAL vs FUTURO

| Hoje | Futuro |
|---|---|
| Perda digitada à mão, uma linha por plano | Perda **calculada automaticamente**; o usuário só revisa e, se quiser, ajusta |
| Array posicional, sem nome do plano | Cada valor gravado com `dsPlanoOrcamentario`, a origem (regra/manual) e a regra usada |
| Sem histórico nem usuário | Histórico append-only com `usuario_id`, valor sugerido e valor final |
| Um município e um PDF por vez | Seleção de **vários municípios** com geração em lote (ZIP de PDFs) |

## 🏗️ COMPONENTES AFETADOS

- **Backend:**
  - `backend/app/services/api_client.py` (consulta ao Ministério; hoje grava um cache global a cada chamada);
  - `backend/app/services/municipios_editados.py`;
  - tabela `edicoes` (`backend/app/models/db_models.py:25-38`, já existe e não é usada);
  - `backend/app/api/endpoints/relatorios.py`;
  - `backend/app/services/relatorio_pdf.py`.
- **Frontend:**
  - `frontend/src/components/DataTable/FinancialTable.tsx`;
  - `frontend/src/hooks/useAutoSave.ts`;
  - `frontend/src/hooks/useConsultarDados.ts`;
  - `frontend/src/stores/municipioStore.ts`;
  - `frontend/src/components/Selectors/*`;
  - `frontend/src/components/Layout/Sidebar.tsx`.
- **Novos:**
  - `backend/app/services/regras_perda.py` (motor de regras);
  - endpoint de sugestão;
  - endpoint de lote;
  - tela/seletor de vários municípios.

## 📋 STORIES

### Story 3.0: Hotfix: autosave envia a última edição ✅ FEITA (commit `fix(autosave)`)
**Prioridade: fazer primeiro (perda de dados).**
- **Problema:** em `FinancialTable.tsx:71-75` e `:173-177`, `onCommit` chama `updatePerca()` e, logo em seguida, `triggerSave()`. Mas `triggerSave` (`useAutoSave.ts:73`) usa o `dadosEditados` do render anterior (closure desatualizada). Resultado: cada salvamento vai **sem a última edição**, e o PDF sai com o valor antigo.
- **Correção (implementada):** `triggerSave` e `updatePerca` leem `useMunicipioStore.getState()` no momento da chamada. A leitura é feita na chamada, e não no disparo do timer, para não salvar dados de outro município se o usuário trocar de seleção durante o debounce.
- **AC:**
  - o upsert contém o valor recém-digitado (conferir no Network);
  - várias edições dentro de 2 s geram um único envio com todas elas;
  - nada mais muda.
- É o mesmo AC 1 da story 2.4. Se esta for feita antes, marcar lá como já resolvido.

### Story 3.1: Spike: confirmar as regras contra a API do Ministério ✅ FEITA
**Resultado:** `docs/analises/regras-perda-ministerio.md`. ACS e eSF viram sugestão automática; eMulti vira sugestão guiada (o usuário escolhe quantas equipes); Saúde Bucal e demais planos continuam manuais até responder às perguntas do relatório.

**Tipo:** investigação, sem mudar o produto.
1. Para cada um dos 241 registros, consultar `https://relatorioaps-prd.saude.gov.br/financiamento/pagamento`, com os mesmos parâmetros de `api_client.py:71-80` (`coMunicipio` com 6 dígitos e `nuParcelaInicio`/`nuParcelaFim` = competência). Salvar as respostas brutas **fora do repo**, como cache local de estudo, e usar um intervalo entre as chamadas.
   - **Não** usar `ApiClient.consultar_financiamento` como está, porque ele sobrescreve `data_cache_papprefeito.json`.
2. Para cada plano, cruzar a perda informada com os quantitativos de `pagamentos`:
   - eSF: `qtEsfCredenciado`, `qtEsfHomologado`, `qtEsfPgto` e classificações;
   - eMulti: quantitativos por modalidade;
   - ACS: quantitativos de ACS;
   - Saúde Bucal: quantitativos de SB.
   Tentar regras do tipo `(credenciado − pago) × valor_unitário` e `diferença de classificação × valor`.
3. Medir, por plano, a **taxa de acerto** de cada regra: igual ao centavo, dentro de ±1% e fora. Listar os casos que não batem para conversar com o usuário.
4. **Entregável:** `docs/analises/regras-perda-ministerio.md`, com a tabela de acerto por plano, as regras aprovadas, os valores unitários encontrados (e em que portaria se baseiam, se identificável) e as perguntas para o usuário.
- **Critério para seguir:** regra com ≥ 90% de acerto entra como automática. Entre 60% e 90%, entra como sugestão destacada para revisar. Abaixo de 60%, o plano continua manual.

### Story 3.1b: Spike: eMulti limitada pelos profissionais do CNES
- Reaproveitar do repositório `maisprofissionais` os módulos `cnes_utils.py` (API CNES web, que exige o header `Referer`) e `emulti_utils.py` (Portaria 635/2023, composição fixa/variável e mapeamento de CBO).
- Para cerca de 20 municípios do histórico: T (eSF + eAP) → combinação que cobre as equipes → limitar pela CH e pelas categorias disponíveis no CNES → comparar com a perda informada.
- **Entregável:** taxa de acerto e regra final da eMulti, acrescentadas a `docs/analises/regras-perda-ministerio.md`.
- **Decisão técnica a tomar:** copiar os módulos para `backend/app/services/cnes/` ou empacotar o `maisprofissionais` como dependência.

### Story 3.2: Registro estruturado e histórico das perdas
- Gravar, para cada plano, `{dsPlanoOrcamentario, valor, origem: "regra"|"manual", regra_id, valor_sugerido}`, e não mais só o array posicional.
- Manter compatibilidade: o array atual continua sendo lido e os PDFs continuam funcionando. Migração com script que lê o JSON existente, **sem apagá-lo**.
- Histórico append-only com `usuario_id` e data. Avaliar reaproveitar a tabela `edicoes`, que já tem `usuario_id` e timestamps. A partir daí, cada aceite ou correção de sugestão vira dado para recalibrar as regras.
- Corrigir `useConsultarDados.ts:161`, que cria o array com o tamanho de todos os resumos em vez de aplicar o filtro de esfera.

### Story 3.3: Preenchimento automático na tela
- Ao consultar um município, o backend calcula as perdas com as regras aprovadas na 3.1 e a tabela já vem preenchida, sem cálculo nem digitação.
- Cada célula mostra a origem ("calculado" ou "ajustado por você") e, se o usuário alterar, o valor sugerido fica visível.
- Planos sem regra ficam em branco, destacados como "preencher manualmente".
- **AC:** para municípios do histórico, o valor calculado bate com o que o usuário havia informado, na taxa medida na 3.1.

### Story 3.4: Seleção de vários municípios
- Na sidebar, selecionar **vários municípios** (multi-select por UF, com "selecionar todos da UF") e uma competência.
- Consultar em fila, com limite de concorrência e retry, mostrando o progresso ("12 de 40").
- Mostrar uma lista/resumo com o total de perda por município e marcar os que precisam de revisão (plano sem regra, outlier, erro da API).

### Story 3.5: Relatórios em lote
- Novo endpoint, por exemplo `POST /api/relatorios/lote`, que recebe a lista de municípios, a competência e o tipo de relatório e devolve um **ZIP** com um PDF por município (nome: `{UF}_{municipio}_{competencia}.pdf`).
- Processar no servidor com limite de concorrência (o WeasyPrint é pesado). Para lotes grandes, usar um job com progresso, em vez de uma requisição síncrona longa.
- Usar as perdas calculadas e salvas das stories 3.2 e 3.3.
- **AC:**
  - um lote de 20 municípios gera 20 PDFs idênticos aos gerados individualmente;
  - uma falha num município não derruba o lote (vai para um `erros.txt` dentro do ZIP).

## ⚠️ RISCOS E MITIGAÇÃO

- **Regras erradas geram relatórios errados:** o usuário sempre revisa antes de emitir. A origem de cada valor fica visível, e as regras só entram com a taxa de acerto medida na 3.1.
- **O Ministério muda a ordem ou os nomes dos planos:** gravar por `dsPlanoOrcamentario` (3.2) em vez da posição.
- **A API do Ministério limita ou cai em consultas em lote:** fila com concorrência baixa, retry com backoff e cache por município/competência (substituindo o `data_cache_papprefeito.json` global).
- **Carga do WeasyPrint no servidor:** limite de concorrência e job assíncrono.
- **Rollback:** cada story é isolada por feature flag ou endpoint novo. O fluxo manual atual continua disponível até a 3.3 ser validada pelo usuário.

## ✅ DEFINITION OF DONE

- O usuário gera os relatórios de um lote de municípios sem digitar nenhum valor nos planos cobertos por regra.
- Os valores calculados foram conferidos contra o histórico (3.1) e contra a revisão do usuário.
- O fluxo individual atual (consulta, edição manual, PDF) continua funcionando.
- `npx tsc -b` passa, o lint não piora (hoje tem 16 erros) e há testes do motor de regras com casos reais do histórico.
