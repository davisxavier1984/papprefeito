/**
 * Utilitários SIAPS no frontend.
 *
 * Mapeia a lacuna financeira por equipe (detalhe SIAPS) para cada linha de recurso
 * exibida na tabela, casando por substring do nome do recurso (mesma convenção de
 * processarProgramas.ts). Robusto a filtragem/ordem dos resumos.
 */
import type { DadosPagamento, SiapsGapResponse } from '../types';

// sgEquipe (SIAPS) → substring do nome do recurso (dsPlanoOrcamentario).
export const EQUIPE_SUBSTRING: Record<string, string> = {
  eSF: 'Equipes de Saúde da Família',
  eAP: 'Equipes de Saúde da Família',
  eSB: 'Saúde Bucal',
  eMulti: 'Multiprofissionais',
};

/**
 * Lacuna potencial decomposta por componente (Vínculo e Acompanhamento / Qualidade),
 * alinhada à lista de recursos. `null` significa que o componente NÃO se aplica àquele
 * recurso (não há registro SIAPS); um número (inclusive 0) significa que se aplica.
 *
 * Usa sempre o cenário POTENCIAL (lacuna total até "Ótimo"), conforme o Autopreencher.
 */
export interface ComponenteSugestao {
  vinculo: number | null;
  qualidade: number | null;
}

export function sugestoesPorComponente(
  gap: SiapsGapResponse | null,
  recursos: string[]
): ComponenteSugestao[] {
  return recursos.map((recurso) => {
    if (!gap) {
      return { vinculo: null, qualidade: null };
    }
    let vinculo: number | null = null;
    let qualidade: number | null = null;
    for (const d of gap.detalhe) {
      const substr = EQUIPE_SUBSTRING[d.sgEquipe];
      if (!substr || !recurso.includes(substr)) {
        continue;
      }
      const comp = (d.componente || '').toUpperCase();
      if (comp === 'CVAT') {
        vinculo = (vinculo ?? 0) + d.gap_potencial;
      } else if (comp === 'QUALIDADE') {
        qualidade = (qualidade ?? 0) + d.gap_potencial;
      }
    }
    return { vinculo, qualidade };
  });
}

/**
 * Valor ATUAL de cada componente (já contido no vlEfetivoRepasse), lido do pagamento.
 * Serve apenas como contexto na UI ("atual: R$ X") para deixar claro que a lacuna é um
 * ganho adicional — não duplica o recebido. `null` quando o campo não existe no pagamento.
 */
export interface ComponenteBase {
  vinculo: number | null;
  qualidade: number | null;
}

export function basePorComponente(
  pagamento: DadosPagamento | undefined,
  recursos: string[]
): ComponenteBase[] {
  return recursos.map((recurso) => {
    if (!pagamento) {
      return { vinculo: null, qualidade: null };
    }
    if (recurso.includes('Equipes de Saúde da Família')) {
      const vinculo = (pagamento.vlVinculoEsf ?? 0) + (pagamento.vlVinculoEap ?? 0);
      const qualidade = (pagamento.vlQualidadeEsf ?? 0) + (pagamento.vlQualidadeEap ?? 0);
      return { vinculo: vinculo || null, qualidade: qualidade || null };
    }
    if (recurso.includes('Saúde Bucal')) {
      return { vinculo: null, qualidade: pagamento.vlPagamentoEsb40hQualidade ?? null };
    }
    if (recurso.includes('Multiprofissionais')) {
      return { vinculo: null, qualidade: pagamento.vlPagamentoEmultiQualidade ?? null };
    }
    return { vinculo: null, qualidade: null };
  });
}
