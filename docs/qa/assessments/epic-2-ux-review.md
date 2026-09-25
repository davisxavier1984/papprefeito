# Revisão de UX priorizada — EPIC-UX-002

Atende ao AC1 da story `docs/stories/2.1.fundacao-motion-e-revisao-ux.md`: os 50 achados de UX/UI do épico
`docs/prd/epic-2-frontend-ux-animacoes.md` (achados 1–30, seção "Estado atual") e das telas novas do épico 3
(achados 31–50, revisados em `docs/qa/assessments/2026-09-24-revisao-frontend.md`, seção 2), cada um com
arquivo:linha, prioridade e a story responsável.

**Base:** HEAD atual da branch `fix/revisao-frontend`, depois das Tasks 1–4 do plano
`.superpowers/sdd/2026-09-24-correcoes-revisao-frontend/` (commits `4c78e91`, `a14fe66`, `6118e28`, `c309725`,
`8489fca`, `c31d668` — ver `git log --oneline c0d1962..HEAD`). Todas as referências arquivo:linha abaixo foram
reconferidas por leitura direta do código nesta data (2026-09-24), **não** copiadas de
`2026-09-24-revisao-frontend.md` (cujas linhas valiam para o HEAD `0cb1594`, anterior às Tasks 1–4). Caminhos
relativos a `frontend/src/`, salvo indicação contrária.

Arquivos alterados pelas Tasks 1–4 (linhas recontadas neste documento): `hooks/useAutoSave.ts`,
`hooks/useConsultarDados.ts`, `utils/filaSalvamento.ts` (novo), `utils/selecao.ts` (novo),
`utils/consultaAtual.ts` (novo), `utils/municipiosLote.ts`, `pages/RelatoriosLote.tsx`,
`components/Selectors/SeletorVariosMunicipios.tsx`, `components/DataTable/PreenchimentoAutomatico.tsx`,
`pages/Admin/ValoresReferencia.tsx`, `pages/Dashboard.tsx` (só o import de `descarregarAutosave`),
`components/DataTable/FinancialTable.tsx` (uma linha: `useAutoSave()` sem parâmetro). Todos os demais arquivos
citados abaixo (`App.tsx`, `App.css`, `index.css`, `AppLayout.tsx`, `Sidebar.tsx`, `Header.tsx`,
`MetricsCards.tsx`, `CurrencyInput.tsx`, `municipioStore.ts`, `LoginForm.tsx`, `RegisterForm.tsx`,
`ProgramaCard.tsx`, `AnaliseBox.tsx`, `ProgramasCards.tsx`, `ProgressBar.tsx`, `SaudeBucalDetalhada.tsx`,
`UserManagement.tsx`, `ProtectedRoute.tsx`) estão **idênticos** ao HEAD `0cb1594` (`git diff --stat
0cb1594..HEAD -- frontend/src` confirma isso), e tiveram suas linhas conferidas por amostragem direta.

## Achados 1–30 (revisão original do épico 2)

| # | Prioridade | Story | Status | Arquivo:linha (HEAD atual) | Achado |
|---|---|---|---|---|---|
| 1 | Alta | 2.2 | Válido (piorou) | `App.tsx:119-174`; `AppLayout.tsx:20-21`; `Sidebar.tsx:69-78` | As 5 rotas protegidas (`/dashboard`, `/relatorios-lote`, `/profile`, `/admin/users`, `/admin/valores-referencia`) instanciam cada uma seu próprio `<AppLayout>`: ao navegar, Header/Sidebar remontam e o estado da sidebar (`sidebarCollapsed`, `sidebarWidth`) some. A Sidebar agora navega (`handleNavigate`/`handleConsultar`), então cada clique no menu da própria Sidebar também a remonta. |
| 2 | Média | 2.2 | Válido | `AppLayout.tsx:81`; `Dashboard.tsx:106,221`; `App.css:24-37` | `fade-in-up` aplicada em dois níveis aninhados (Content do layout + raiz da página); a keyframe não respeita `prefers-reduced-motion`. |
| 3 | Média | 2.2 | Válido | `Sidebar.tsx:252`; `Sidebar.tsx:89-113` | `transition: 'width 0.2s ease, padding 0.2s ease'` do `Sider` também se aplica durante o arraste (`handleMouseDown`), causando atraso ("borracha"). |
| 4 | Baixa | 2.2 | Válido | `AppLayout.tsx:27`; `FinancialTable.tsx:38`; `index.css:42,61`; `App.css:40` | Breakpoints "mobile" inconsistentes: 760/780 px com histerese em `AppLayout`, 768 px sem histerese em `FinancialTable`/CSS; cada componente com seu próprio listener de `resize`. |
| 5 | Alta | 2.3 | Válido | `Dashboard.tsx:104-218` | Durante a primeira consulta (`isLoading` verdadeiro, ainda sem dados) o usuário continua vendo o estado vazio "Nenhum dado carregado ainda"; sem skeleton. |
| 6 | Média | 2.3 | Válido | `FinancialTable.tsx:264` | Numa reconsulta (dados já carregados), só a `Table` recebe `loading`; `MetricsCards`/`ProgramasCards`/`AnaliseBox` continuam com os números antigos sem indicação. |
| 7 | Alta | 2.5 | Parcial | `Sidebar.tsx:74-78`; `Sidebar.tsx:175-185`; `Sidebar.tsx:211-234` | O erro de consulta só aparece no `Alert` da sidebar; no mobile fica dentro do `Drawer` (`isMobile` → `Drawer`). O Drawer fecha ao navegar para outra rota (`handleNavigate` chama `onDrawerClose`), mas **não** fecha automaticamente após uma consulta bem-sucedida disparada da própria sidebar (`handleConsultar` não fecha o Drawer). |
| 8 | Baixa | 2.5 | Válido | `Dashboard.tsx:129` | Imagem do estado vazio ainda vem de `gw.alipayobjects.com` (CDN externo). |
| 9 | Baixa | 2.5 | Válido | `pages/Admin/UserManagement.tsx:243-255` (confirmado: `Spin` em `:245`) | `Spin` apenas no primeiro carregamento; sem estado vazio específico para lista filtrada vazia. |
| 10 | Alta | 2.4 | Válido | `hooks/useAutoSave.ts:14` (SaveStatus), `:27` (error), `:78-118` (triggerSave), `:128-135` (retorno); `FinancialTable.tsx:227-234` | Não existe estado `'pending'` entre a edição e o fim do debounce (`SaveStatus` continua `'idle'\|'saving'\|'saved'\|'error'`); o indicador mostra "Pronto" enquanto há edição não salva. `error` nunca é lido nem exibido pela tabela; sem ação de "tentar novamente". |
| 11 | Alta | 2.4 | Válido | `FinancialTable.tsx:227-234` (condição redundante em `:231`) | Indicador de status sem `aria-live`/`role="status"`; `isSaved && status === 'saved'` continua redundante. |
| 12 | Alta | 2.4 | Válido | `FinancialTable.tsx:126` | `MobileCardView` continua declarado dentro do corpo de `FinancialTable` — nova identidade de componente a cada render, remonta todos os cards/inputs mobile a cada alteração do store ou do status do autosave. |
| 13 | Média | 2.4 | Válido | `FinancialTable.tsx:47-118` (dependências do `useMemo` em `:118`) | Colunas recriadas a cada edição (`[dadosProcessados, triggerSave, updatePerca]`); sem destaque visual de quais valores derivados mudaram após salvar. |
| 14 | Alta | 2.4 | Válido | `FinancialTable.tsx:113` (desktop), `:208` (mobile); `Metrics/MetricsCards.tsx:35,84-114` | Semântica de cor contraditória: diferença anual `> 0` é `success`/verde na tabela e "Perda"/vermelho nos cards de métricas. |
| 15 | Média | 2.2 / 2.3 / 2.5 | Válido | `Metrics/MetricsCards.tsx:44-190`; `Auth/LoginForm.tsx:43-76`; `Auth/RegisterForm.tsx:82-114,136-169`; gradiente em `Sidebar.tsx:150`, `AppLayout.tsx:65-72`, `LoginForm.tsx:147-154`, `RegisterForm.tsx:298-305` | Estilos inline duplicados em massa: os 4 cards de métricas repetem o mesmo bloco; o casco fundo/overlay/card de Login é copiado no Registro (inclusive na tela de sucesso); o botão com gradiente se repete em 4 arquivos. |
| 16 | Média | 2.5 | Válido | `Sidebar.tsx:150`; `LoginForm.tsx:62,151`; `App.tsx:60`; `Header.tsx:89` | Gradientes divergentes para a "mesma" marca (`--primary-blue → --secondary-blue` vs `#0ea5e9 → #06b6d4`); o token `Layout.headerBg` (`App.tsx:60`) não é usado porque o Header força `background: '#fff'` (`Header.tsx:89`). |
| 17 | Baixa | 2.5 | Válido | `Layout/Header.tsx:145-146` | Cor da tag de UF fixa para BA/GO (`#1e40af`/`#16a34a`) e cinza para as demais 25 UFs, sem significado para o usuário. |
| 18 | Baixa | 2.5 | Válido | `index.css:36-40,42-46`; `Header.tsx:96` | `.header-logo` com `max-height: 80px` dentro de um header de `74px`; no mobile o Header não esconde tags nem o nome do usuário. |
| 19 | Baixa | 2.3 | Válido | `Programas/ProgramaCard.tsx:56-62`; `Programas/AnaliseBox.tsx:39-45`; `Programas/SaudeBucalDetalhada.tsx:13-19` | Formatadores `Intl.NumberFormat` recriados a cada render, divergindo dos formatadores de módulo de `MetricsCards.tsx:11-21`/`FinancialTable.tsx:21-25`. |
| 20 | Média | 2.5 | Válido | `pages/Admin/UserManagement.tsx:134,140`; `AppLayout.tsx:84` | `padding: '24px'` somado ao padding do `Content` → recuo duplo; `Row gutter={16}` sem gutter vertical. |
| 21 | Baixa | 2.5 | Válido | `Programas/SaudeBucalDetalhada.tsx` (0 ocorrências de import fora do próprio arquivo, confirmado via `grep -rn SaudeBucalDetalhada frontend/src`) | Código morto; usa `Collapse.Panel`, API depreciada no Ant Design 5. |
| 22 | Alta | 2.5 | Válido | `Header.tsx:134-136,157-159`; `Sidebar.tsx:264`; `LoginForm.tsx:87`; `App.tsx:47` | Contraste texto branco sobre `#0ea5e9` ≈ 2,8:1 e sobre `#22c55e` ≈ 2,3:1 — abaixo de 4,5:1 (WCAG AA); mesmo problema em títulos na cor `colorPrimary`. |
| 23 | Alta | 2.4 | Válido | `inputs/CurrencyInput.tsx:131-148`; `FinancialTable.tsx:71,173` | `CurrencyInput` sem `aria-label`; `id` padrão `'currency-input'` (`CurrencyInput.tsx:133`) duplicaria se o `id` não fosse passado (na tabela já é passado nas linhas 71/173). |
| 24 | Média | 2.5 | Válido | `Sidebar.tsx:268-277` (botão recolher); `:283-301` (borda de redimensionamento) | Botão de recolher só com ícone e `title` (sem `aria-label`/`aria-expanded`); borda de redimensionamento só funciona com mouse. |
| 25 | Baixa | 2.5 | Válido | `Dashboard.tsx:116,157,271`; `Programas/ProgramasCards.tsx:40,69`; `AnaliseBox.tsx:57,109-125` | Emojis em títulos são lidos por leitores de tela e competem com a hierarquia visual. |
| 26 | Baixa | 2.5 | Válido | `Programas/ProgramaCard.tsx:208-215,259,275`; `SaudeBucalDetalhada.tsx:30,40`; `Header.tsx:196` (10 px, Tag "Admin") | Fontes de 10–11 px prejudicam a legibilidade. |
| 27 | Média | 2.5 | Válido | `index.css` (nenhuma regra `:focus-visible`) | Navegação por teclado depende só do padrão do Ant Design; `outline` some em elementos customizados. |
| 28 | Baixa | 2.5 | Válido | `Auth/LoginForm.tsx:146` | `useAuthStore(...)` chamado dentro de uma prop JSX (`loading={...}`). |
| 29 | Média | 2.5 | Pior (regressão; valor de referência desatualizado) | build de verificação a refazer | A linha de base de 1.349.737 bytes não existe mais; a medição mais recente registrada (1.391.147 bytes, revisão de 2026-09-24) também é **anterior** às Tasks 1–4 deste plano. Essas tasks só adicionaram utilitários puros (`filaSalvamento.ts`, `selecao.ts`, `consultaAtual.ts`, funções em `municipiosLote.ts`) e pequenas mudanças de fluxo, sem novas dependências — impacto esperado no bundle é mínimo, mas não medido aqui (tarefa de documentação, sem build). A story 2.1 deve medir uma nova linha de base no HEAD atual antes de iniciar (ver Task 6.3 revisada). |
| 30 | Alta | 2.4 | **Resolvido** (`9d19d19`) — só regressão pendente na 2.4 | `hooks/useAutoSave.ts:78-118`, leitura da store em `:85` | `triggerSave` já lê `useMunicipioStore.getState()` no momento da chamada (comentário explicativo em `:81-84`), corrigindo a closure desatualizada relatada no achado original. Os defeitos decorrentes desse bug (C1/C2/C10 da revisão de código de 2026-09-24 — edição perdida no unmount, PDF sem a última edição, reconsulta sobrescrevendo edição) foram corrigidos nesta branch `fix/revisao-frontend` via a fila de autosave (`utils/filaSalvamento.ts`; commits `4c78e91`, `a14fe66`, `6118e28`): a edição pendente é gravada ao desmontar a tabela, antes dos dois PDFs (`Dashboard.tsx` chama `descarregarAutosave()`) e antes de nova consulta (`useConsultarDados.ts:34`). A story 2.4 deve apenas validar a regressão (Network) e implementar os estados visuais que ainda faltam (ver achado 10). |

## Achados 31–50 (telas novas do épico 3)

| # | Prioridade | Story | Status | Arquivo:linha (HEAD atual) | Achado |
|---|---|---|---|---|---|
| 31 | Média | 2.4 | Válido | `FinancialTable.tsx:227-250` | Barra "Status" + botão "Preencher automaticamente" num `Space` sem `wrap`; ainda pode transbordar em 375 px. |
| 32 | Média | 2.4 | Válido | `DataTable/PreenchimentoAutomatico.tsx:105-106` | Ao aplicar (`onAplicado(); onClose();`), o modal fecha sem mensagem nem destaque das linhas alteradas; o indicador de status fica "Pronto" durante o debounce (ver achado 10). |
| 33 | Alta | 2.5 | Válido | `PreenchimentoAutomatico.tsx:150-153` | Checkbox de seleção do plano sem rótulo acessível. |
| 34 | Média | 2.5 | Válido | `PreenchimentoAutomatico.tsx:178` | `minWidth: 300` no Checkbox de componente; transbordo em 375 px. |
| 35 | Média | 2.5 | **Parcialmente resolvido** (`c31d668`) | `PreenchimentoAutomatico.tsx:45-71` (reset por abertura), `:132-139` (Spin/Empty) | Corrigido nesta branch: o estado (`planos`/`erro`/`aviso`) é limpo a cada abertura do modal (`:48-53`), o `Spin` agora tem texto ("Calculando a sugestão…", `:134`) e existe um `Empty` para "nenhum plano com cálculo automático" (`:139`). O texto original do achado ("aviso antigo fica junto de erro novo") não se reproduz mais. Falta só a entrada animada (fade), prevista para a story 2.5. |
| 36 | Baixa | 2.5 | Válido | `PreenchimentoAutomatico.tsx:120,162` | "→" (`:162`) lido como "seta" por leitor de tela; texto "plano(s)" (`:120`). |
| 37 | Média | 2.5 | Válido | `Selectors/SeletorVariosMunicipios.tsx:76-111` | Selects de UF/município só com `placeholder`; campo de competência com `addonBefore` sem `<label>` associado. |
| 38 | Média | 2.5 | Válido | `SeletorVariosMunicipios.tsx:95`; `RelatoriosLote.tsx:172,174` | Competência inválida só pinta a borda (`status="error"`); botão "Gerar" fica desabilitado (`disabled={!podeGerar \|\| iniciando}`) sem explicação visível do motivo. |
| 39 | Média | 2.5 | Válido | `SeletorVariosMunicipios.tsx:25-36` | `isError` das queries de UFs e municípios (não desestruturado do `useQuery`) continua ignorado; falha de rede não é comunicada. |
| 40 | Baixa | nova story (justificativa: melhoria de granularidade da seleção, não coberta pelos ACs de nenhuma story 2.x) | Válido | `SeletorVariosMunicipios.tsx:113-125` | Resumo por UF só com contagem (`Tag` fechável por UF inteira); não dá para ver ou remover um município específico de outra UF sem abrir aquela UF de novo. |
| 41 | Média | 2.5 | Válido | `RelatoriosLote.tsx:179-188` | Bloco de progresso (`Progress` + texto de contagem) sem `aria-live`/`role="status"`. |
| 42 | Média | nova story (justificativa: a parte pendente — seleção editável durante a geração — não está coberta por nenhum AC das stories 2.2–2.5) | **Parcialmente resolvido** (`c309725`) | `RelatoriosLote.tsx:36-37` (estado), `:58-65` (retomada), `:71-99` (polling), `:103-123` (limpeza) | A retomada do lote ao sair/voltar da página foi implementada nesta branch via `sessionStorage` (`utils/municipiosLote.ts`: `guardarLoteAtivo`/`lerLoteAtivo`; efeito de retomada em `RelatoriosLote.tsx:58-65`) — isso também resolve o achado C7 da revisão de código de 2026-09-24 ("lote em andamento se perde ao sair da página"). Continua em aberto, por isso mantido como nova story: a seleção de municípios e os tipos de relatório continuam editáveis durante a geração (`gerando` não desabilita `SeletorVariosMunicipios` nem o `Checkbox.Group` de tipos). |
| 43 | Baixa | 2.5 | Válido | `RelatoriosLote.tsx:183,194-205` | `lote.status === 'erro'` com `lote.erros` vazio mostra só a barra vermelha (`Progress status="exception"`); o `Alert` de erros só é renderizado quando `erros.length > 0`. |
| 44 | Baixa | 2.5 | Válido | `RelatoriosLote.tsx:120,174,186` | "Gerar 0 relatório(s)" é possível antes de qualquer seleção (`listaSelecionados.length * tipos.length`); plural sempre "(s)", mesmo com 1 item. |
| 45 | Média | 2.5 | Válido | `Admin/ValoresReferencia.tsx:114-133` | Formulário de cadastro só com `placeholder` (sem `<label>`); larguras fixas (150/190/220/360 px) transbordam em 375 px. |
| 46 | Média | 2.5 | **Resolvido** (`c31d668`) | `Admin/ValoresReferencia.tsx:139-150` | O erro ao listar valores de referência agora aparece num `Alert` com botão "Tentar novamente" (`refetch()`), em vez de virar silenciosamente uma tabela vazia sem explicação. O cadastro continua disponível mesmo com a listagem falhando. A story 2.5 deve só dar acabamento visual (entrada animada) a esse `Alert`, se fizer sentido. |
| 47 | Baixa | 2.5 | Válido | `ValoresReferencia.tsx:82-88` (botão remover sem `loading`); `:69-76` (coluna "Valor" sem unidade) | `remover.isPending` não é usado no botão; coluna "Valor" não exibe "R$". |
| 48 | Média | 2.2 | Válido | `Layout/Sidebar.tsx:117-130,212-217,264-266`; `Layout/Header.tsx:36-84` | Navegação dentro da sidebar ainda rotulada "Filtros" (Menu de navegação seguido do Divider "Consulta de município" no mesmo bloco visual; título "Filtros" no `Sider`; "Filtros e Parâmetros" no `Drawer`); itens de navegação (Dashboard, Relatórios em lote, Meu Perfil, Gestão de Usuários, Valores de referência) duplicados no dropdown do Header. **Correção de referência:** o achado original apontava `AppLayout.tsx:60-76` para os itens duplicados; a lista de itens do dropdown está em `Header.tsx:36-84` — `AppLayout.tsx` não contém itens de menu. |
| 49 | Baixa | 2.2 | Válido | `Sidebar.tsx:119,243-249` | `Menu inlineCollapsed` (~80 px de largura mínima) dentro de um `Sider` recolhido de 64 px com padding de 8 px (`collapsedWidth={64}`, `padding: collapsed ? '24px 8px' : ...'`); possível corte visual (não verificado num navegador real). |
| 50 | Baixa | 2.5 | Válido | `RelatoriosLote.tsx:139`; `Admin/ValoresReferencia.tsx:94`; `Dashboard.tsx:231-233` | `Title level={3}` nessas duas telas novas, enquanto as demais usam `level={2}`/`level={4}`; o botão "Vários municípios" (`Dashboard.tsx:231`) não indica que leva à tela "Relatórios em lote". |

## Resumo

- **Resolvidos nesta branch:** achados 30 (`9d19d19` + `4c78e91`/`a14fe66`/`6118e28`) e 46 (`c31d668`).
- **Parcialmente resolvidos nesta branch** (parte tratada, resto permanece com a story indicada): achados 35 e 42 (`c31d668` e `c309725`, respectivamente); achado 7 segue "Parcial" como já estava na revisão de 2026-09-24 (Drawer fecha ao trocar de rota, mas não após consulta bem-sucedida na própria sidebar).
- **Regressão de dado (não de comportamento):** achado 29 — a linha de base de bundle precisa ser remedida no início da story 2.1.
- **Correção de mapeamento de arquivo em relação à revisão de 2026-09-24:** achado 48 (itens duplicados do dropdown estão em `Header.tsx`, não em `AppLayout.tsx`).
- Todos os demais achados (1–6, 8–28, 31–34, 36–41, 43–45, 47, 49–50) continuam válidos como descrito, só com arquivo:linha reancorado ao HEAD atual.
