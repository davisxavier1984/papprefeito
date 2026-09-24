# Regras do preenchimento automático completo (story 3.3)

**Origem:** entrevista com o usuário em 24/09/2026, validada contra os 241 registros do histórico e contra a API do Ministério (`docs/analises/regras-perda-ministerio.md`).

## Princípio

> "O endpoint já traz tudo o que o município tem. O objetivo é estimar o que ele poderia ter."

A perda de cada plano é o **potencial** do município (o que ele poderia receber) menos o que ele **já recebe**, calculado a partir da resposta da API do Ministério (`pagamentos` + `resumosPlanosOrcamentarios`). O usuário revisa e ajusta antes de salvar.

## Como aparece na tela

- Ao consultar um município, a tabela mostra o que está salvo. O botão **"Preencher automaticamente"** calcula os valores, e **nada é sobrescrito sem o usuário pedir**. Depois o usuário revisa e salva.
- Cada célula preenchida indica "calculado" e a regra usada. Ao passar o mouse, aparece a composição, por exemplo "48 ACS × R$ 3.242".
- O que for gravado leva `origem: "regra"`, `regra_id` e `valor_sugerido` (story 3.2), para o sistema aprender com os ajustes.

## Regras por plano

| Plano | Regra | Decisão do usuário |
|---|---|---|
| **eSF/eAP** | equipes eSF pagas × (vínculo ÓTIMO − pago + qualidade ÓTIMO − paga) **+** N equipes novas × (fixo do estrato + vínculo ÓTIMO + qualidade ÓTIMO) | N segue o padrão dos dados: se faltam **até 2** equipes até o teto, N = todas; se faltam mais, N = ⌈diferença ÷ 3⌉ |
| eSF: constante R$ 14.058 | Constante do próprio usuário, somada caso a caso | O sistema sugere **0 vezes**, e o usuário informa quantas |
| **ACS** | **(teto de ACS − ACS pagos) × valor por ACS** (R$ 3.242) | Teto (potencial máximo). O valor por credenciados − pagos aparece como informação |
| **eMulti** | Módulo "Estimativa eMulti" (story 3.6): nº de equipes = mín(T, profissionais elegíveis ÷ 6, nutricionistas + psicólogos) × custeio − custeio atual | Opcional, o usuário aplica |
| **Saúde Bucal** | Soma dos componentes abaixo | Potencial do município |
| Demais programas, Manutenção, Promoção, Academia | **Zero**, destacado como "preencher manualmente, se houver" | — |

### Saúde Bucal: componentes (validados no histórico de 202512)

| Componente | Cálculo | Entra por padrão |
|---|---|---|
| Qualidade até ÓTIMO | eSB 40h pagas × (qualidade ÓTIMO − qualidade paga por equipe) | Sim |
| eSB novas até o teto | (teto eSB 40h − eSB credenciadas) × (fixo por equipe + qualidade ÓTIMO) | Sim |
| **SESB** (Portaria GM/MS 751/2023) | R$ 7.200/mês se o município tem **até 20 mil habitantes** (`qtPopulacao`) e **ainda não recebe** SESB. A cobertura de 75% o usuário confere | Sim, se elegível |
| UOM | R$ 9.360/mês por unidade odontológica móvel | Não (opcional) |
| LRPD | Subir para a próxima faixa (R$ 11.250 → 18.000 → 27.000 → 33.750) ou implantar | Não (opcional) |
| CEO | Implantar ou mudar de tipo (valores pagos observados: 27.720 / 36.960 / 64.660) | Não (opcional) |

No histórico, essa composição explica **23 de 54** perdas de Saúde Bucal de 202512 ao centavo, e em **21 delas o SESB entrava**. Os componentes UOM, LRPD e CEO dependem de produção e demanda, que não estão na API. Por isso ficam como opções que o usuário marca.

## Tabela de valores de referência por competência (admin)

Os valores mudam por portaria, então ficam numa tabela editável por vigência, e não fixos no código. Tela de administração (superusuário), com uma linha por parâmetro e vigência (`vigente_desde` = competência AAAAMM).

Valores **confirmados para 2025** (dos pagamentos e da pesquisa):

| Parâmetro | Valor | Fonte |
|---|---|---|
| ACS: valor por agente | 3.242,00 (o Ministério pagou 3.036 em 2025; o usuário usa 3.242) | dados + usuário |
| eSF: fixo por estrato 1/2/3/4 | 18.000 / 16.000 / 14.000 / 12.000 | pagamentos |
| eSF: vínculo BOM / ÓTIMO | 6.000 / 8.000 | pagamentos / inferido do histórico |
| eSF: qualidade BOM / ÓTIMO | 6.000 / 8.000 | pagamentos / inferido do histórico |
| eMulti: custeio Estratégica/Complementar/Ampliada | 12.000 / 24.000 / 36.000 | Portaria 635/2023 |
| eMulti: qualidade BOM | 18,75% do custeio | pagamentos |
| eSB 40h: fixo | 6.021,00 | pagamentos |
| eSB 40h: qualidade ÓTIMO / BOM / SUFICIENTE | 3.673,50 / 2.755,13 / 1.836,75 | pesquisa + pagamentos |
| SESB: custeio mensal | 7.200,00 (+ 1.800 de desempenho) | Portaria 751/2023 |
| UOM | 9.360,00 | pagamentos |
| LRPD: faixas | 11.250 / 18.000 / 27.000 / 33.750 | pagamentos |

**2026: a completar pelo usuário** conforme a portaria vigente (Portaria GM/MS 10.994/2026, Anexos XCIX-A/B da PRC 6/2017). Já se observa qualidade eSB paga de R$ 3.000 por equipe e eSF com R$ 6.000 por equipe em alguns municípios de TO. Enquanto não houver valor cadastrado para uma competência, o sistema usa a vigência anterior e avisa na tela.

## Fontes
- [Portaria GM/MS 3.493/2024 (BVS)](https://bvsms.saude.gov.br/bvs/saudelegis/gm/2024/prt3493_11_04_2024.html)
- [SESB: Portaria GM/MS 751/2023 (BVS)](https://bvsms.saude.gov.br/bvs/saudelegis/gm/2023/prt0751_20_06_2023.html) e [Ministério da Saúde: SESB](https://www.gov.br/saude/pt-br/composicao/saps/brasil-sorridente/sesb)
- [Credenciamento de eSB (Ministério da Saúde)](https://www.gov.br/saude/pt-br/composicao/saps/brasil-sorridente/saude-bucal-na-aps/credenciamento-de-esb)
- [LRPD (Ministério da Saúde)](https://www.gov.br/saude/pt-br/composicao/saps/previne-brasil/valores-de-referencia/custeio-de-atencao-a-saude-bucal/lrpd)
- [Portaria GM/MS 10.994/2026](https://www.acsace.com.br/2026/05/portaria-gm-ms-10994-2026-financiamento-aps.html)
