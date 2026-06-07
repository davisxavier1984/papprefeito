/**
 * Formatação de moeda (BRL) compartilhada.
 *
 * Fonte única de verdade para exibir valores em Real, evitando divergências de
 * casas decimais entre componentes (ex.: tabela financeira × card SIAPS).
 */

const brlFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/** Formata um número como moeda BRL com 2 casas decimais (ex.: "R$ 1.234,56"). */
export const formatCurrencyBRL = (value: number): string =>
  brlFormatter.format(Number.isFinite(value) ? value : 0);

export default formatCurrencyBRL;
