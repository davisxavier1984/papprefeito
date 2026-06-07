# SIAPS — CLI Downloader

Baixa do portal **SIAPS — Relatórios Públicos da APS** (https://siaps.saude.gov.br/publico) a
**classificação final das equipes** no Cofinanciamento da Atenção Primária, nos dois componentes:

- **CVAT** — Vínculo e Acompanhamento Territorial (componente que substituiu a "capitação ponderada");
- **QUALIDADE**.

O dado vem da API REST pública `apisiaps.saude.gov.br`, por município e **quadrimestre**.

## Uso

```bash
# Por quadrimestre (recomendado):
poetry run python -m SIAPS --ibge 260040 --quadrimestre 2025Q1,2025Q2,2025Q3 -v

# Por intervalo de competências AAAAMM (mapeado para quadrimestres):
poetry run python -m SIAPS --ibge 260040 --comp-inicial 202501 --comp-final 202512
```

| Argumento        | Obrigatório | Descrição |
|------------------|-------------|-----------|
| `--ibge`         | sim         | IBGE de 6 ou 7 dígitos (normalizado p/ 6). |
| `--quadrimestre` | sim*        | Quadrimestre(s) `AAAAQN` por vírgula (`2025Q1,2025Q2`). |
| `--comp-inicial` / `--comp-final` | sim* | Alternativa em `AAAAMM`; mapeada para quadrimestres (01–04→Q1, 05–08→Q2, 09–12→Q3). |
| `--uf`           | não         | Sigla UF; se omitida, deriva do prefixo IBGE. |
| `--output-dir`   | não         | Padrão: `data/SIAPS/<ibge6>/`. |
| `--timeout`      | não         | Timeout HTTP em segundos (padrão 60). |
| `-v, --verbose`  | não         | Log em DEBUG (stderr). |

\* Informe **`--quadrimestre`** OU o par **`--comp-inicial`/`--comp-final`**.

## Saída

JSON em `data/SIAPS/<ibge6>/<periodo>.json` (ex.: `data/SIAPS/260040/2025Q1_2025Q2_2025Q3.json`).
Ver `SCHEMA.md` para a estrutura. O stdout imprime apenas o caminho do arquivo salvo.

## Exit codes

`0` ok · `2` argumento inválido · `3` falha de negócio (período indisponível / sem dados / HTTP) ·
`4` falha de rede · `1` erro inesperado.
