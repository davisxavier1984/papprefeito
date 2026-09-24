# Continuar o trabalho (handoff de 24/09/2026)

## Onde está tudo
Branch: `chore/limpeza-seguranca`, criada a partir de `dev`. Ainda **não** houve merge nem deploy.

| Commit | O quê |
|---|---|
| `fix(deps)` | Fixa `pydyf==0.10.0` (compatibilidade com weasyprint 62.3) |
| `chore(git)` | Banco, JSONs de dados, backups, PDFs e pid saem do git (`.gitignore`); adiciona `deploy/` |
| `fix(seguranca)` | Rotas de dados exigem usuário autorizado; o frontend envia o token e faz refresh; escape no PDF; gravação atômica do JSON; handler de erro sem detalhes |
| `feat(frontend)` | Favicon do MaisPAP, título "Sistema MaisPAP", `lang=pt-BR` |
| `docs(epic-2)` | Épico de UX/animações + stories 2.1–2.5 (Draft) |
| `docs(epic-3)` | Épico de preenchimento automático e relatórios em lote + script de análise |

## ⚠️ Antes do `git pull` no PC de dev
Este pull **remove do git** `backend/papprefeito.db`, `backend/municipios_editados.json`, `backend/data_cache_papprefeito.json`, backups e PDFs. Se esses arquivos existirem rastreados na sua cópia local, o git **vai apagá-los do disco** no pull. Então:
1. Faça backup antes: `cp backend/papprefeito.db backend/municipios_editados.json ~/backup-maispap/`.
2. `git fetch && git switch chore/limpeza-seguranca`.
3. Restaure os arquivos do backup, se sumirem. Depois disso eles ficam ignorados pelo git.

Para trabalhar com os dados reais, copie-os do servidor. Lá existe um backup em `~/backups/maispap-20260924-0554/`.

## Para publicar em produção (servidor)
A produção roda **da própria pasta do repositório** no servidor (uvicorn em `backend/` e `frontend/dist` servido por `deploy/serve_spa.py`).
1. Faça merge da branch.
2. Rode `cd frontend && npm run build`, que gera a `dist` nova (o frontend novo envia o token).
3. Rode `sudo systemctl restart papprefeito-backend`, que ativa a exigência de login.
4. Os passos 2 e 3 precisam acontecer juntos: o frontend antigo não envia token e quebraria.
5. Teste: login, consulta, edição de perda, PDF individual e detalhado.
6. No primeiro start, o backend cria as tabelas `historico_perdas` e `valores_referencia` no SQLite (`create_all`, sem alterar as tabelas existentes) e grava os valores de referência de 2025.

## Próximos passos (ordem sugerida)
1. ~~Story 3.0 (hotfix do autosave)~~: **feita**. Falta validar no navegador que o upsert leva o valor recém-digitado (DevTools → Network).
2. ~~Story 3.1 (regras vs. Ministério)~~ e ~~3.1b (eMulti × CNES)~~: **feitas**. Ver `docs/analises/regras-perda-ministerio.md`. Os módulos do CNES do `maisprofissionais` foram copiados para `backend/app/services/cnes/`.
3. **Levar as 6 perguntas do relatório 3.1 ao usuário** (R$ 14.058 na eSF, critério da eMulti, Saúde Bucal etc.).
4. ~~Story 3.2 (registro estruturado + histórico)~~: **feita**. Depois do deploy, rodar a migração dos itens (primeiro sem `--aplicar` para conferir):
   `cd backend && .venv/bin/python scripts/estudo_regras_perda.py baixar municipios_editados.json` e depois `.venv/bin/python scripts/migrar_itens_perda.py municipios_editados.json`.
5. ~~3.4 + 3.5 (relatórios Prefeito/Detalhado em lote)~~: **feitas**. Página `/relatorios-lote`. Falta testar no navegador.
6. ~~3.3 (preenchimento automático)~~: **feita**. Falta testar no navegador. **Pendência do usuário:** cadastrar os valores de referência de 2026 em Menu → Valores de referência.
7. Próxima: 3.6 (módulo opcional de estimativa eMulti).
8. Épico 2 (animações): stories 2.1 → 2.5.

Documentos:
- `docs/prd/epic-3-preenchimento-automatico-e-lote.md`
- `docs/prd/epic-2-frontend-ux-animacoes.md`
- `docs/stories/`

Análise dos dados:
- `python backend/scripts/analise_perdas_informadas.py [caminho/municipios_editados.json]`: estatísticas das perdas informadas.
- `python backend/scripts/estudo_regras_perda.py baixar|analisar [caminho]`: cruza com a API do Ministério (cache em `~/.cache/maispap-ministerio`).
- `cd backend && .venv/bin/python scripts/estudo_emulti_cnes.py [municipios_editados.json]`: cruza a eMulti com o CNES (cache em `~/.cache/maispap-cnes`).

## Pendências conhecidas (fora dos épicos)
- `SECRET_KEY` tem um valor padrão inseguro em `backend/app/core/config.py` (o `install.sh` gera uma chave no deploy).
- Tokens ficam no `localStorage`; o refresh dura 7 dias.
- `/docs` e `/redoc` ficam públicos em produção.
- O frontend cai em `localhost:8000` se `VITE_API_BASE_URL` não estiver definida no build.
- O `papprefeito.db` continua no **histórico** do git (só foi tirado do índice).
- Os arquivos vazios `apt`, `sudo` e `update` (do root) estão na raiz do servidor. Para remover: `sudo rm apt sudo update`.
- O lint do frontend já tinha 16 erros antes deste trabalho.
