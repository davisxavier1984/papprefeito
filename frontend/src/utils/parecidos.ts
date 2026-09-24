/**
 * Municípios parecidos (Demais programas e Promoção à saúde): formatação da linha do modal.
 */
import type { ExemploParecido } from '../types';

/** regra_id gravado quando o consultor aplica a mediana dos parecidos */
export const REGRA_PARECIDOS = 'parecidos_v1';

export const competenciaCurta = (c: string) => `${c.slice(4)}/${c.slice(0, 4)}`;

export const resumoParecidos = (exemplos: ExemploParecido[], moeda: Intl.NumberFormat) =>
  exemplos
    .map((e) => `${e.municipio}/${e.uf} ${competenciaCurta(e.competencia)} ${moeda.format(e.valor)}`)
    .join(' · ');
