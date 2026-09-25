/**
 * Extrai a mensagem de erro enviada pelo backend (campo `detail`)
 */
export const mensagemDeErro = (error: unknown, padrao: string): string => {
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  return typeof detail === 'string' ? detail : padrao;
};
