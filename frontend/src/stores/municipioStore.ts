/**
 * Store Zustand para gerenciamento de estado global da aplicação
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  AppStore,
  Municipio,
  DadosFinanciamento,
  MunicipioEditado,
  DadosProcessados,
  ResumoFinanceiro
} from '../types';

// Estado inicial
const initialState = {
  // Seleções atuais
  selectedUF: '',
  selectedMunicipio: null,
  selectedCompetencia: '',

  // Dados carregados
  dadosFinanciamento: null,
  dadosEditados: null,

  // Estados de UI
  isLoading: false,
  error: null,

  // Dados processados para tabela
  dadosProcessados: [],
  resumoFinanceiro: null,
};

/**
 * Store principal da aplicação usando Zustand
 */
export const useMunicipioStore = create<AppStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // ================================
        // AÇÕES DE SELEÇÃO
        // ================================

        setSelectedUF: (uf: string) => {
          set(() => ({
            selectedUF: uf,
            // Reset município quando UF muda
            selectedMunicipio: null,
            // Limpar dados quando muda seleção
            dadosFinanciamento: null,
            dadosEditados: null,
            dadosProcessados: [],
            resumoFinanceiro: null,
            error: null
          }), false, 'setSelectedUF');
        },

        setSelectedMunicipio: (municipio: Municipio | null) => {
          set(() => ({
            selectedMunicipio: municipio,
            // Limpar dados quando muda município
            dadosFinanciamento: null,
            dadosEditados: null,
            dadosProcessados: [],
            resumoFinanceiro: null,
            error: null
          }), false, 'setSelectedMunicipio');
        },

        setSelectedCompetencia: (competencia: string) => {
          set(() => ({
            selectedCompetencia: competencia,
            // Limpar dados quando muda competência
            dadosFinanciamento: null,
            dadosEditados: null,
            dadosProcessados: [],
            resumoFinanceiro: null,
            error: null
          }), false, 'setSelectedCompetencia');
        },

        // ================================
        // AÇÕES DE DADOS
        // ================================

        setDadosFinanciamento: (dados: DadosFinanciamento | null) => {
          set({ dadosFinanciamento: dados }, false, 'setDadosFinanciamento');

          // Se temos dados, processar automaticamente
          if (dados) {
            get().processarDados();
          }
        },

        setDadosEditados: (dados: MunicipioEditado | null) => {
          set({ dadosEditados: dados }, false, 'setDadosEditados');

          // Reprocessar dados quando editados mudam
          if (get().dadosFinanciamento) {
            get().processarDados();
          }
        },

        // ================================
        // AÇÕES DE UI
        // ================================

        setLoading: (loading: boolean) => {
          set({ isLoading: loading }, false, 'setLoading');
        },

        setError: (error: string | null) => {
          set({ error }, false, 'setError');
        },

        // ================================
        // AÇÕES DE DADOS PROCESSADOS
        // ================================

        updateDadosProcessados: (dados: DadosProcessados[]) => {
          set({ dadosProcessados: dados }, false, 'updateDadosProcessados');

          // Recalcular resumo financeiro automaticamente
          get().calcularResumoFinanceiro();
        },

        updateResumoFinanceiro: (resumo: ResumoFinanceiro) => {
          set({ resumoFinanceiro: resumo }, false, 'updateResumoFinanceiro');
        },

        // ================================
        // AÇÕES AUXILIARES
        // ================================

        resetState: () => {
          set(initialState, false, 'resetState');
        },

        // ================================
        // MÉTODOS DE PROCESSAMENTO
        // ================================

        processarDados: () => {
          const { dadosFinanciamento, dadosEditados } = get();

          if (!dadosFinanciamento?.resumosPlanosOrcamentarios) {
            return;
          }

          const dadosProcessados: DadosProcessados[] = dadosFinanciamento.resumosPlanosOrcamentarios.map((resumo, index) => {
            const percaMensal = dadosEditados?.perca_recurso_mensal?.[index] || 0;

            return {
              recurso: resumo.dsPlanoOrcamentario,
              recurso_real: resumo.vlEfetivoRepasse,
              perca_recurso_mensal: percaMensal,
              recurso_potencial: resumo.vlEfetivoRepasse + percaMensal,
              recurso_real_anual: resumo.vlEfetivoRepasse * 12,
              recurso_potencial_anual: (resumo.vlEfetivoRepasse + percaMensal) * 12,
              diferenca: (resumo.vlEfetivoRepasse + percaMensal) * 12 - resumo.vlEfetivoRepasse * 12
            };
          });

          set({ dadosProcessados }, false, 'processarDados');
          get().calcularResumoFinanceiro();
        },

        calcularResumoFinanceiro: () => {
          const { dadosProcessados } = get();

          if (!dadosProcessados.length) {
            set({ resumoFinanceiro: null }, false, 'calcularResumoFinanceiro');
            return;
          }

          const totalPercaMensal = dadosProcessados.reduce((sum, item) => sum + item.perca_recurso_mensal, 0);
          const totalDiferencaAnual = dadosProcessados.reduce((sum, item) => sum + item.diferenca, 0);
          const totalRecebido = dadosProcessados.reduce((sum, item) => sum + item.recurso_real, 0);
          const totalRealAnual = dadosProcessados.reduce((sum, item) => sum + item.recurso_real_anual, 0);

          const percentualPerdaAnual = totalRealAnual > 0 ? (totalDiferencaAnual / totalRealAnual) * 100 : 0;

          const resumo: ResumoFinanceiro = {
            total_perca_mensal: totalPercaMensal,
            total_diferenca_anual: totalDiferencaAnual,
            percentual_perda_anual: percentualPerdaAnual,
            total_recebido: totalRecebido
          };

          set({ resumoFinanceiro: resumo }, false, 'calcularResumoFinanceiro');
        },

      }),
      {
        name: 'municipio-store', // Chave para localStorage
        partialize: (state) => ({
          // Persistir apenas seleções, não dados sensíveis
          selectedUF: state.selectedUF,
          selectedMunicipio: state.selectedMunicipio,
          selectedCompetencia: state.selectedCompetencia,
        }),
      }
    ),
    {
      name: 'municipio-store', // Nome para DevTools
    }
  )
);

// ================================
// HOOKS AUXILIARES
// ================================

/**
 * Hook para verificar se temos dados completos para consulta
 */
export const useCanConsult = () => {
  const { selectedUF, selectedMunicipio, selectedCompetencia } = useMunicipioStore();

  return !!(
    selectedUF &&
    selectedMunicipio?.codigo_ibge &&
    selectedCompetencia &&
    selectedCompetencia.length === 6
  );
};

/**
 * Hook para verificar se temos dados carregados
 */
export const useHasDados = () => {
  const { dadosFinanciamento } = useMunicipioStore();

  return !!(
    dadosFinanciamento?.resumosPlanosOrcamentarios &&
    dadosFinanciamento.resumosPlanosOrcamentarios.length > 0
  );
};

/**
 * Hook para obter informações do município atual
 */
export const useMunicipioInfo = () => {
  const { selectedUF, selectedMunicipio, selectedCompetencia } = useMunicipioStore();

  if (!selectedMunicipio) return null;

  return {
    uf: selectedUF,
    codigo: selectedMunicipio.codigo_ibge,
    nome: selectedMunicipio.nome,
    competencia: selectedCompetencia
  };
};

/**
 * Hook para atualizar perca de recurso de um item específico
 */
export const useUpdatePercaRecurso = () => {
  const { dadosEditados, setDadosEditados, dadosProcessados } = useMunicipioStore();

  return (index: number, novoValor: number) => {
    // Atualizar dados editados
    const percasAtuais = dadosEditados?.perca_recurso_mensal || Array(dadosProcessados.length).fill(0);
    const novasPercas = [...percasAtuais];
    novasPercas[index] = novoValor;

    const novosEditados: MunicipioEditado = {
      codigo_ibge: dadosEditados?.codigo_ibge || '',
      competencia: dadosEditados?.competencia || '',
      perca_recurso_mensal: novasPercas,
      data_edicao: new Date().toISOString()
    };

    setDadosEditados(novosEditados);
  };
};