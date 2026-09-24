# ÉPICO BROWNFIELD: Preenchimento automático das perdas e relatórios em lote

**ID:** EPIC-AUTO-003
**Status:** ✅ Concluído (3.0 a 3.6). Pendências de uso: cadastrar os valores de referência de 2026 e validar no navegador (ver `docs/analises/regras-perda-ministerio.md`)
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

### Story 3.1b: Spike: eMulti limitada pelos profissionais do CNES ✅ FEITA
- Os módulos do `maisprofissionais` foram **copiados** para `backend/app/services/cnes/`: `cnes_client.py` (API CNES web, adaptado de requests para httpx) e `emulti_regras.py` (Portaria 635/2023 + `avaliar_modalidade`).
- **Resultado:** hipótese rejeitada. 82 de 85 municípios têm profissionais suficientes, e nenhuma regra fixa passa de 14% de acerto. A eMulti vira **sugestão guiada** na 3.3: o usuário escolhe quantas equipes a mais e o sistema calcula. Detalhes em `docs/analises/regras-perda-ministerio.md`.
- Script: `backend/scripts/estudo_emulti_cnes.py`.

### Story 3.2: Registro estruturado e histórico das perdas ✅ FEITA
- **Backend:**
  - `MunicipioEditado`/`Create`/`Update` ganham `itens` opcionais (`ItemPerda`: `plano`, `valor`, `origem` manual|regra|estimativa, `regra_id`, `valor_sugerido`). Os itens precisam ter o mesmo tamanho e os mesmos valores de `perda_recurso_mensal` (senão 422).
  - O array posicional continua sendo a fonte dos PDFs, então nada muda para o fluxo atual.
  - Um `PUT` sem itens remove os itens antigos, para não ficarem descrevendo valores que mudaram.
  - Nova tabela append-only `historico_perdas` (`HistoricoPerdaDB`), criada pelo `create_all` sem tocar nas tabelas existentes. Cada create/update/upsert/delete grava usuário, operação, valores e itens (`app/services/historico_perdas.py`). Uma falha no histórico é logada e não impede a gravação.
  - Nova rota `GET /api/municipios-editados/{ibge}/{competencia}/historico`.
- **Frontend:**
  - O autosave envia `itens` com o nome de cada plano (origem `manual`) quando a tabela e o array têm o mesmo tamanho.
  - `useConsultarDados` passa a criar o array de zeros só com os planos municipais, com o filtro compartilhado `filtrarResumosMunicipais`.
- **Migração:** `backend/scripts/migrar_itens_perda.py` rotula 235 dos 241 registros com o nome do plano, usando o cache do Ministério. Por padrão só gera `<arquivo>.com_itens.json`; com `--aplicar`, faz backup e substitui. **Ainda não foi aplicada** nos dados de produção.
- **Testado** em processo com cópia dos dados: formato antigo compatível, itens incoerentes → 422, histórico com usuário, rota sem token → 403, JSON manteve as 241 entradas.

### Story 3.3: Preenchimento automático na tela (regras definidas em entrevista) ✅ FEITA
**Implementado:**
- Backend:
  - `app/services/regras_perda.py` (motor de regras);
  - `app/services/valores_referencia.py` e a tabela `valores_referencia`, com os valores de 2025 gravados na inicialização;
  - rotas `GET /api/preenchimento/{ibge}/{comp}/sugestao` (só calcula) e `GET|POST|DELETE /api/preenchimento/valores-referencia` (escrita só para administrador).
- Frontend:
  - botão "Preencher automaticamente" na tabela, com a tela de revisão `PreenchimentoAutomatico.tsx`;
  - o autosave mantém a origem `regra` enquanto o valor não muda, e `manual` com `valor_sugerido` depois de um ajuste;
  - tela de administração `/admin/valores-referencia`.
- A digitação manual funciona como antes: sem clicar no botão, nada muda. Após aplicar, qualquer célula continua editável.
- **Mudança em relação à entrevista:** a meta de eSB novas é uma por eSF (credenciadas + novas), e não o teto de eSB, porque explicou melhor o histórico.

**Especificação completa:** `docs/analises/regras-preenchimento-completo.md` (entrevista de 24/09/2026).
- **Princípio:** estimar o que o município **poderia ter** a partir do que o Ministério informa, e não reproduzir valores antigos.
- Botão **"Preencher automaticamente"** no Dashboard. Nada é sobrescrito sem o usuário pedir, e ele revisa antes de salvar.
- **eSF:** ganho até ÓTIMO nas equipes pagas + equipes novas (até 2 faltando: todas; mais: ⌈diferença ÷ 3⌉). Campo para a constante R$ 14.058 (padrão 0 vezes).
- **ACS:** (teto − pagos) × valor por ACS.
- **Saúde Bucal:** qualidade até ÓTIMO + eSB novas até o teto + SESB (se ≤ 20 mil hab. e ainda não recebe). UOM, LRPD e CEO como opcionais.
- **eMulti:** via módulo da story 3.6 (opcional).
- Demais planos: zero, destacados.
- **Tabela de valores de referência por competência** (tela de administração), com 2025 já preenchido. Os valores de 2026 são cadastrados pelo usuário.
- Cada valor preenchido é gravado com `origem: "regra"`, `regra_id` e `valor_sugerido` (3.2).
- **AC:**
  - para municípios do histórico, a Saúde Bucal calculada com os mesmos componentes bate com o valor informado, como medido na análise;
  - nenhum valor salvo muda sem o usuário clicar em "Preencher" e salvar;
  - uma competência sem valores cadastrados usa a vigência anterior e avisa.

### Story 3.4: Seleção de vários municípios para relatórios ✅ FEITA
**Implementado:** página `/relatorios-lote` (`frontend/src/pages/RelatoriosLote.tsx`), com acesso pelo menu do usuário ("Relatórios em lote") e pelo botão "Vários municípios" no Dashboard. Seleção acumulada entre UFs, "selecionar todos da UF", competência, tipos, opção para municípios sem perdas e conferência (`POST /api/relatorios/lote/conferencia`). A opção "calcular pelas regras" (padrão) calcula as perdas dos municípios sem perdas salvas com o motor da 3.3, salva com origem `regra` e registra no histórico. A eMulti fica zerada.

**Objetivo (definido pelo usuário):** selecionar vários municípios de uma vez para **gerar os relatórios**, escolhendo o tipo: **"Relatório PAP Prefeito"** (`/relatorios/pdf`) ou **"Relatório Detalhado"**/completo (`/relatorios/pdf-detalhado`).
- Nova tela "Relatórios em lote", separada do Dashboard atual, que continua igual. Nela:
  - UF → municípios, com multi-select, "selecionar todos da UF" e busca;
  - competência;
  - tipo de relatório (Prefeito, Detalhado ou ambos).
- Antes de gerar, uma lista de conferência por município: perdas salvas? (sim/não/parcial), total da perda mensal, origem dos valores (manual/regra/estimativa) e avisos (sem perdas salvas, outlier, erro na consulta ao Ministério).
- Os municípios sem perdas salvas podem: (a) ficar de fora, (b) usar as regras da 3.3/3.6 se o usuário marcar essa opção, ou (c) sair com perda zero, e nesse caso o relatório avisa. Padrão: (a).

### Story 3.5: Geração dos relatórios em lote ✅ FEITA
**Implementado:**
- `app/services/relatorios_service.py`: preparação e renderização compartilhadas com as rotas individuais.
- `app/services/relatorios_lote.py`: job em segundo plano, com 3 consultas simultâneas ao Ministério e renderização em thread, uma por vez.
- Rotas: `POST /api/relatorios/lote` (202), `GET /api/relatorios/lote/{id}` e `GET /api/relatorios/lote/{id}/download`. Cada lote só é visível para o usuário que o criou.
- O estado dos lotes fica em memória (se o backend reiniciar, os lotes em andamento se perdem), e os ZIPs são apagados depois de 6 h.

**Testado:** o texto dos PDFs do lote é idêntico ao dos individuais (`pdftotext`, Prefeito e Detalhado). As rotas individuais geram o mesmo texto antes e depois da refatoração. Município sem perdas → aviso no `erros.txt`, sem token → 403, lote de outro id → 404.

- Novo endpoint `POST /api/relatorios/lote` com `{municipios: [...], competencia, tipos: ["prefeito"|"detalhado"]}`. Devolve um **ZIP** com um PDF por município e tipo (`{UF}_{municipio}_{competencia}_{tipo}.pdf`).
- Reaproveitar as funções que já geram os PDFs individuais (`relatorios.py` e `relatorio_pdf.py`), sem duplicar layout.
- Processar no servidor com limite de concorrência (o WeasyPrint é pesado). Para lotes grandes, usar um job assíncrono com progresso na tela ("12 de 40"), em vez de uma requisição síncrona longa.
- **AC:**
  - um lote de 20 municípios gera PDFs idênticos aos gerados individualmente;
  - uma falha num município não derruba o lote (vai para um `erros.txt` dentro do ZIP);
  - o tipo escolhido é respeitado.

### Story 3.6: Módulo opcional "Estimativa eMulti" (substitui o cálculo manual do usuário) ✅ FEITA
**Implementado:**
- Backend:
  - `app/services/emulti_estimativa.py`: estimativa com cache do CNES de 12 h e aplicação;
  - rotas `GET /api/preenchimento/emulti/{ibge}/{comp}/estimativa?divisor=` (só calcula) e `POST /api/preenchimento/emulti/aplicar`, que grava só a posição da eMulti com `origem: "estimativa"`, mantém as outras posições e registra no histórico;
  - custeios, qualidade BOM e divisor ficam nos valores de referência.
- Frontend:
  - página `/estimativa-emulti` (menu do usuário e atalho na tela de preenchimento), com vários municípios, progresso, combinação editável (E/C/A), qualidade BOM opcional, detalhe dos profissionais por categoria, aplicação em lote com confirmação e exportação CSV;
  - o seletor de vários municípios foi extraído para `components/Selectors/SeletorVariosMunicipios.tsx`, que os relatórios em lote também usam.
- **Testado:** em 290240 e 291420 (202512), a estimativa bateu exatamente com o valor informado pelo usuário (12.000 e 24.000). Aplicar alterou só a posição da eMulti, e um município inválido não afetou os outros.

**Contexto:** o usuário estima a quantidade de eMulti a partir dos **profissionais elegíveis existentes** no município. **Decisão: a estimativa não usa carga horária, só a quantidade de profissionais.** Calibrado nos 85 municípios do histórico, o estimador abaixo acerta a perda exatamente em 16% dos casos e dentro de ±1 equipe (±12 mil) em 39%, contra ≤14% das regras só por nº de equipes. É o melhor ponto de partida, desde que **transparente e revisável**.

**Módulo próprio e opcional:**
- Tela separada "Estimativa eMulti". Nada muda na tabela até o usuário **aplicar** a estimativa.
- Funciona para **um ou vários municípios** (mesma seleção da 3.4), e as estimativas aplicadas alimentam os relatórios em lote.

**Cálculo por município** (backend `app/services/emulti_estimativa.py`, usando `app/services/cnes/`), **sem carga horária**:
1. **Equipes vinculáveis (T):** eSF + eAP credenciadas (Ministério), comparadas com as ativas no CNES.
2. **eMulti atuais:** pagas (Ministério) e cadastradas no CNES.
3. **Profissionais elegíveis (P):** pessoas distintas no CNES nas categorias da Portaria 635/2023 (composição fixa + variável, com o mapeamento de CBO de `emulti_regras`).
4. **Número de eMulti possíveis** = mínimo entre:
   - **T** (cada eMulti vincula ao menos uma eSF/eAP);
   - **P ÷ 6**, uma equipe a cada 6 profissionais elegíveis. O divisor 6 foi o melhor na calibração (5 dá mais acertos aproximados, 6–7 mais acertos exatos) e fica ajustável na tela;
   - **nutricionistas + psicólogos**, a composição fixa mínima da Estratégica.
5. **Combinação sugerida:** o número de equipes do passo 4, em Estratégicas (R$ 12 mil). Na tela, o usuário pode converter em Complementar/Ampliada, respeitando as faixas da Portaria (5–9 e 10–12 eSF/eAP) e o teto do Ministério.
6. **Perda** = custeio da combinação − custeio atual, com a opção de incluir a qualidade BOM (+18,75%).

**Tela:**
- Por município: T, eMulti atuais, quadro de profissionais elegíveis (categoria e pessoas), combinação sugerida e valor.
- Botões "Aplicar" (grava na posição da eMulti com `origem: "estimativa"`, `regra_id` e `valor_sugerido`, via 3.2) e "Ajustar".
- No modo lote: tabela com todos os municípios selecionados, estimativa de cada um, "aplicar em todos" ou por linha, e exportação para planilha (como no `maisprofissionais`).

**Aprendizado:** cada aplicação ou ajuste fica no histórico da 3.2. Com isso dá para recalibrar o divisor (profissionais por equipe) e a preferência de combinação por porte de município.

**AC:**
- a estimativa de um município mostra os profissionais usados no cálculo;
- aplicar grava com origem `estimativa` e aparece no histórico;
- sem aplicar, nada muda nos dados;
- a estimativa em lote de 20 municípios termina com progresso visível;
- uma falha do CNES num município não impede os outros.

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
