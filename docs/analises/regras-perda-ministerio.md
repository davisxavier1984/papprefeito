# Story 3.1: Regras de perda confirmadas contra a API do Ministério

**Data:** 24/09/2026
**Base:** os 241 registros de `municipios_editados.json`, todos de um único usuário, cruzados com `relatorioaps-prd.saude.gov.br/financiamento/pagamento` (241 de 241 consultas ok).
**Script:** `backend/scripts/estudo_regras_perda.py`. O comando `baixar` preenche o cache fora do repo e o `analisar` gera os números abaixo.

## Resumo

| Plano | Regra encontrada | Acerto | Decisão proposta |
|---|---|---|---|
| **ACS** | (ACS credenciados − ACS pagos) × **R$ 3.242** | Desde 202512: 80% são múltiplos de 3.242, 76% ficam a ±2 ACS da regra e 39% batem exato | **Sugestão automática** (60–90%) |
| **eSF/eAP** | equipes pagas × **R$ 4.000** + equipes novas até o teto × (fixo do estrato + R$ 16.000) | 39% exato (até 202510) e 30% (desde 202512) | **Sugestão automática**, com a quantidade de equipes novas ajustável |
| **eMulti** | O teto segue a Portaria 635/2023 (Estratégica 1–4, Complementar 5–9, Ampliada 10–12 eSF/eAP), mas a quantidade de equipes novas é decisão do usuário. O CNES não limita (3.1b) | Nenhuma regra passa de 14% | **Sugestão guiada**: o usuário escolhe quantas equipes por modalidade e o sistema calcula |
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

### eMulti (revisado com o repositório `maisprofissionais`)
**Regra da Portaria GM/MS 635/2023** (ver `emulti_utils.py` em github.com/davisxavier1984/maisprofissionais): a modalidade depende de **quantas eSF/eAP a eMulti vincula**.

| Modalidade | eSF/eAP vinculadas | CH mínima da equipe | Custeio/mês | Composição fixa |
|---|---|---|---|---|
| Estratégica | 1 a 4 | 100 h | R$ 12.000 | Nutricionista ou Psicólogo |
| Complementar | 5 a 9 | 200 h | R$ 24.000 | Grupo 1 (Assist. Social, Farmacêutico Clínico, Nutricionista, Psicólogo) + Grupo 2 (Fisio, Fono, Ed. Física, TO) |
| Ampliada | 10 a 12 | 300 h | R$ 36.000 | Igual à Complementar |

**Confirmado nos dados:** o teto que o Ministério devolve é `teto Estratégica = T`, `teto Complementar = ⌊T/5⌋` e `teto Ampliada = ⌊T/10⌋`, com T = eSF + eAP credenciadas. São **alternativas**, e não se somam. Exemplos:
- T = 10 → teto (1, 2, 10);
- T = 21 → teto (2, 4, 21);
- T = 54 → teto (5, 10, 54).

**O que o usuário faz:** escolhe equipes a mais (ex.: T = 21 e nenhuma eMulti → 4 Complementares = 96.000, igual em 290460 e 293070; T = 10–12 sem eMulti → 2 Complementares = 48.000 na maioria dos casos). A perda é **combinação alvo − custeio atual**.

**Spike 3.1b: a hipótese do CNES foi testada e rejeitada.** A coleta foi feita com `backend/scripts/estudo_emulti_cnes.py` sobre 85 municípios do período recente.
- **82 de 85** municípios têm os grupos fixos completos e carga horária para ao menos uma Complementar. Então o CNES quase nunca limita.
- Municípios com o mesmo T e disponibilidade parecida recebem alvos diferentes. Por exemplo, com T = 8 e CH elegível entre 814 e 883, o alvo foi 48 mil em dois casos e 72 mil em outros dois.
- Nenhuma regra fixa explica os valores:

| Regra testada (desde 202512, n = 83) | Acerto exato |
|---|---|
| ⌊T/5⌋ Complementares + 1 Estratégica para o resto − atual | 11% |
| ⌊T/5⌋ Complementares + 1 Estratégica por equipe restante − atual | 8% |
| ⌊T/5⌋ × 24 mil − atual | 11% |
| +1 Estratégica (12 mil) | 11% |
| +2 Estratégicas (24 mil) | 14% |

- 63% das perdas são múltiplos de 12 mil. Os valores mais comuns são 24 mil (12×), 48 mil (12×), 12 mil (9×) e 36 mil (5×). Ou seja, o usuário **acrescenta de 1 a 4 equipes**, numa quantidade que ele decide caso a caso.

**Estimativa por quantidade de profissionais elegíveis (sem carga horária).** Foi a forma indicada pelo usuário. Testes nos 85 municípios:

| Estimador | ±1 equipe (±12 mil) | Exato |
|---|---|---|
| min(T, CH elegível × 50% ÷ 100 h, nutri + psi) × 12 mil − atual (com CH, descartado) | 42% | 12% |
| **min(T, P ÷ 6, nutri + psi) × 12 mil − atual** (P = profissionais elegíveis) | 39% | **16%** |
| min(T, P ÷ 5, nutri + psi) × 12 mil − atual | 42% | 7% |
| (min(T, P ÷ 7) − equipes atuais) × 12 mil | 39% | 16% |
| min(⌊T/5⌋, grupo 1, grupo 2, P ÷ 10) × 24 mil − atual | 36% | 12% |

Decisão: a story 3.6 usa **P ÷ 6** (ajustável), **sem carga horária**. Uma limitação: o CNES consultado é o cadastro atual, não o da época de cada competência, e isso reduz a taxa medida.

**Conclusão para a story 3.3 (eMulti = sugestão guiada):**
1. A tela mostra T, o teto por modalidade, as eMulti atuais e a disponibilidade no CNES (grupos fixos e CH), usando `backend/app/services/cnes/`.
2. O usuário informa **quantas equipes a mais de cada modalidade**, e o sistema calcula o valor (custeio + qualidade BOM de 18,75%, se marcado). Assim ele não precisa calcular nem digitar valores.
3. O padrão inicial é a escolha mais frequente dele para aquele porte de município. Com o histórico da story 3.2, esse padrão passa a ser aprendido com os aceites e as correções.

### Saúde Bucal
- Não há relação simples com o número de equipes nem com o valor por equipe. Como 77% dos valores têm centavos, o cálculo deve ser proporcional (qualidade, CEO, UOM, LRPD). **É preciso perguntar ao usuário como calcula.**

## Implicações para as stories 3.2 a 3.5

1. **Story 3.3:** a tabela passa a vir com ACS e eSF preenchidos pela regra. Na eMulti, o usuário escolhe quantas equipes a mais de cada modalidade, e o sistema calcula o valor. Saúde Bucal e os demais planos continuam manuais, destacados.
2. **Parâmetros ajustáveis:** valor por ACS, valores ÓTIMO da eSF e custeio da eMulti ficam numa tabela de parâmetros por competência, e não fixos no código, porque os valores mudam por portaria.
3. **Story 3.2:** gravar `valor_sugerido`, `valor_final` e `regra_id`. Com o uso, a taxa de aceite mostra se a regra está boa, e as correções do usuário mostram o que falta (ex.: o componente de 14.058).
4. **Lote (3.4 e 3.5):** para lotes, ACS e eSF já saem calculados. Os planos manuais aparecem como "pendente de revisão" na lista de municípios.

## Perguntas para o usuário (antes da story 3.3)
1. eSF: o que é o valor de **R$ 14.058** que aparece somado em vários municípios?
2. eSF: qual o critério para limitar as equipes novas quando o teto é muito maior do que o número de equipes atual?
3. eMulti: como você decide quantas equipes a mais propor (1, 2, 4…)? O CNES não explica: quase todos os municípios têm profissionais suficientes.
4. Saúde Bucal: como você calcula a perda?
5. ACS: nos municípios grandes (292740, 354780, 352310, 310350), você usou o teto de ACS em vez dos credenciados?
6. Em 2026, a eSF passou a R$ 6.000 por equipe em alguns municípios de TO: foi outra classificação?
