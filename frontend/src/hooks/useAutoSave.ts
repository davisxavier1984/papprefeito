/**
 * Hook: useAutoSave
 * - Realiza upsert dos dados editados com debounce
 * - Fornece status visual (saving, saved, error)
 */

import { useCallback, useEffect, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, queryKeys } from '../services/api';
import { useMunicipioStore } from '../stores/municipioStore';
import type { MunicipioEditadoCreate, MunicipioEditado } from '../types';
import { criarFilaSalvamento } from '../utils/filaSalvamento';

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

// Uma fila para o app todo: a edição pendente sobrevive à desmontagem da tabela
// e pode ser gravada por quem precisa do valor salvo (PDF, nova consulta)
const filaAutosave = criarFilaSalvamento<MunicipioEditadoCreate>(2000);

/** Grava na hora a edição que ainda está no debounce e espera o envio em curso. */
export const descarregarAutosave = () => filaAutosave.descarregar();

export const useAutoSave = () => {
  const queryClient = useQueryClient();
  const { selectedMunicipio, selectedCompetencia } = useMunicipioStore();
  const [status, setStatus] = useState<SaveStatus>('idle');
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: async (payload: MunicipioEditadoCreate) => {
      return apiClient.upsertMunicipioEditado(payload);
    },
    onMutate: async (payload) => {
      setStatus('saving');
      setError(null);
      // Optimistic cache update
      if (payload.codigo_ibge && payload.competencia) {
        const prev = queryClient.getQueryData<MunicipioEditado>(
          queryKeys.editado(payload.codigo_ibge, payload.competencia)
        );
        const optimistic: MunicipioEditado = {
          codigo_ibge: payload.codigo_ibge,
          competencia: payload.competencia,
          perda_recurso_mensal: payload.perda_recurso_mensal,
          perda_vinculo_mensal: payload.perda_vinculo_mensal,
          perda_qualidade_mensal: payload.perda_qualidade_mensal,
          data_edicao: new Date().toISOString(),
        };
        queryClient.setQueryData(
          queryKeys.editado(payload.codigo_ibge, payload.competencia),
          optimistic
        );
        return { prev };
      }
      return { prev: undefined };
    },
    onError: (err: any, payload, context) => {
      // Rollback: usa o município/competência do payload que falhou (2º argumento do
      // onError), não a seleção atual da tela — evita reverter os dados errados se o
      // usuário já trocou de município/competência enquanto o envio estava em voo.
      const prev = (context as any)?.prev as MunicipioEditado | undefined;
      if (prev && payload.codigo_ibge && payload.competencia) {
        queryClient.setQueryData(
          queryKeys.editado(payload.codigo_ibge, payload.competencia),
          prev
        );
      }
      setStatus('error');
      setError(err?.message || 'Erro ao salvar');
    },
    onSuccess: (saved) => {
      // Sync cache with server response
      queryClient.setQueryData(
        queryKeys.editado(saved.codigo_ibge, saved.competencia),
        saved
      );
      setStatus('saved');
    },
  });

  // Debounced trigger
  const triggerSave = useCallback(
    (overridePerdas?: number[]) => {
      if (!selectedMunicipio?.codigo_ibge || !selectedCompetencia) return;
      // Lê a store no momento da chamada (o set do Zustand é síncrono), e não o
      // valor do render em que triggerSave foi criado: assim a edição recém-confirmada
      // entra no payload. Ler aqui, e não no disparo do timer, evita salvar dados de
      // outro município se o usuário trocar de seleção durante o debounce.
      const editados = useMunicipioStore.getState().dadosEditados;
      const perdas = overridePerdas ?? editados?.perda_recurso_mensal;
      if (!perdas) return;

      const payload: MunicipioEditadoCreate = {
        codigo_ibge: selectedMunicipio.codigo_ibge,
        competencia: selectedCompetencia,
        perda_recurso_mensal: perdas,
        // Decomposição por componente (SIAPS)
        perda_vinculo_mensal: editados?.perda_vinculo_mensal,
        perda_qualidade_mensal: editados?.perda_qualidade_mensal,
      };

      // Nome do plano de cada posição (story 3.2). Só envia quando a tabela e o
      // array têm o mesmo tamanho, para não rotular posições erradas em registros antigos.
      const { dadosProcessados, sugestoesAplicadas } = useMunicipioStore.getState();
      if (dadosProcessados.length === perdas.length) {
        payload.itens = perdas.map((valor, i) => {
          // Valor calculado (stories 3.3/3.6): mantém a origem enquanto o usuário não alterar;
          // se alterar, vira "manual" mas guarda a sugestão para o aprendizado
          const sug = sugestoesAplicadas[i];
          return {
            plano: dadosProcessados[i].recurso,
            valor,
            origem:
              sug && Math.abs(valor - sug.valor_aplicado) < 0.005
                ? sug.regra_id.startsWith('emulti_estimativa') ? 'estimativa' : 'regra'
                : 'manual',
            regra_id: sug?.regra_id ?? null,
            valor_sugerido: sug?.valor_sugerido ?? null,
          };
        });
      }

      filaAutosave.agendar(payload, (p) => mutation.mutateAsync(p));
    },
    [mutation, selectedCompetencia, selectedMunicipio?.codigo_ibge]
  );

  // Ao sair da tela (troca de rota, de município ou "Limpar Seleções"), grava a
  // edição pendente em vez de descartá-la. O payload já tem o município da edição.
  useEffect(() => {
    return () => {
      filaAutosave.descarregar().catch(() => undefined);
    };
  }, []);

  return {
    triggerSave,
    status,
    isSaving: status === 'saving',
    isSaved: status === 'saved',
    isError: status === 'error',
    error,
  };
};

export default useAutoSave;

