# SIAPS — Schema do JSON de saída

**Caminho:** `data/SIAPS/<ibge6>/<periodo>.json`
(`<periodo>` = quadrimestres unidos por `_`, ex.: `2025Q1_2025Q2_2025Q3`)

**Fonte:** `POST https://apisiaps.saude.gov.br/api/public/componente/indicador-quadrimestre/filtro`
(portal SIAPS — Relatórios Públicos da APS, https://siaps.saude.gov.br/publico)

## Estrutura top-level

```json
{
  "ibge": "260040",
  "uf": "PE",
  "municipio": "ÁGUA PRETA",
  "quadrimestres": ["2025Q1", "2025Q2", "2025Q3"],
  "fonte": "https://apisiaps.saude.gov.br/api/public/componente/indicador-quadrimestre/filtro",
  "extraido_em": "2026-06-03",
  "total_registros": 12,
  "registros": [ { /* registro bruto da API, ver abaixo */ } ]
}
```

| Campo             | Tipo        | Descrição |
|-------------------|-------------|-----------|
| `ibge`            | string (6)  | Código IBGE do município (normalizado para 6 dígitos). |
| `uf`              | string (2)  | Sigla da UF (derivada do IBGE ou passada via `--uf`). |
| `municipio`       | string\|null| Nome do município (best-effort via `/uf/<UF>/municipios`; `null` se indisponível). |
| `quadrimestres`   | string[]    | Quadrimestres consultados (AAAAQN). |
| `fonte`           | string      | URL do endpoint de origem. |
| `extraido_em`     | string      | Data da extração (ISO `AAAA-MM-DD`). |
| `total_registros` | int         | `len(registros)`. |
| `registros`       | object[]    | Registros **brutos** da API (chaves originais preservadas). |

## Registro (`registros[]`) — chaves originais da API

Cada registro é a classificação final de um **tipo de equipe** num **quadrimestre**, para
**um** dos dois componentes (`tipoOrigem`). Para um mesmo município/equipe há tipicamente um
registro `CVAT` e um `QUALIDADE` por quadrimestre.

| Campo                              | Descrição |
|------------------------------------|-----------|
| `nuQuadrimestre`                   | Quadrimestre (ex.: `2025Q1`). |
| `sgUf`, `coMunicipioIbge`, `noMunicipioAcentuado` | UF, IBGE (6), nome do município. |
| `sgEquipe`                         | Tipo de equipe: `eSF`, `eSB`, `eAP`, `eMulti`. |
| `qtdClassificacaoOtimo` … `Regular`| Contagem de equipes por classificação (Ótimo/Bom/Suficiente/Regular). |
| `percentualClassificacaoOtimo` … `Regular` | Percentual correspondente. |
| `totalEquipesValidasParaComponente`| Total de equipes válidas no componente. |
| `coTipoIndicadorOrigem`            | `119` = CVAT · `120` = QUALIDADE. |
| `tipoOrigem`                       | `"CVAT"` (Vínculo e Acompanhamento Territorial) ou `"QUALIDADE"`. |
