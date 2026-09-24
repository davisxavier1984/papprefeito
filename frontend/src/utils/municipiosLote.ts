/**
 * Utilitários da seleção de vários municípios (relatórios em lote)
 */
import type { LoteStatus, MunicipioLote } from '../types';

export const competenciaValida = (c: string) =>
  /^\d{6}$/.test(c) && Number(c.slice(4)) >= 1 && Number(c.slice(4)) <= 12;

export const ordenarMunicipios = (selecionados: Record<string, MunicipioLote>) =>
  Object.values(selecionados).sort((a, b) => (a.uf + a.nome).localeCompare(b.uf + b.nome, 'pt-BR'));

/** Ignora respostas de status fora de ordem: o andamento de um lote nunca volta. */
export const statusMaisRecente = (atual: LoteStatus | null, novo: LoteStatus): LoteStatus => {
  if (!atual || atual.id !== novo.id) return novo;
  if (atual.status !== 'processando') return atual;
  if (novo.status === 'processando' && novo.processados < atual.processados) return atual;
  return novo;
};

// Lote em andamento, para retomar o acompanhamento ao voltar à página
const CHAVE_LOTE_ATIVO = 'maispap:lote-ativo';

export interface Armazenamento {
  getItem: (chave: string) => string | null;
  setItem: (chave: string, valor: string) => void;
  removeItem: (chave: string) => void;
}

const sessao = (): Armazenamento | null => {
  try {
    return globalThis.sessionStorage ?? null;
  } catch {
    return null;
  }
};

export const guardarLoteAtivo = (id: string | null, armazenamento: Armazenamento | null = sessao()) => {
  try {
    if (id) armazenamento?.setItem(CHAVE_LOTE_ATIVO, id);
    else armazenamento?.removeItem(CHAVE_LOTE_ATIVO);
  } catch {
    // Sem armazenamento (modo privado/bloqueado): só não retoma
  }
};

export const lerLoteAtivo = (armazenamento: Armazenamento | null = sessao()): string | null => {
  try {
    return armazenamento?.getItem(CHAVE_LOTE_ATIVO) ?? null;
  } catch {
    return null;
  }
};
