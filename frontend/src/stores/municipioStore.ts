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
  ResumoFinanceiro,
  DetalhamentoPrograma
} from '../types';
import { processarProgramas } from '../utils/processarProgramas';

// UFs permitidas no sistema
const ALLOWED_UFS = ['BA', 'GO'];

/**
 * Valida se a UF do município é permitida no sistema
 */
const validateMunicipioUF = (municipio: Municipio | null): boolean => {
  if (!municipio) return true;

  const isValid = ALLOWED_UFS.includes(municipio.uf.toUpperCase());

  if (!isValid) {
    console.warn(
      `⚠️ Município de UF não permitida detectado: ${municipio.nome} - ${municipio.uf}. ` +
      `Este sistema só atende municípios da Bahia (BA) e Goiás (GO).`
    );
  }

  return isValid;
};

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

  // Dados processados para cards de programas
  dadosProgramas: [],
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
            dadosProgramas: [],
            error: null
          }), false, 'setSelectedUF');
        },

        setSelectedMunicipio: (municipio: Municipio | null) => {
          // Validar UF do município
          validateMunicipioUF(municipio);

          set(() => ({
            selectedMunicipio: municipio,
            // Limpar dados quando muda município
            dadosFinanciamento: null,
            dadosEditados: null,
            dadosProcessados: [],
            resumoFinanceiro: null,
            dadosProgramas: [],
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
            dadosProgramas: [],
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
            get().processarProgramas();
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

        updateDadosProgramas: (programas: DetalhamentoPrograma[]) => {
          set({ dadosProgramas: programas }, false, 'updateDadosProgramas');
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
            const perdaMensal = dadosEditados?.perda_recurso_mensal?.[index] || 0;

            return {
              recurso: resumo.dsPlanoOrcamentario,
              recurso_real: resumo.vlEfetivoRepasse,
              perda_recurso_mensal: perdaMensal,
              recurso_potencial: resumo.vlEfetivoRepasse + perdaMensal,
              recurso_real_anual: resumo.vlEfetivoRepasse * 12,
              recurso_potencial_anual: (resumo.vlEfetivoRepasse + perdaMensal) * 12,
              diferenca: (resumo.vlEfetivoRepasse + perdaMensal) * 12 - resumo.vlEfetivoRepasse * 12
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

          const totalPerdaMensal = dadosProcessados.reduce((sum, item) => sum + item.perda_recurso_mensal, 0);
          const totalDiferencaAnual = dadosProcessados.reduce((sum, item) => sum + item.diferenca, 0);
          const totalRecebido = dadosProcessados.reduce((sum, item) => sum + item.recurso_real, 0);
          const totalRealAnual = dadosProcessados.reduce((sum, item) => sum + item.recurso_real_anual, 0);

          const percentualPerdaAnual = totalRealAnual > 0 ? (totalDiferencaAnual / totalRealAnual) * 100 : 0;

          const resumo: ResumoFinanceiro = {
            total_perda_mensal: totalPerdaMensal,
            total_diferenca_anual: totalDiferencaAnual,
            percentual_perda_anual: percentualPerdaAnual,
            total_recebido: totalRecebido
          };

          set({ resumoFinanceiro: resumo }, false, 'calcularResumoFinanceiro');
        },

        processarProgramas: () => {
          const { dadosFinanciamento } = get();

          if (!dadosFinanciamento?.resumosPlanosOrcamentarios) {
            set({ dadosProgramas: [] }, false, 'processarProgramas');
            return;
          }

          const pagamento = dadosFinanciamento.pagamentos?.[0];
          const programas = processarProgramas(
            dadosFinanciamento.resumosPlanosOrcamentarios,
            pagamento
          );

          set({ dadosProgramas: programas }, false, 'processarProgramas');
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
 * Hook para atualizar perda de recurso de um item específico
 */
export const useUpdatePerdaRecurso = () => {
  const { dadosEditados, setDadosEditados, dadosProcessados } = useMunicipioStore();

  return (index: number, novoValor: number) => {
    // Atualizar dados editados
    const perdasAtuais = dadosEditados?.perda_recurso_mensal || Array(dadosProcessados.length).fill(0);
    const novasPerdas = [...perdasAtuais];
    novasPerdas[index] = novoValor;

    const novosEditados: MunicipioEditado = {
      codigo_ibge: dadosEditados?.codigo_ibge || '',
      competencia: dadosEditados?.competencia || '',
      perda_recurso_mensal: novasPerdas,
      data_edicao: new Date().toISOString()
    };

    setDadosEditados(novosEditados);
  };
};