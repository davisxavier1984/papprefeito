# Revisão do frontend — 2026-09-24

Base: HEAD `0cb1594` (branch `chore/limpeza-seguranca`). Três revisões independentes, somente leitura:

1. Revisão de código das mudanças de frontend do épico 3 (`git diff 2abfccf..HEAD -- frontend`, 15 arquivos).
2. Revalidação dos 30 achados de UX do épico 2 (`docs/prd/epic-2-frontend-ux-animacoes.md`) e revisão de UX das telas novas do épico 3 (achados 31–50).
3. Validação de prontidão das stories 2.1–2.5 (task `validate-next-story`).

Caminhos relativos a `frontend/src/`, salvo indicação. As linhas valem para o HEAD `0cb1594`.

---

## 1. Revisão de código (épico 3)

Verificações: `npx tsc -p tsconfig.app.json --noEmit` → 0 erros. `npx eslint src` → 16 erros + 1 warning, todos pré-existentes (nenhum novo). Contratos front × backend conferidos (`ItemPerda`, `MunicipioEditado*.itens`, `LoteRequest`/`LoteStatus`, `PlanoSugestao`/`SugestaoResposta`, `ValorReferencia*`, rotas `/relatorios/lote*`, `/preenchimento/*`); rotas admin protegidas nos dois lados; homônimos tratados por `codigo_ibge`. A correção de closure do autosave (`9d19d19`) funciona.

### Média

| # | Achado | Onde | Correção sugerida |
|---|---|---|---|
| C1 | Edição no debounce (< 2 s) é descartada quando a tabela desmonta (troca de rota, de município/UF/competência, "Limpar Seleções"): o cleanup só faz `clearTimeout`. Confirmado. | `hooks/useAutoSave.ts:121-127` | Enviar o pendente no unmount em vez de descartar. |
| C2 | PDFs individuais saem sem a edição da janela de 2 s (ex.: "Aplicar" no preenchimento e logo "Relatório PAP Prefeito"). Confirmado. | `pages/Dashboard.tsx:27-61` | `flush()` do autosave antes de gerar. |
| C3 | Resposta atrasada da consulta: `onSuccess` grava dados de A com B já selecionado; a próxima edição salva as perdas de A em B. Plausível. | `hooks/useConsultarDados.ts:67-96` | Capturar a seleção da requisição e descartar a resposta se a seleção mudou. |
| C4 | Duplo clique em "Gerar" cria dois lotes (o botão só fica em loading depois da resposta do POST). Confirmado. | `pages/RelatoriosLote.tsx:41-48,122` | Estado `iniciando` no `loading`/`disabled`. |

### Baixa

| # | Achado | Onde |
|---|---|---|
| C5 | Campo de competência do lote não pode ser apagado: o effect repõe a última competência sempre que fica vazio. | `components/Selectors/SeletorVariosMunicipios.tsx:44-48` |
| C6 | Polling com `setInterval` + callback assíncrono: respostas fora de ordem fazem o progresso regredir; uma falha isolada faz `setLote(null)` e some com erros e download. | `pages/RelatoriosLote.tsx:51-62` |
| C7 | Lote em andamento se perde ao sair da página (estado local), embora o backend mantenha o lote. | `pages/RelatoriosLote.tsx:36` |
| C8 | Modal de preenchimento mantém planos/aviso da abertura anterior quando a nova busca falha; "Aplicar" fica habilitado. | `components/DataTable/PreenchimentoAutomatico.tsx:45-58` |
| C9 | Falha ao listar valores de referência aparece como tabela vazia e o Select de parâmetros fica vazio, sem mensagem. | `pages/Admin/ValoresReferencia.tsx:26-35` |
| C10 | Reconsulta durante o debounce: a tela passa a mostrar o valor do servidor sem a edição, e a próxima edição grava por cima. Plausível. | `hooks/useConsultarDados.ts` + `hooks/useAutoSave.ts` |

---

## 2. Revisão de UX

### 2.1 Revalidação dos 30 achados do épico 2

Resumo: 27 ainda válidos (maioria só mudou de linha), 1 resolvido (30), 1 parcial (7), 2 pioraram (1 e 29).

| # | Prior. | Story | Status | Arquivo:linha atual | Evidência |
|---|---|---|---|---|---|
| 1 | Alta | 2.2 | Válido (pior) | App.tsx:124-171; AppLayout.tsx:20-21 | 5 rotas, cada uma com seu `<AppLayout>`; a Sidebar agora navega (Sidebar.tsx:67-78), então cada clique no menu remonta a Sidebar e perde recolhimento/largura. |
| 2 | Média | 2.2 | Válido | AppLayout.tsx:81; Dashboard.tsx:101,215; App.css:24-37 | `fade-in-up` dupla, sem reduced-motion. |
| 3 | Média | 2.2 | Válido | Sidebar.tsx:252; :89-114 | Transição ativa durante o arraste. |
| 4 | Baixa | 2.2 | Válido | AppLayout.tsx:27; FinancialTable.tsx:38; index.css:42,61; App.css:40 | 760/780 × 768, listeners separados. |
| 5 | Alta | 2.3 | Válido | Dashboard.tsx:99-213 | Estado vazio durante a primeira consulta. |
| 6 | Média | 2.3 | Válido | FinancialTable.tsx:264 | Só a Table recebe `loading`. |
| 7 | Alta | 2.5 | Parcial | Sidebar.tsx:74-78, 176-185, 211-234 | Drawer só fecha quando a consulta parte de outra rota; erro só no Alert da sidebar. |
| 8 | Baixa | 2.5 | Válido | Dashboard.tsx:124 | Imagem de `gw.alipayobjects.com`. |
| 9 | Baixa | 2.5 | Válido | Admin/UserManagement.tsx:243-255 | Só `Spin`, sem estado vazio. |
| 10 | Alta | 2.4 | Válido | useAutoSave.ts:71-117,19,135; FinancialTable.tsx:230-233 | Sem estado "pendente"; `error` nunca exibido; após "Preencher automaticamente" fica "Pronto" por 2 s. |
| 11 | Alta | 2.4 | Válido | FinancialTable.tsx:227-233 | Sem `aria-live`; condição redundante continua. |
| 12 | Alta | 2.4 | Válido | FinancialTable.tsx:126 | `MobileCardView` declarado dentro do componente. |
| 13 | Média | 2.4 | Válido | FinancialTable.tsx:47-118 | Colunas recriadas; sem destaque do que mudou. |
| 14 | Alta | 2.4 | Válido | FinancialTable.tsx:113,208; MetricsCards.tsx:35,84-114 | `> 0` verde na tabela, vermelho nos cards. |
| 15 | Média | 2.2/2.3/2.5 | Válido | MetricsCards.tsx:44-190; LoginForm.tsx:43-76; RegisterForm.tsx:82-114,136-169; gradiente em Sidebar.tsx:150, AppLayout.tsx:65-72, LoginForm.tsx:147-154, RegisterForm.tsx:298-305 | Estilos duplicados. |
| 16 | Média | 2.5 | Válido | Sidebar.tsx:150; LoginForm.tsx:62,151; App.tsx:60; Header.tsx:89 | Gradientes divergentes. |
| 17 | Baixa | 2.5 | Válido | Header.tsx:145-146 | Cores fixas BA/GO. |
| 18 | Baixa | 2.5 | Válido | index.css:36-38; Header.tsx:96 | Header sem tratamento mobile. |
| 19 | Baixa | 2.3 | Válido | ProgramaCard.tsx:56-62; AnaliseBox.tsx:39-45; SaudeBucalDetalhada.tsx:13-19 | Formatadores por render. |
| 20 | Média | 2.5 | Válido | UserManagement.tsx:134,140; AppLayout.tsx:58,84 | Padding duplo; gutter sem vertical. |
| 21 | Baixa | 2.5 | Válido | Programas/SaudeBucalDetalhada.tsx | Código morto. |
| 22 | Alta | 2.5 | Válido | Header.tsx:134-136,157-159; Sidebar.tsx:264; LoginForm.tsx:87; App.tsx:47 | Contraste ≈2,8:1; o item selecionado do novo Menu também. |
| 23 | Alta | 2.4 | Válido | inputs/CurrencyInput.tsx:131-148 | Sem `aria-label` (na tabela o id já é passado: FinancialTable.tsx:71,173). |
| 24 | Média | 2.5 | Válido | Sidebar.tsx:269-277; :280-301 | Sem `aria-expanded`/`role="separator"`/teclado. |
| 25 | Baixa | 2.5 | Válido | Dashboard.tsx:111,152,266; ProgramasCards.tsx:40,69,73,76,79; AnaliseBox.tsx:57,109-125 | Emojis. |
| 26 | Baixa | 2.5 | Válido | ProgramaCard.tsx:208-215,259,275; SaudeBucalDetalhada.tsx:30,40; Header.tsx:196 (10 px) | Fontes < 12 px. |
| 27 | Média | 2.5 | Válido | index.css | Sem `:focus-visible`. |
| 28 | Baixa | 2.5 | Válido | Auth/LoginForm.tsx:146 | Hook dentro de prop JSX. |
| 29 | Média | 2.5 | Pior | dist/assets/index-4IQc32-n.js; App.tsx:13,19 | 1.391.147 bytes (+41 KB sobre 1.349.737), sem code splitting. |
| 30 | Alta | 2.4 | Resolvido (`9d19d19`) | useAutoSave.ts:74-78 | `triggerSave` lê `getState()` na chamada. Só verificação de regressão. |

### 2.2 Achados novos (telas do épico 3)

| # | Prior. | Story | Achado |
|---|---|---|---|
| 31 | Média | 2.4 | `FinancialTable.tsx:226-249` — barra "Status" + botão "Preencher automaticamente" num `Space` sem `wrap`; transborda em 375 px. |
| 32 | Média | 2.4 | `PreenchimentoAutomatico.tsx:92-93` — ao aplicar, o modal fecha sem mensagem nem destaque das linhas; status "Pronto" durante o debounce. |
| 33 | Alta | 2.5 | `PreenchimentoAutomatico.tsx:133-136` — Checkbox do plano sem rótulo acessível. |
| 34 | Média | 2.5 | `PreenchimentoAutomatico.tsx:161` — `minWidth: 300` no Checkbox de componente; transbordo em 375 px. |
| 35 | Média | 2.5 | `PreenchimentoAutomatico.tsx:119-124` — sem estado vazio; `Spin` sem texto; aviso antigo fica junto de erro novo. |
| 36 | Baixa | 2.5 | `PreenchimentoAutomatico.tsx:145,107` — "→" lido como "seta"; "plano(s)". |
| 37 | Média | 2.5 | `SeletorVariosMunicipios.tsx:75-109` — Selects só com placeholder; competência com `addonBefore` sem `<label>`. |
| 38 | Média | 2.5 | `SeletorVariosMunicipios.tsx:93` + `RelatoriosLote.tsx:89,122` — competência inválida só pinta a borda; "Gerar" desabilitado sem explicação. |
| 39 | Média | 2.5 | `SeletorVariosMunicipios.tsx:25-36` — `isError` de UFs/municípios ignorado. |
| 40 | Baixa | nova story | `SeletorVariosMunicipios.tsx:111-123` — resumo por UF só com contagem; não dá para ver/remover município de outra UF. |
| 41 | Média | 2.5 | `RelatoriosLote.tsx:128-137` — progresso sem `aria-live`/`role="status"`. |
| 42 | Média | nova story | `RelatoriosLote.tsx:36,51-62,103-124` — estado do lote local; seleção editável durante a geração. |
| 43 | Baixa | 2.5 | `RelatoriosLote.tsx:132` — `status==='erro'` com `erros` vazio mostra só a barra vermelha. |
| 44 | Baixa | 2.5 | `RelatoriosLote.tsx:123,135-136` — "Gerar 0 relatório(s)"; plural "(s)". |
| 45 | Média | 2.5 | `Admin/ValoresReferencia.tsx:114-127` — formulário só com placeholder; larguras fixas transbordam em 375 px. |
| 46 | Média | 2.5 | `Admin/ValoresReferencia.tsx:26-35` — erro da listagem vira "Sem dados" e bloqueia o cadastro sem explicação. |
| 47 | Baixa | 2.5 | `Admin/ValoresReferencia.tsx:75,84-85` — remover sem loading; coluna Valor sem unidade. |
| 48 | Média | 2.2 | `Layout/Sidebar.tsx:115-130,211-217,262-266` + `AppLayout.tsx:60-76` — navegação dentro da sidebar ainda chamada "Filtros"; itens duplicados no dropdown do Header (`Header.tsx:37-72`). |
| 49 | Baixa | 2.2 | `Sidebar.tsx:117,246-250` — Menu `inlineCollapsed` (~80 px) num Sider de 64 px com padding 8 px; possível corte (não verificado visualmente). |
| 50 | Baixa | 2.5 | `RelatoriosLote.tsx:94`, `ValoresReferencia.tsx:94` usam Title level 3 × level 2 nas demais; botão "Vários municípios" (`Dashboard.tsx:225`) não diz que leva a "Relatórios em lote". |

Pontos positivos das telas novas: textos em pt-BR, `message` nas ações, `aria-label` no InputNumber de quantidade e no botão de remover.

---

## 3. Validação das stories 2.1–2.5

Template: as cinco seguem `story-tmpl.yaml`, sem placeholders. Lint: continua 16 erros + 1 warning (linhas deslocadas). **Linha de base do bundle vencida:** hoje `index-4IQc32-n.js` = 1.391.147 bytes (o valor 1.349.737 de `index-bSt5rp5M.js` não existe mais).

| Story | Parecer | Nota |
|---|---|---|
| 2.1 Fundação motion + revisão de UX | NO-GO | 6 |
| 2.2 Transições de rota e layout | NO-GO | 5 |
| 2.3 Dashboard animado | GO com ajustes | 7 |
| 2.4 Tabela financeira e autosave | NO-GO | 4 |
| 2.5 Microinterações, desempenho, acessibilidade | NO-GO | 4 |

### 2.1
- **Crítico:** AC1 copia arquivo:linha desatualizados → reancorar no HEAD. Achado 30 resolvido em `9d19d19` → marcar "Resolvido, só regressão na 2.4". Faltam achados das telas novas → incluir 31–50 com mapeamento.
- **Deveria:** `App.tsx:104-165` → faixa atual; AC8/Task 6.3 com linha de base medida (`npx vite build --outDir /tmp/maispap-base` no HEAD antes da 2.1); roteiro manual com Menu da Sidebar, `/relatorios-lote`, `/admin/valores-referencia`; decidir `LazyMotion` + `m` já na 2.1 (a 2.5 o torna obrigatório).
- **Opcional:** AC9 "rollback testado" → "`git revert` numa branch + `tsc` + build".

### 2.2
- **Crítico:** AC1/Task 1 citam 3 rotas; hoje são 5 (`/dashboard`, `/relatorios-lote`, `/profile`, `/admin/users`, `/admin/valores-referencia`) — Task 1.2 deve envolver as duas rotas admin com `requireSuperuser`; atualizar trechos "Código atual"/"Alvo". A Sidebar tem `Menu` + `Divider` (`Sidebar.tsx:57-72,117-130`): o `Divider` entra no bloco com fade; o `Menu` do AntD usa `inlineCollapsed` e não pode ser envolvido em `motion` (Restrições). Linhas: `Sidebar.tsx:80-88`→`:132`; `:193-206`→`:243-262`; `:202`→`:252`; `FinancialTable.tsx:31-42`→`:36-45`; `App.tsx:117-150`→`:119-174`.
- **Deveria:** roteiro do AC2 pelo Menu da Sidebar (não pelo dropdown); registrar `handleConsultar`/`handleNavigate` e o exit de 150 ms com `AnimatePresence mode="wait"`; incluir `RelatoriosLote.tsx`/`ValoresReferencia.tsx` no eslint e na regressão.
- **Opcional:** "Acesso Negado" (`ProtectedRoute.tsx:44`) também em `/admin/valores-referencia`.

### 2.3
- **Deveria:** linhas `Dashboard.tsx:97`→`:99`; `:97-121`→`:99-142`; `:243-251`→`:248-268`; `useConsultarDados.ts:61-64`→`:63-64`; `:86-88`→`:101-102`; `municipioStore.ts:201-224`→`:218-240`; `:281-288`→`:298-305`; disparo da consulta em `Sidebar.tsx:75` e `CompetenciaInput.tsx:100`. Preenchimento automático muda todas as perdas de uma vez: contadores animam, stagger não se repete (AC3/AC4 + roteiro). Task 3.4 (extrair `MetricCard`) obrigatória, pois a 2.5 depende dela.
- **Opcional:** stagger em reconsulta do mesmo município (contador de consultas no store); roteiro começando em `/relatorios-lote`.

### 2.4
- **Crítico:** AC1/Task 1 já resolvidos em `9d19d19` → AC1 vira regressão; remover a Task 1.2 (contradiz a decisão do commit). AC2: o payload agora inclui `itens` → `retry()` reenvia o payload completo; não alterar a montagem de `itens`/`origem`. AC3/Task 3.3: substituir só o bloco Status (`FinancialTable.tsx:228-234`), preservando o botão "Preencher automaticamente", o contador e `onAplicado={() => triggerSave()}`. Cobrir o preenchimento em lote no AC4/AC9 (derivadas de todas as linhas alteradas piscam juntas, uma vez; indicador passa por "Alterações pendentes").
- **Deveria:** linhas do `FinancialTable.tsx` (+3 em quase todas: `:19-25`→`:21-27`, `:44-115`→`:47-118`, `:71-75`→`:74-78`, `:123-220`→`:126-223`, `:173-177`→`:176-180`, `:204-215`→`:207-218`, `:240`→`:259`); `useAutoSave.ts:71-81`→`:71-118`; diferença em `municipioStore.ts:210`; os PDFs usam `preparar_dados` em `backend/app/services/relatorios_service.py:29` (não mais `relatorios.py:33-37,104-108`). AC8 (cor da diferença) depende do PO. AC6: barra de status sem transbordo em 375 px.
- **Opcional:** o modal de preenchimento (Modal do AntD) não pode ser envolvido em `motion`.

### 2.5
- **Crítico:** AC4 (+40 KB sobre 1.349.737) já falha → "≤ 40 KB sobre a linha de base medida no início da 2.1". AC11 ("nenhuma animação em nenhuma tela") não é cumprível com o AntD → restringir a `motion`/CSS do épico ou desligar o movimento do AntD com `ConfigProvider theme={{ token: { motion: false } }}` via `useReducedMotion`. Telas novas fora do AC3/AC8/AC10 → incluir Relatórios em lote, Valores de referência, modal de preenchimento e Menu da Sidebar. AC2 já parcialmente atendido → "fechar também quando a consulta parte de `/dashboard`".
- **Deveria:** linhas da Sidebar (`:125-135`→`:175-185`, `:161-184`→`:211-234`, `:54-78`→`:89-113`, `:214`→`:264`, `:218-227`→`:268-277`, `:233-251`→`:282-300`, gradiente `:99-103`→`:141-170`), Header (`:73-85`→`:87-100`, `:117-151`→`:131-165`, `:129-140`→`:143-154`), Dashboard (`:121-139`→`:122-141`), `useConsultarDados.ts:82-88`→`:97-102`; AC7 com a navegação duplicada Header × Sidebar e a tag de 10 px (`Header.tsx:196`); AC5 com capturas das telas novas (a troca de `colorPrimary` as afeta).

### Decisões pendentes do PO
- Cor da diferença (verde × vermelho) — bloqueia a 2.4 (AC8).
- Paleta/contraste (`colorPrimary`) — bloqueia a 2.5 (AC5).
