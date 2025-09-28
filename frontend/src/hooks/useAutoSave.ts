/**
 * Hook: useAutoSave
 * - Realiza upsert dos dados editados com debounce
 * - Fornece status visual (saving, saved, error)
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, queryKeys } from '../services/api';
import { useMunicipioStore } from '../stores/municipioStore';
import type { MunicipioEditadoCreate, MunicipioEditado } from '../types';

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export const useAutoSave = (debounceMs = 2000) => {
  const queryClient = useQueryClient();
  const { selectedMunicipio, selectedCompetencia, dadosEditados } = useMunicipioStore();
  const [status, setStatus] = useState<SaveStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

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
          perca_recurso_mensal: payload.perca_recurso_mensal,
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
    onError: (err: any, _payload, context) => {
      // Rollback
      const prev = (context as any)?.prev as MunicipioEditado | undefined;
      if (prev && selectedMunicipio?.codigo_ibge && selectedCompetencia) {
        queryClient.setQueryData(
          queryKeys.editado(selectedMunicipio.codigo_ibge, selectedCompetencia),
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
    (overridePercas?: number[]) => {
      if (!selectedMunicipio?.codigo_ibge || !selectedCompetencia) return;
      const percas = overridePercas ?? dadosEditados?.perca_recurso_mensal;
      if (!percas) return;

      const payload: MunicipioEditadoCreate = {
        codigo_ibge: selectedMunicipio.codigo_ibge,
        competencia: selectedCompetencia,
        perca_recurso_mensal: percas,
      };

      // Clear existing timer
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
      }
      // Schedule save
      timerRef.current = window.setTimeout(() => {
        mutation.mutate(payload);
      }, debounceMs);
    },
    [debounceMs, dadosEditados?.perca_recurso_mensal, mutation, selectedCompetencia, selectedMunicipio?.codigo_ibge]
  );

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
      }
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

