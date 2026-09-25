/**
 * Município + competência de uma consulta. Usado para descartar respostas que chegam
 * depois de o usuário trocar a seleção.
 */
export interface Selecao {
  codigo_ibge: string;
  competencia: string;
}

export const mesmaSelecao = (a: Selecao, b: Selecao) =>
  !!a.codigo_ibge && !!a.competencia && a.codigo_ibge === b.codigo_ibge && a.competencia === b.competencia;
