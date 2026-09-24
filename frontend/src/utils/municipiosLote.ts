/**
 * Utilitários da seleção de vários municípios (relatórios em lote e estimativa eMulti)
 */
import type { MunicipioLote } from '../types';

export const competenciaValida = (c: string) =>
  /^\d{6}$/.test(c) && Number(c.slice(4)) >= 1 && Number(c.slice(4)) <= 12;

export const ordenarMunicipios = (selecionados: Record<string, MunicipioLote>) =>
  Object.values(selecionados).sort((a, b) => (a.uf + a.nome).localeCompare(b.uf + b.nome, 'pt-BR'));
