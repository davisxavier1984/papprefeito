# ÉPICO BROWNFIELD: Refinamento de UX/UI e Animações do Frontend

**ID:** EPIC-UX-002
**Título:** Revisão de UX/UI e introdução de animações com `motion` no frontend MaisPAP
**Responsáveis:** PM / UX Expert / SM
**Status:** Draft
**Prioridade:** Média-Alta
**Data:** 2026-09-24

---

## 🎯 EPIC GOAL

Corrigir os problemas concretos de UX/UI identificados no frontend do Sistema MaisPAP (consistência visual, estados de carregamento/vazio/erro, responsividade, acessibilidade e feedback de ações) e introduzir animações curtas e discretas com a biblioteca `motion` (antigo framer-motion, import de `'motion/react'`), respeitando `prefers-reduced-motion`, sem alterar nenhuma regra de negócio nem o fluxo de consulta, edição com autosave, geração de PDF, login e administração.

## 📊 BUSINESS VALUE

### Para gestores municipais e consultores (usuários finais)
- Percepção imediata de que a consulta está em andamento (skeletons) e de que a edição foi salva (indicador de autosave claro).
- Leitura mais rápida dos números principais (entrada escalonada dos cards, contadores em R$ com formatação pt-BR).
- Menos erros "invisíveis": hoje, no celular, o erro de consulta fica escondido dentro do Drawer fechado.

### Para o sistema / produto
- Aparência mais profissional e coesa nas apresentações a prefeitos.
- Base de tokens de movimento (`src/theme/motion.ts`) reutilizável, evitando estilos/animações duplicados.
- Melhor acessibilidade (WCAG 2.1 AA como alvo: contraste, rótulos, foco visível, movimento reduzido).

## 🔍 CURRENT STATE vs FUTURE STATE

### Estado atual — achados da revisão de UX/UI (arquivo:linha, caminhos relativos a `frontend/src/`)

**Arquitetura de layout e navegação**
1. `App.tsx:118-150` — cada rota protegida instancia seu próprio `<AppLayout>`. Ao navegar entre `/dashboard`, `/profile` e `/admin/users`, Header e Sidebar são desmontados e remontados: o estado da sidebar (`sidebarCollapsed`, `sidebarWidth` em `components/Layout/AppLayout.tsx:20-21`) é perdido e a animação `fade-in-up` roda de novo na página inteira.
2. `components/Layout/AppLayout.tsx:81` e `pages/Dashboard.tsx:99,214` — a classe `fade-in-up` é aplicada em dois níveis aninhados (Content + página), gerando animação dupla; a keyframe em `App.css:24-37` ignora `prefers-reduced-motion`.
3. `components/Layout/Sidebar.tsx:202` — `transition: 'width 0.2s ease'` também se aplica enquanto o usuário arrasta a borda de redimensionamento (`Sidebar.tsx:54-78`), causando atraso ("borracha") no arraste.
4. Breakpoints inconsistentes: `AppLayout.tsx:27` usa 760/780 px com histerese, `DataTable/FinancialTable.tsx:35` usa 768 px, `index.css:42` e `App.css:40` usam 768 px, e cada componente registra seu próprio listener de `resize`.

**Estados de carregamento, vazio e erro**
5. `pages/Dashboard.tsx:97-211` — durante a primeira consulta (`isLoading` verdadeiro e ainda sem dados) o usuário continua vendo o estado vazio "Nenhum dado carregado ainda"; não há skeleton nem indicação na área principal.
6. Em uma reconsulta (dados já carregados), `MetricsCards`, `ProgramasCards` e `AnaliseBox` continuam exibindo os números antigos sem nenhum indicador; só a tabela recebe `loading` (`FinancialTable.tsx:245`).
7. `components/Layout/Sidebar.tsx:125-135` — o erro de consulta só é exibido dentro da sidebar; no mobile ela é um Drawer (`Sidebar.tsx:161-184`) que pode estar fechado, e o erro não aparece em lugar nenhum. O Drawer também não fecha após consulta bem-sucedida.
8. `pages/Dashboard.tsx:122` — a imagem do estado vazio vem de um CDN externo (`gw.alipayobjects.com`), dependência externa desnecessária (falha offline/CSP); o Ant Design já oferece `Empty.PRESENTED_IMAGE_SIMPLE`.
9. `pages/Admin/UserManagement.tsx:243-255` — `Spin` apenas no primeiro carregamento; sem estado vazio específico ("nenhum usuário encontrado com esses filtros").

**Feedback de ações (tabela financeira e autosave)**
10. `hooks/useAutoSave.ts:71-93` — entre a edição e o fim do debounce de 2 s não existe estado "alterações pendentes"; o indicador em `FinancialTable.tsx:227-230` mostra "Pronto" enquanto há dados não salvos. O estado `error` do hook (`useAutoSave.ts:19,110`) nunca é exibido, e não há ação de "tentar novamente".
11. `FinancialTable.tsx:226-230` — o indicador de status não tem `aria-live`, então leitores de tela não anunciam "Salvando/Salvo/Erro". A condição `isSaved && status === 'saved'` é redundante.
12. `FinancialTable.tsx:123-220` — `MobileCardView` é um componente declarado dentro do corpo de `FinancialTable`; a cada render ele é uma nova função, o React desmonta e remonta todos os cards (e os `CurrencyInput`) a cada alteração do store ou do status do autosave — no celular, um input em digitação pode perder foco e rascunho quando o salvamento de outra linha termina. Qualquer animação de entrada rodaria novamente a cada edição.
13. `FinancialTable.tsx:44-115` — as colunas dependem de `dadosProcessados` e são recriadas a cada edição; após salvar uma perda não existe nenhum destaque visual de quais valores derivados (Potencial, Diferença) mudaram.

**Consistência visual e hierarquia**
14. Semântica de cor contraditória: em `Metrics/MetricsCards.tsx:35,84-114` diferença anual `> 0` é "Perda" (vermelho), enquanto em `FinancialTable.tsx:110` e `:205` diferença `> 0` é `success` (verde).
15. Estilos inline duplicados em massa: os 4 cards de `MetricsCards.tsx:44-190` repetem o mesmo bloco (ícone circular 32 px, gradiente, borda); o fundo/overlay/card de `Auth/LoginForm.tsx:43-76` é copiado duas vezes em `Auth/RegisterForm.tsx:82-114` e `:136-169`; o botão com gradiente aparece em `Sidebar.tsx:99-103`, `AppLayout.tsx:65-72`, `LoginForm.tsx:147-154` e `RegisterForm.tsx:298-305`.
16. Gradientes diferentes para a "mesma" marca: `#0ea5e9 → #0284c7` (`Sidebar.tsx:100`, `index.css:13-14`) versus `#0ea5e9 → #06b6d4` (`LoginForm.tsx:62,151`). O token `Layout.headerBg` em gradiente (`App.tsx:58`) não é usado, pois o Header força `background: '#fff'` (`Layout/Header.tsx:75`).
17. `Layout/Header.tsx:131-132` — cor da tag de UF fixa para BA/GO (`#1e40af`/`#16a34a`) e cinza para as demais 25 UFs, sem significado para o usuário.
18. `index.css:36-38` — `.header-logo` com `max-height: 80px` dentro de um header de `74px` (`Header.tsx:82`); no mobile o Header não esconde tags nem o nome do usuário, podendo transbordar.
19. Formatadores `Intl.NumberFormat` recriados em cada render em `Programas/ProgramaCard.tsx:56-62`, `Programas/AnaliseBox.tsx:39-45` e `Programas/SaudeBucalDetalhada.tsx:13-19`, divergindo dos formatadores de módulo usados em `MetricsCards.tsx:11-21` e `FinancialTable.tsx:19-25`.
20. `pages/Admin/UserManagement.tsx:134` — `padding: 24px` somado ao padding do `Content` (`AppLayout.tsx:84`) → recuo duplo; `Row gutter={16}` (`:140`) sem gutter vertical deixa os cards colados no mobile.
21. `Programas/SaudeBucalDetalhada.tsx` não é importado em nenhum lugar (código morto) e usa `Collapse.Panel`, API depreciada no Ant Design 5.

**Acessibilidade**
22. Contraste: texto branco sobre `#0ea5e9` (botões primários, tag do município em `Header.tsx:120-122`) tem razão ≈ 2,8:1 e sobre `#22c55e` (tag de competência, `Header.tsx:143-145`) ≈ 2,3:1 — abaixo de 4,5:1 (WCAG AA). O mesmo vale para títulos em `#0ea5e9` sobre branco (`LoginForm.tsx:87`, `Sidebar.tsx:214`).
23. `inputs/CurrencyInput.tsx:131-148` — os inputs de perda da tabela não têm `aria-label` nem rótulo associado; o `id` padrão `'currency-input'` (`:133`) gera ids duplicados se o prop não for passado.
24. `Sidebar.tsx:218-227` — botão de recolher só com ícone e `title` (sem `aria-label`/`aria-expanded`); a borda de redimensionamento (`:233-251`) só funciona com mouse (sem `role="separator"`, sem teclado).
25. Emojis em títulos (`Dashboard.tsx:109,150,261`, `ProgramasCards.tsx:40,69`, `AnaliseBox.tsx:57,109-125`) são lidos por leitores de tela ("prédio clássico", "prancheta"…) e competem com a hierarquia visual.
26. Fontes de 11 px em `ProgramaCard.tsx:208-215,259,275` e `SaudeBucalDetalhada.tsx:30,40` prejudicam a legibilidade.
27. `index.css` não define estilo de `:focus-visible`; a navegação por teclado depende apenas do padrão do Ant Design, e o `outline` some em elementos customizados (ex.: passos do Dashboard).
28. `Auth/LoginForm.tsx:146` chama o hook `useAuthStore(...)` dentro de uma prop JSX (funciona, mas foge do padrão de hooks e dificulta manutenção).

**Desempenho**
29. O bundle de produção tinha ~1,35 MB sem code splitting quando este achado foi escrito; o valor exato (1.349.737 bytes) não existe mais desde a revisão de 2026-09-24 e não deve ser usado como referência — a story 2.1 mede uma nova linha de base no HEAD atual antes de qualquer mudança do épico. Qualquer biblioteca nova precisa ser carregada de forma enxuta (`LazyMotion` + `domAnimation` + componente `m`).

**Integridade do autosave (bug encontrado durante a revisão)**
30. **Resolvido** em `9d19d19` — `triggerSave` (`hooks/useAutoSave.ts:78-118`, leitura da store em `:85`) já lê `useMunicipioStore.getState()` no momento da chamada, em vez do `dadosEditados` capturado no render anterior (closure desatualizada). Os defeitos decorrentes desse bug (edição perdida ao trocar de rota/município antes do fim do debounce; PDF sem a última edição; reconsulta sobrescrevendo edição em andamento) foram corrigidos na branch `fix/revisao-frontend` via a fila de autosave (`utils/filaSalvamento.ts`, commits `4c78e91`/`a14fe66`/`6118e28`). A story 2.4 mantém só a validação da regressão (Network) — texto original do achado preservado no histórico de `docs/qa/assessments/epic-2-ux-review.md` (achado 30).

Achados 31–50 (telas novas do épico 3 — relatórios em lote, preenchimento automático, valores de referência) e a reanálise completa dos achados 1–30 no HEAD atual estão em `docs/qa/assessments/epic-2-ux-review.md`.

### Estado futuro
- Layout persistente entre rotas (rota de layout com `<Outlet />`) e transição suave apenas da área de conteúdo (`AnimatePresence` com `location.pathname` como key).
- Tokens de movimento centralizados em `src/theme/motion.ts` (durações de 150–300 ms, easings, variants) e `MotionConfig reducedMotion="user"` na raiz; animações CSS legadas também respeitam `prefers-reduced-motion`.
- Dashboard com skeletons durante a consulta, entrada escalonada dos cards, contadores numéricos animados em R$ (pt-BR) e barras de progresso animadas.
- Autosave enviando sempre o valor atual (correção do achado 30).
- Tabela financeira com destaque sutil de linha/célula alterada (sem roubar foco nem animar o input em edição), indicador de autosave com estados "Alterações pendentes → Salvando → Salvo / Erro (tentar novamente)", anunciado via `aria-live`.
- Microinterações discretas (hover/press), estados vazios e de erro consistentes e animados, correções de acessibilidade e checagem de impacto no bundle.

## 🏗️ ARCHITECTURE INTEGRATION

### Stack atual (de `frontend/package.json`)
React 19.1, Vite 7, TypeScript ~5.8, Ant Design 5.27, Zustand 5, TanStack React Query 5, React Router DOM 7.9. Nova dependência: `motion` (imports exclusivamente de `'motion/react'`).

### Componentes afetados
| Arquivo (em `frontend/src/`) | Stories |
| --- | --- |
| `App.tsx`, `main.tsx` | 2.1, 2.2 |
| `theme/motion.ts` (novo) | 2.1 |
| `App.css`, `index.css` | 2.1, 2.5 |
| `components/Layout/AppLayout.tsx`, `Sidebar.tsx`, `Header.tsx` | 2.2, 2.5 |
| `components/Auth/LoginForm.tsx`, `RegisterForm.tsx` | 2.2 |
| `pages/Dashboard.tsx` | 2.3, 2.5 |
| `components/Metrics/MetricsCards.tsx` | 2.3 |
| `components/Programas/ProgramasCards.tsx`, `ProgramaCard.tsx`, `ProgressBar.tsx`, `AnaliseBox.tsx` | 2.3 |
| `components/common/AnimatedNumber.tsx` (novo, sugerido) | 2.3 |
| `components/DataTable/FinancialTable.tsx` | 2.4 |
| `hooks/useAutoSave.ts` | 2.4 |
| `components/inputs/CurrencyInput.tsx` | 2.4 (somente atributos de acessibilidade) |
| `components/common/SaveStatusIndicator.tsx` (novo, sugerido) | 2.4 |
| `pages/Admin/UserManagement.tsx` | 2.5 |

### Pontos de integração que NÃO mudam
- `hooks/useConsultarDados.ts` (fluxo de consulta) e `stores/municipioStore.ts` (cálculos) — apenas leitura de `isLoading`/`error`.
- Contrato de `useAutoSave`: `triggerSave`, debounce de 2000 ms e payload `MunicipioEditadoCreate` permanecem iguais; só são **adicionados** campos de status.
- Serviços `services/api.ts`, `authService`, `userManagementService`, endpoints de PDF.
- Backend: sem mudanças.

## 📋 USER STORIES

| Story | Arquivo | Resumo |
| --- | --- | --- |
| 2.1 | `docs/stories/2.1.fundacao-motion-e-revisao-ux.md` | Registrar achados priorizados, instalar `motion`, criar `src/theme/motion.ts`, `MotionConfig` no App, reduced-motion (inclusive CSS legado). |
| 2.2 | `docs/stories/2.2.transicoes-rota-e-layout.md` | Layout persistente, transições entre rotas com `AnimatePresence`, sidebar colapsando com animação, entrada do Login/Registro. |
| 2.3 | `docs/stories/2.3.dashboard-animado.md` | Entrada escalonada de MetricsCards/ProgramasCards, contador animado em R$, ProgressBar animada, skeletons na consulta. |
| 2.4 | `docs/stories/2.4.feedback-tabela-financeira.md` | Destaque sutil da linha/célula editada, indicador de autosave (pendente/salvando/salvo/erro), transições no mobile. |
| 2.5 | `docs/stories/2.5.microinteracoes-e-acessibilidade.md` | Microinterações, estados vazios/erro animados, desempenho do bundle (`LazyMotion`), acessibilidade e regressão final. |

Ordem: 2.1 → 2.2 → (2.3 ∥ 2.4) → 2.5.

## 🔒 COMPATIBILITY REQUIREMENTS

- [ ] Consulta de município (UF → município → competência → "Consultar Dados") funciona exatamente como hoje.
- [ ] Edição de "Perda Recurso Mensal" com `CurrencyInput` (Enter confirma, Esc cancela, blur confirma) e autosave com debounce de 2 s continuam iguais; nenhuma animação move, re-monta ou tira o foco do input em edição.
- [ ] Geração dos PDFs "Relatório PAP Prefeito" e "Relatório Detalhado" continua igual (mesmos nomes de arquivo e mensagens).
- [ ] Login, registro, logout, rota protegida e página de administração de usuários continuam funcionando.
- [ ] Nenhuma mudança de API/backend; nenhuma mudança nos cálculos do `municipioStore`.
- [ ] Com `prefers-reduced-motion: reduce`, nenhuma animação de deslocamento/escala/contagem é executada (no máximo fades instantâneos).
- [ ] Nenhuma nova falha de `npx tsc -b`; lint não piora além dos 16 erros pré-existentes.
- [ ] `frontend/dist` (servido em produção) **não** é sobrescrito durante o desenvolvimento: builds de verificação usam `npx vite build --outDir /tmp/...`.

## 🚨 RISKS & MITIGATION

| Risco | Mitigação |
| --- | --- |
| Animação interferir na digitação na tabela (perda de foco, re-mount, salto de layout) | Proibido animar `CurrencyInput`/célula em foco; sem `layout` animations dentro da `Table`; destaque apenas por cor de fundo/opacidade; extrair `MobileCardView` para fora do componente antes de animar. |
| Aumento do bundle (~1,35 MB hoje) | `LazyMotion` + `domAnimation` + componente `m`; medir tamanho antes/depois em build separado; orçamento: no máximo +40 KB (min+gzip ≈ +15 KB). |
| Usuários sensíveis a movimento | `MotionConfig reducedMotion="user"` + `useReducedMotion` nos contadores/efeitos imperativos + `@media (prefers-reduced-motion: reduce)` no CSS. |
| Conflito com animações internas do Ant Design (Drawer, Modal, Dropdown) | Não envolver componentes de overlay do AntD com `motion`; animar apenas wrappers próprios. |
| Refatorar rotas quebrar `ProtectedRoute`/superusuário | Story 2.2 mantém `ProtectedRoute` e `requireSuperuser` com testes manuais de cada rota. |
| Sobrescrever `frontend/dist` usado em produção | Proibido `npm run build` na pasta; build de verificação sempre com `--outDir /tmp/...`. |

### Rollback
- Cada story é um commit/PR isolado; reverter o commit restaura o comportamento anterior.
- Rollback global: remover `MotionConfig`/`LazyMotion` de `App.tsx`, reverter os componentes e executar `npm uninstall motion`. Como nenhuma API ou dado muda, não há migração a desfazer.
- Emergência sem novo deploy de código: `MotionConfig reducedMotion="always"` desliga as animações de transformação em todo o app (mudança de uma linha).

## ⏳ DECISÕES PENDENTES DO PO

Levantadas na revisão de frontend de 2026-09-24 (`docs/qa/assessments/2026-09-24-revisao-frontend.md`, seção 3) — bloqueiam ACs específicos até serem decididas:

- **Cor da diferença (verde × vermelho):** hoje "Diferença Anual" aparece verde/`success` na tabela financeira (`FinancialTable.tsx:113,208`) e vermelha/"Perda" nos cards de métricas (`MetricsCards.tsx:35`) — mesmo valor, cores opostas (achado 14). A story 2.4 (AC 8) propõe alinhar a tabela à semântica dos cards (perda = vermelho); se o PO preferir o contrário, ajustar `MetricsCards` em vez da tabela.
- **Paleta/contraste (`colorPrimary` e cores da marca):** o azul `#0ea5e9` e o verde `#22c55e` usados em texto/botões não atingem 4,5:1 de contraste (WCAG AA) — a story 2.5 (AC 5) propõe `#0369a1` e `#15803d` para texto/fundo de botão, mantendo os tons originais só em uso decorativo. Precisa de aprovação do PO com captura antes/depois, porque muda a aparência visual da marca em várias telas.
- **Movimento do próprio Ant Design (story 2.5, AC 11):** o épico controla as animações que ele mesmo introduz (`motion`/`m`, CSS do épico), mas não as animações internas do Ant Design (Drawer, Modal, Dropdown, Menu). Decidir entre manter essas animações como estão (documentando a exceção) ou desligá-las também com `ConfigProvider theme={{ token: { motion: false } }}` quando `prefers-reduced-motion: reduce` estiver ativo.

## ✅ DEFINITION OF DONE

### Funcional
- [ ] Todas as stories 2.1–2.5 com ACs atendidos e status Done.
- [ ] Achados de alta prioridade da revisão (itens 1, 5, 7, 10, 11, 12, 14, 22, 23, 30) resolvidos ou com justificativa registrada.
- [ ] Animações entre 150 e 300 ms (exceto contadores numéricos e o destaque de edição da tabela, até 600 ms) e desligadas com reduced-motion.

### Técnico
- [ ] `npx tsc -b` sem erros.
- [ ] `npx eslint` nos arquivos alterados sem novos erros (total do projeto ≤ 16 erros).
- [ ] Build de verificação em pasta separada concluído e diferença de tamanho do bundle registrada.
- [ ] Zero regressões nos fluxos de consulta, edição/autosave, PDF, login e admin.

### Qualidade
- [ ] Verificação manual em Chrome/Firefox, desktop (≥ 1280 px) e mobile (375 px), com e sem `prefers-reduced-motion`.
- [ ] Contraste AA nos textos alterados; inputs da tabela com rótulo acessível; status de autosave anunciado.

## 📅 TIMELINE (estimativa)

- 2.1: 0,5–1 dia · 2.2: 1 dia · 2.3: 1–1,5 dia · 2.4: 1–1,5 dia · 2.5: 1 dia
- **Total:** 4,5–6 dias
