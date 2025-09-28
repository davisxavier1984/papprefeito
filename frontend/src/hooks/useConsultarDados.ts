/**
 * Hook: useConsultarDados
 * - Executa a consulta de financiamento
 * - Carrega dados editados existentes (ou inicializa zeros)
 * - Atualiza o store e processamentos
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, queryKeys } from '../services/api';
import { useMunicipioStore } from '../stores/municipioStore';
import type { DadosFinanciamento, MunicipioEditado } from '../types';

export const useConsultarDados = () => {
  const queryClient = useQueryClient();
  const {
    selectedMunicipio,
    selectedCompetencia,
    setLoading,
    setError,
    setDadosFinanciamento,
    setDadosEditados,
  } = useMunicipioStore();

  const mutation = useMutation({
    mutationFn: async () => {
      if (!selectedMunicipio?.codigo_ibge || !selectedCompetencia) {
        throw new Error('Parâmetros incompletos para consulta');
      }

      // 1) Buscar dados de financiamento
      const dados: DadosFinanciamento = await apiClient.consultarDadosFinanciamento(
        selectedMunicipio.codigo_ibge,
        selectedCompetencia
      );

      // 2) Tentar carregar dados editados
      let editados: MunicipioEditado | null = null;
      try {
        editados = await apiClient.getMunicipioEditado(
          selectedMunicipio.codigo_ibge,
          selectedCompetencia
        );
      } catch (err: any) {
        // Se não existir (404), iniciamos com zeros
        if (err?.error_code === '404') {
          const zeros = (dados.resumosPlanosOrcamentarios || []).map(() => 0);
          editados = {
            codigo_ibge: selectedMunicipio.codigo_ibge,
            competencia: selectedCompetencia,
            perca_recurso_mensal: zeros,
            data_edicao: new Date().toISOString(),
          };
        } else {
          throw err;
        }
      }

      // Retornar ambos para uso no onSuccess
      return { dados, editados } as { dados: DadosFinanciamento; editados: MunicipioEditado };
    },
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: ({ dados, editados }) => {
      // Atualizar cache de queries relevantes
      if (selectedMunicipio?.codigo_ibge && selectedCompetencia) {
        queryClient.setQueryData(
          queryKeys.financiamento(selectedMunicipio.codigo_ibge, selectedCompetencia),
          dados
        );
        queryClient.setQueryData(
          queryKeys.editado(selectedMunicipio.codigo_ibge, selectedCompetencia),
          editados
        );
      }

      // Atualizar store e processar
      setDadosFinanciamento(dados);
      setDadosEditados(editados);
    },
    onError: (err: any) => {
      const message = err?.message || err?.details?.message || 'Erro ao consultar dados';
      setError(message);
    },
    onSettled: () => {
      setLoading(false);
    },
  });

  return {
    consultar: () => mutation.mutate(),
    isLoading: mutation.isPending,
    isSuccess: mutation.isSuccess,
    isError: mutation.isError,
    error: mutation.error,
  };
};

export default useConsultarDados;

