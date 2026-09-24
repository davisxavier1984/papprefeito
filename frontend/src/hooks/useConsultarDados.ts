/**
 * Hook: useConsultarDados
 * - Executa a consulta de financiamento
 * - Carrega dados editados existentes (ou inicializa zeros)
 * - Atualiza o store e processamentos
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, queryKeys } from '../services/api';
import { filtrarResumosMunicipais, useMunicipioStore } from '../stores/municipioStore';
import type { DadosFinanciamento, MunicipioEditado, SugestaoAplicada } from '../types';
import { descarregarAutosave } from './useAutoSave';
import { mesmaSelecao, type Selecao } from '../utils/selecao';
import { ehConsultaAtual } from '../utils/consultaAtual';

// Compartilhado entre todas as instâncias do hook (Sidebar e CompetenciaInput têm cada
// uma seu próprio useMutation, mas escrevem no mesmo isLoading global da store): identifica
// qual foi a última consulta disparada, para o onSettled de uma consulta obsoleta não
// desligar o loading enquanto uma consulta mais nova ainda está em andamento.
let ultimaConsulta = 0;

export const useConsultarDados = () => {
  const queryClient = useQueryClient();
  const { setLoading, setError, setDadosFinanciamento, setDadosEditados, setSugestoesAplicadas } =
    useMunicipioStore();

  const mutation = useMutation({
    mutationFn: async ({ codigo_ibge, competencia }: Selecao) => {
      if (!codigo_ibge || !competencia) {
        throw new Error('Parâmetros incompletos para consulta');
      }

      // Grava a edição pendente antes de recarregar, para a tela não voltar a um valor antigo.
      // Erro aqui é do autosave, não da consulta: relança com mensagem própria para o
      // usuário não confundir as duas falhas.
      try {
        await descarregarAutosave();
      } catch (err) {
        const mensagem = err instanceof Error ? err.message : 'erro desconhecido';
        throw new Error(`Não foi possível salvar a alteração anterior: ${mensagem}`);
      }

      // 1) Buscar dados de financiamento
      const dados: DadosFinanciamento = await apiClient.consultarDadosFinanciamento(codigo_ibge, competencia);

      // 2) Tentar carregar dados editados
      let editados: MunicipioEditado | null = null;
      try {
        editados = await apiClient.getMunicipioEditado(codigo_ibge, competencia);
      } catch (err: any) {
        // Se não existir (404), iniciamos com zeros
        if (err?.error_code === '404') {
          // Mesmo tamanho da tabela: só os planos da esfera municipal
          const zeros = filtrarResumosMunicipais(dados.resumosPlanosOrcamentarios || []).map(() => 0);
          editados = {
            codigo_ibge,
            competencia,
            perda_recurso_mensal: zeros,
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
      return { id: ++ultimaConsulta };
    },
    onSuccess: ({ dados, editados }, selecao) => {
      // O usuário trocou de município/competência enquanto esta consulta estava em andamento
      const { selectedMunicipio: atualMun, selectedCompetencia: atualComp } = useMunicipioStore.getState();
      if (!mesmaSelecao(selecao, { codigo_ibge: atualMun?.codigo_ibge ?? '', competencia: atualComp })) return;

      // Atualizar cache de queries relevantes
      queryClient.setQueryData(queryKeys.financiamento(selecao.codigo_ibge, selecao.competencia), dados);
      queryClient.setQueryData(queryKeys.editado(selecao.codigo_ibge, selecao.competencia), editados);

      // Posições que vieram do cálculo automático (story 3.3): mantém a origem nas próximas gravações
      const sugestoes: Record<number, SugestaoAplicada> = {};
      (editados.itens ?? []).forEach((item, i) => {
        if (item.regra_id && item.valor_sugerido != null) {
          sugestoes[i] = {
            regra_id: item.regra_id,
            valor_sugerido: item.valor_sugerido,
            valor_aplicado: item.origem === 'manual' ? item.valor_sugerido : item.valor,
          };
        }
      });

      // Atualizar store e processar
      setSugestoesAplicadas(sugestoes);
      setDadosFinanciamento(dados);
      setDadosEditados(editados);
    },
    onError: (err: any, selecao) => {
      // O usuário trocou de município/competência: o erro não é mais relevante
      const { selectedMunicipio: atualMun, selectedCompetencia: atualComp } = useMunicipioStore.getState();
      if (!mesmaSelecao(selecao, { codigo_ibge: atualMun?.codigo_ibge ?? '', competencia: atualComp })) return;

      const message = err?.message || err?.details?.message || 'Erro ao consultar dados';
      setError(message);
    },
    onSettled: (_data, _err, _selecao, context) => {
      // Só desliga o loading se esta ainda for a consulta mais recente: uma resposta
      // atrasada de uma consulta já substituída não pode reabilitar o botão Consultar
      // enquanto a consulta atual ainda está em voo.
      if (context && ehConsultaAtual(context.id, ultimaConsulta)) {
        setLoading(false);
      }
    },
  });

  return {
    consultar: () => {
      const { selectedMunicipio: mun, selectedCompetencia: comp } = useMunicipioStore.getState();
      mutation.mutate({ codigo_ibge: mun?.codigo_ibge ?? '', competencia: comp });
    },
    isLoading: mutation.isPending,
    isSuccess: mutation.isSuccess,
    isError: mutation.isError,
    error: mutation.error,
  };
};

export default useConsultarDados;

