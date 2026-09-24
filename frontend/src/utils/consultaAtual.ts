/**
 * Diz se `id` ainda corresponde à consulta mais recente disparada (`idAtual`).
 * Usado para não desligar o loading global quando uma resposta atrasada de uma
 * consulta já substituída por outra mais nova termina de resolver.
 */
export const ehConsultaAtual = (id: number, idAtual: number): boolean => id === idAtual;
