# Preenchimento automático que aprende com o consultor — desenho

**Data:** 2026-09-24 · **Status:** aprovado em conversa, aguardando revisão do documento
**Relacionados:** story 3.3 (`docs/analises/regras-preenchimento-completo.md`), story 3.2 (itens com `origem`/`valor_sugerido`), relatórios em lote (stories 3.4/3.5)

## 1. Objetivo

A geração em lote só faz sentido se o preenchimento automático produzir valores próximos do que o consultor informaria, porque o lote roda **sem revisão**. Este trabalho:

1. corrige a regra que mais se afasta do consultor (ACS);
2. guarda as respostas do Ministério para que o sistema possa se medir contra o histórico;
3. mostra ao consultor, no modal de preenchimento do Dashboard, como ele mesmo preencheu **Demais programas** e **Promoção à saúde** em municípios parecidos;
4. dá ao administrador um painel de "acerto do automático" por plano, recalculado sobre o histórico a cada consulta (aprendizado contínuo com decisão humana).

**Fora do escopo:** edição de valores no lote; ajuste automático das regras por fatores (abordagem B) e troca automática de fórmula (abordagem C), ambas descartadas.

## 2. Evidências (simulação sobre o histórico)

Base: 92 registros salvos desde 202512 em `backend/municipios_editados.json`, com a resposta do Ministério consultada para cada um (validação deixando cada município de fora).

| Plano | Regra atual vs. consultor (87 registros manuais) | Conclusão |
|---|---|---|
| eSF | erro mediano 26%, 41/85 em ±25%, soma 0,94 | manter |
| Saúde Bucal | 28%, 38/84, soma 0,89 | manter |
| ACS (teto − pagos) | 175%, 3/51, soma 3,40, zero certo 58/87 | **trocar** |
| ACS (credenciados diretos − pagos diretos) × 3.242 | **49/87 exatos**, erro 4%, 33/51 em ±25%, zero certo 75/87 | nova regra |

Fatores de correção aprendidos (global ou por porte) não melhoraram eSF nem Saúde Bucal. Para Demais e Promoção, os dados do Ministério **não** preveem quando o consultor preenche (empata ou perde para "sempre zero": 78/92 e 23/33); quando ele preenche, a mediana dos 3 municípios parecidos que preencheram erra 32% (Promoção, 5/10 em ±25%) e 57% (Demais, 2/14).

## 3. Desenho

### 3.1 Regra do ACS

`backend/app/services/regras_perda.py`, `regra_acs`, passa a devolver dois componentes:

| id | nome | quantidade | valor unitário | incluído | editável |
|---|---|---|---|---|---|
| `acs_credenciados` | ACS credenciados ainda não pagos | `max(qtAcsDiretoCredenciado − qtAcsDiretoPgto, 0)` | `acs_valor` | **sim** | sim |
| `acs_teto` | ACS até o teto (acima dos credenciados) | `max(qtTetoAcs − max(qtAcsDiretoCredenciado, qtAcsDiretoPgto), 0)` | `acs_valor` | **não** | sim |

Detalhe do primeiro: "Credenciados {c}, pagos {p}, teto {t}". O `regra_id` passa a `acs_v2` (o `v1` antigo continua reconhecido na leitura dos itens gravados). O lote (`sem_perdas='regras'`) soma só componentes incluídos, logo passa a usar credenciados − pagos sem mudança no serviço de lote.

Atualizações: `docs/analises/regras-preenchimento-completo.md` (linha do ACS e seção de validação) e `backend/tests/test_regras_perda.py` (casos com credenciados > pagos, credenciados ≤ pagos, teto acima dos credenciados, e um caso real do histórico que bate ao centavo).

### 3.2 Respostas do Ministério no SQLite

Nova tabela em `backend/app/models/db_models.py`, criada por `init_db` (incluir o modelo no import de `init_db`):

```
respostas_ministerio
  codigo_ibge   TEXT   (PK composta)
  competencia   TEXT   (PK composta, AAAAMM)
  resposta      TEXT   JSON bruto devolvido pela API
  atualizado_em DATETIME
```

Gravação: em `SaudeAPIClient.consultar_financiamento` (`backend/app/services/api_client.py`), depois de validar a resposta, fazer upsert com uma sessão própria (`async_session()`, como no `lifespan` de `main.py`). Falha ao gravar só gera log; nunca quebra a consulta. Como todas as consultas passam por esse método (Dashboard, preenchimento, eMulti, PDFs, lote), não há outro ponto a alterar.

Serviço `backend/app/services/respostas_ministerio.py`: `salvar(ibge, comp, dados)`, `obter(ibge, comp) -> dict | None`, `listar(chaves) -> dict[(ibge, comp), dict]`.

Carga inicial: `backend/scripts/carregar_respostas_ministerio.py` percorre as chaves de `municipios_editados.json` com competência ≥ um parâmetro (padrão `202512`), pula as que já existem na tabela e consulta o Ministério com intervalo de 0,4 s. Roda manualmente, uma vez, no servidor.

### 3.3 Municípios parecidos (Demais e Promoção, só no modal)

Serviço puro `backend/app/services/parecidos.py`:

- `perfil(resposta) -> Perfil`: `uf`, `populacao` (`qtPopulacao`), `equipes` (`qtEsfTotalPgto + qtEapTotalPgto`), `recebe` (dict plano → soma de `vlIntegral` dos resumos municipais).
- `distancia(a, b, plano)`: euclidiana sobre `log10(populacao)`, `log1p(equipes)`, `log1p(recebe Demais)/3`, `log1p(recebe Promoção)/3`, `log1p(recebe plano)/3`, **+0,5** se a UF for diferente. (Mesma medida da simulação.)
- `parecidos(alvo, historico, plano, k=3)`: ordena o histórico pela distância, descarta o mesmo `codigo_ibge`, mantém só registros em que o plano foi preenchido **manualmente** com valor > 0, devolve os `k` primeiros e a mediana dos valores.

O histórico são os registros de `municipios_editados.json` que têm resposta gravada (3.2); cada registro salvo depois disso entra automaticamente na próxima busca (aprendizado contínuo sem passo extra).

Endpoint `GET /api/preenchimento/{ibge}/{comp}/parecidos` (usuário autorizado) → `{ planos: [{ plano: 'Demais programas…', indice, mediana, exemplos: [{ codigo_ibge, municipio, uf, competencia, valor, distancia }] }] }`, só para os planos cujo nome começa com "Demais programas" e "Incentivo financeiro da APS - Promoção". Se o município consultado não tiver resposta gravada, o endpoint consulta o Ministério (o que também a grava).

Frontend (`PreenchimentoAutomatico.tsx`): para esses dois planos, uma linha "Municípios parecidos: Maricá/RJ 202606 R$ 27.300 · …" e um botão "Aplicar mediana (R$ X)", que marca o plano para aplicação com o valor da mediana e `regra_id` = `parecidos_v1`. Nada vem marcado. Sem exemplos: "Sem histórico parecido". O lote **não** usa este recurso: Demais e Promoção continuam zero no lote.

### 3.4 Painel "Acerto do automático" (admin)

Serviço `backend/app/services/acerto.py`: para cada registro do histórico com resposta gravada e competência ≥ `desde`, roda `sugerir(resposta, valores_vigentes)` (sem estimativa de eMulti) e compara, plano a plano, o total sugerido com o valor do item de origem `manual`. Métricas por plano (eSF, Saúde Bucal, ACS; Demais e Promoção só com contagem de preenchidos):

- registros comparados; exatos (|dif| < R$ 1); erro mediano (só onde o informado > 0); dentro de ±25%; zero certo (sugerido > 0 ⇔ informado > 0); soma sugerida ÷ soma informada;
- `alerta` quando soma ∉ [0,8; 1,25] ou erro mediano > 50%;
- `sem_resposta`: quantos registros ficaram de fora por falta de resposta gravada.

Endpoint `GET /api/preenchimento/acerto?desde=202512` (superusuário). Página `frontend/src/pages/Admin/AcertoAutomatico.tsx`, rota `/admin/acerto-automatico` protegida por `requireSuperuser`, item "Acerto do automático" no Menu da Sidebar junto dos outros itens de admin: tabela por plano com as métricas, tag de alerta, seletor de competência inicial e a contagem de registros sem resposta.

## 4. Erros e casos-limite

- Falha ao gravar resposta do Ministério: log de aviso, consulta segue normalmente.
- Resposta sem `pagamentos` ou sem `qtPopulacao`: o registro fica fora dos parecidos (perfil incompleto) e conta em `sem_resposta` no painel.
- Menos de 3 parecidos: devolve os que houver; nenhum: lista vazia.
- Registros com itens de origem `regra`/`estimativa` não entram nas comparações (não refletem o julgamento do consultor).

## 5. Testes

- Backend (pytest, `backend/tests/`): nova `regra_acs`; `perfil`/`distancia`/`parecidos` com histórico sintético (inclui exclusão do mesmo município e de origem não manual); métricas de `acerto` com casos sintéticos (exato, zero certo, alerta); upsert em `respostas_ministerio` com banco SQLite temporário.
- Frontend (`npm test`, `node --test`): função pura de formatação da linha de parecidos e cálculo do valor aplicado.
- Verificação manual: modal com Demais/Promoção num município com histórico parecido; painel mostrando ACS com soma próxima de 1 depois da troca da regra.

## 6. Restrições

- Não rodar `npm run build` em `frontend/` (produção serve `frontend/dist`); build de verificação só em `/tmp`.
- Não usar o banco de produção em testes; testes criam SQLite temporário.
- Sem dependências novas no frontend; no backend, só o que já está em `requirements.txt`.
