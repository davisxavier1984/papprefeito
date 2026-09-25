/**
 * Fila de salvamento com debounce (autosave da tabela de perdas).
 * Guarda só o último payload agendado e envia um de cada vez, em ordem.
 * `descarregar` envia o pendente na hora e espera o envio em curso: usado por quem
 * precisa do valor já gravado (PDF, nova consulta, saída da tela).
 * Se um envio falha e ninguém agendou nada mais novo enquanto ele estava em voo, o
 * item falho volta a ser o pendente (sem reagendar timer) para uma única retentativa
 * no próximo `agendar`/`descarregar`; se essa retentativa falhar de novo, o item é
 * descartado e a fila segue livre.
 * Sem dependências de React, para poder ser testado com `node --test`.
 */

export interface Relogio {
  setTimeout: (fn: () => void, ms: number) => unknown;
  clearTimeout: (id: unknown) => void;
}

const relogioPadrao: Relogio = {
  setTimeout: (fn, ms) => globalThis.setTimeout(fn, ms),
  clearTimeout: (id) => globalThis.clearTimeout(id as ReturnType<typeof setTimeout>),
};

export interface FilaSalvamento<T> {
  agendar: (payload: T, enviar: (payload: T) => Promise<unknown>) => void;
  descarregar: () => Promise<void>;
  temPendente: () => boolean;
}

export const criarFilaSalvamento = <T>(
  debounceMs: number,
  relogio: Relogio = relogioPadrao
): FilaSalvamento<T> => {
  let timer: unknown = null;
  let pendente:
    | { payload: T; enviar: (payload: T) => Promise<unknown>; retentativa?: boolean; geracao: number }
    | null = null;
  let emCurso: Promise<unknown> | null = null;
  // Incrementada a cada `agendar`: identifica qual foi o último item agendado, para
  // saber (na hora de uma falha) se algo mais novo já tomou o lugar do item que falhou -
  // inclusive quando esse item mais novo já foi retirado da fila por um `descarregar`.
  let geracao = 0;

  const enviarAgora = (): Promise<unknown> => {
    if (timer !== null) {
      relogio.clearTimeout(timer);
      timer = null;
    }
    const item = pendente;
    pendente = null;
    if (!item) return emCurso ?? Promise.resolve();

    // Espera o envio anterior terminar (com sucesso ou erro) antes de mandar o próximo
    const anterior = emCurso ?? Promise.resolve();
    const envio = anterior
      .catch(() => undefined)
      .then(() => item.enviar(item.payload))
      .catch((erro) => {
        // Se ninguém agendou nada mais novo enquanto este envio estava em voo, guarda o
        // item para uma retentativa (sem reagendar timer: só um novo agendar ou um
        // descarregar explícito reenviam). Uma retentativa que falha de novo é descartada,
        // para a fila não ficar travada.
        // A comparação de geração cobre também o caso em que o item mais novo já foi
        // retirado da fila (por um `descarregar` concorrente) antes deste falhar: mesmo
        // com `pendente === null`, a geração atual já avançou e este item não volta.
        if (!item.retentativa && pendente === null && geracao === item.geracao) {
          pendente = { ...item, retentativa: true };
        }
        throw erro;
      });
    emCurso = envio;
    envio
      .finally(() => {
        if (emCurso === envio) emCurso = null;
      })
      .catch(() => undefined);
    return envio;
  };

  return {
    agendar: (payload, enviar) => {
      geracao += 1;
      pendente = { payload, enviar, geracao };
      if (timer !== null) relogio.clearTimeout(timer);
      timer = relogio.setTimeout(() => {
        timer = null;
        // O erro do envio automático é tratado por quem enviou (status do autosave)
        enviarAgora().catch(() => undefined);
      }, debounceMs);
    },
    descarregar: async () => {
      await enviarAgora();
    },
    temPendente: () => pendente !== null,
  };
};
