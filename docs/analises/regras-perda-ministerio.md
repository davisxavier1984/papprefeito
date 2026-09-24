# Story 3.1: Regras de perda confirmadas contra a API do Ministério

**Data:** 24/09/2026
**Base:** os 241 registros de `municipios_editados.json`, todos de um único usuário, cruzados com `relatorioaps-prd.saude.gov.br/financiamento/pagamento` (241 de 241 consultas ok).
**Script:** `backend/scripts/estudo_regras_perda.py`. O comando `baixar` preenche o cache fora do repo e o `analisar` gera os números abaixo.

## Resumo

| Plano | Regra encontrada | Acerto | Decisão proposta |
|---|---|---|---|
| **ACS** | (ACS credenciados − ACS pagos) × **R$ 3.242** | Desde 202512: 80% são múltiplos de 3.242, 76% ficam a ±2 ACS da regra e 39% batem exato | **Sugestão automática** (60–90%) |
| **eSF/eAP** | equipes pagas × **R$ 4.000** + equipes novas até o teto × (fixo do estrato + R$ 16.000) | 39% exato (até 202510) e 30% (desde 202512) | **Sugestão automática**, com a quantidade de equipes novas ajustável |
| **eMulti** | Equipes novas dentro do teto × custeio da modalidade (12k/24k/36k), às vezes com qualidade BOM (+18,75%) | Não é determinística: o usuário escolhe quantas equipes | **Sugestão guiada**: o usuário escolhe a quantidade por modalidade e o sistema calcula o valor |
| **Saúde Bucal** | Não encontrada (valor por equipe varia de R$ 900 a R$ 19 mil; às vezes entram CEO e UOM) | — | **Manual** até conversar com o usuário |
| Demais, Manutenção, Promoção | Não encontrada (raros) | — | **Manual** |

Nas competências até 202510, as perdas eram mais "no olho" (100 mil, 80 mil, 1,5 mi). A partir de 202512, o usuário passou a calcular de forma sistemática. **A automação deve se basear no período recente.**

## Valores oficiais deduzidos dos pagamentos

| Item | Valor |
|---|---|
| ACS: repasse por agente | R$ 3.036 (2025) e **R$ 3.242** (2026). O usuário usa 3.242 também nas competências de 2025 |
| eSF: componente fixo por equipe | Estrato 1 = 18.000, Estrato 2 = 16.000, Estrato 3 = 14.000, Estrato 4 = 12.000 |
| eSF: vínculo e qualidade BOM | R$ 6.000 cada, por equipe. **Todos os municípios estão BOM** |
| eSF: vínculo e qualidade ÓTIMO (inferido) | R$ 8.000 cada, o que explica +4.000 por equipe existente e +16.000 por equipe nova |
| eMulti: custeio mensal | Ampliada 36.000, Complementar 24.000, Estratégica 12.000 |
| eMulti: qualidade BOM | 18,75% do custeio |

## Detalhes por plano

### ACS
- Exemplos exatos:
  - 291060_202512: 85 credenciados − 71 pagos = 14 → 45.388;
  - 291360_202512: 48 ACS → 155.616.
- As diferenças de ±1 ou 2 ACS provavelmente vêm de o Ministério ter atualizado os dados depois da consulta do usuário. Um `nuCompCnes` diferente é um indício.
- Casos fora da regra, para conferir com o usuário:
  - 292740_202512: 2.239 ACS, contra 344 pela regra;
  - 354780_202606: 523, contra 62;
  - 352310_202606: 362, contra 5;
  - 310350_202512: 470, contra 0.
  Parecem usar o **teto** de ACS, e não os credenciados.

### eSF/eAP
- Sem espaço até o teto, a perda é só a qualidade: 170220 (17 equipes → 68.000), 290240 (6 → 24.000), 291150 (5 → 20.000).
- Com espaço: 292370 (12 equipes, teto 15, estrato 2 → 48.000 + 3 × 32.000 = 144.000) e 292560_202606 (6 equipes, teto 8, estrato 3 → 24.000 + 2 × 30.000 = 84.000).
- Quando o teto é muito maior (ex.: 150808, 11 equipes, teto 21), o usuário **limita** a quantidade de equipes novas. Isso é uma decisão dele, não uma regra.
- Aparece um componente recorrente de **R$ 14.058** (e 28.116, 42.174) somado em vários municípios (292260, 292273, 292540, 292575, 291210, 291350, 291060). **Pergunta para o usuário:** o que é esse valor? Uma eAP nova? Algum incentivo?
- Nas competências de 2026 (TO), aparecem R$ 6.000 por equipe em vez de 4.000 (170130, 170307). Pode ser uma classificação diferente de BOM.

### eMulti
- É a expansão do número de equipes dentro do teto, e **quem decide a quantidade é o usuário**. Municípios com o mesmo teto (1/2/10) aparecem com 36, 48 ou 60 mil.
- Exemplos coerentes:
  - 291480: 3 ampliadas pagas, teto 5 → 2 × 36.000;
  - 290310: 1 credenciada e 0 paga → 12.000;
  - 172049_202606: 14.250 = 12.000 + 2.250 (estratégica nova com qualidade BOM).

### Saúde Bucal
- Não há relação simples com o número de equipes nem com o valor por equipe. Como 77% dos valores têm centavos, o cálculo deve ser proporcional (qualidade, CEO, UOM, LRPD). **É preciso perguntar ao usuário como calcula.**

## Implicações para as stories 3.2 a 3.5

1. **Story 3.3:** a tabela passa a vir com ACS e eSF preenchidos pela regra. A eMulti ganha um seletor "equipes novas por modalidade" (padrão: 1 da maior modalidade que ainda cabe no teto). Saúde Bucal e os demais planos continuam manuais, destacados.
2. **Parâmetros ajustáveis:** valor por ACS, valores ÓTIMO da eSF e custeio da eMulti ficam numa tabela de parâmetros por competência, e não fixos no código, porque os valores mudam por portaria.
3. **Story 3.2:** gravar `valor_sugerido`, `valor_final` e `regra_id`. Com o uso, a taxa de aceite mostra se a regra está boa, e as correções do usuário mostram o que falta (ex.: o componente de 14.058).
4. **Lote (3.4 e 3.5):** para lotes, ACS e eSF já saem calculados. Os planos manuais aparecem como "pendente de revisão" na lista de municípios.

## Perguntas para o usuário (antes da story 3.3)
1. eSF: o que é o valor de **R$ 14.058** que aparece somado em vários municípios?
2. eSF: qual o critério para limitar as equipes novas quando o teto é muito maior do que o número de equipes atual?
3. eMulti: qual o critério para decidir quantas equipes novas, e de que modalidade?
4. Saúde Bucal: como você calcula a perda?
5. ACS: nos municípios grandes (292740, 354780, 352310, 310350), você usou o teto de ACS em vez dos credenciados?
6. Em 2026, a eSF passou a R$ 6.000 por equipe em alguns municípios de TO: foi outra classificação?
