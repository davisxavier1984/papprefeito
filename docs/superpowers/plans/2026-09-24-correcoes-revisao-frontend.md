# Correções da revisão do frontend — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir os defeitos C1–C10 da revisão de código do frontend e atualizar o épico 2 (stories 2.1–2.5 + registro da revisão de UX) para o estado do código depois do épico 3.

**Architecture:** O autosave passa a usar uma fila de salvamento de módulo (pura, testável) com `descarregar()`, chamada ao desmontar a tabela, antes de gerar PDF e antes de nova consulta. A consulta passa a carregar a seleção como variável da mutation e descarta respostas de uma seleção antiga. A página de lote ganha polling encadeado com proteção contra respostas fora de ordem e retomada via `sessionStorage`. A lógica nova fica em módulos sem dependências de React/AntD, testados com o runner nativo do Node (`node --test`, type stripping do Node 22.19), sem instalar pacotes.

**Tech Stack:** React 19.1, TypeScript ~5.8, Ant Design 5.27, Zustand 5, TanStack Query 5, Vite 7, Node 22.19 (`node:test`).

**Spec:** `docs/qa/assessments/2026-09-24-revisao-frontend.md` (seções 1 e 3).

## Modo de execução (orquestração)

- A sessão principal orquestra: **um agente por vez**, na ordem das tarefas: implementador → revisor → próxima tarefa.
- **Subagente não lança subagente.** Todo prompt de agente inclui: "Não use a ferramenta Agent nem lance subagentes."
- Branch de trabalho: `fix/revisao-frontend` (criada a partir de `chore/limpeza-seguranca` @ `0cb1594`).

## Global Constraints

- **Nunca** rodar `npm run build` em `frontend/` (sobrescreve `frontend/dist`, servido em produção). Build de verificação só com `npx vite build --outDir /tmp/claude-1000/maispap-build`.
- Nenhuma dependência nova (nem dev). Testes usam `node:test` e `node:assert/strict`.
- Nenhuma mudança de backend nem de contrato de API; o payload `MunicipioEditadoCreate` (inclusive `itens`/`origem`) não muda.
- Debounce do autosave continua 2000 ms.
- `cd frontend && npx tsc -p tsconfig.app.json --noEmit` → 0 erros.
- `cd frontend && npx eslint .` → no máximo 16 erros (todos pré-existentes); nenhum erro novo em arquivo tocado.
- Textos de interface e comentários em pt-BR, com acentuação correta; seguir o estilo dos arquivos vizinhos (comentários curtos, `const` arrow functions).
- Commits em pt-BR no padrão do repositório (`fix(escopo): ...`), terminando com:
  ```
  Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_0136kHzr4LrYg6XUKHvYpm6X
  ```

## Review Focus

1. **Troca de município durante o debounce** — a edição pendente deve ser gravada no município em que foi feita (payload capturado no `agendar`), nunca no novo. Teste: Task 1, "envia o payload capturado no agendamento".
2. **Salvamento falha antes do PDF** — o PDF não é gerado e o usuário vê erro. Teste: Task 1, "descarregar rejeita quando o envio falha" + verificação manual.
3. **Resposta da consulta chega depois de trocar a seleção** — é descartada (nem dados nem erro aplicados). Teste: Task 2, `mesmaSelecao`.
4. **Status do lote fora de ordem / falha isolada de rede** — o progresso nunca regride e uma falha isolada não apaga o lote. Teste: Task 3, `statusMaisRecente`.
5. **`sessionStorage` indisponível (modo privado, bloqueado)** — a página de lote funciona sem retomar. Teste: Task 3, armazenamento que lança.

---

### Task 1: Fila de salvamento do autosave (C1, C2, C10)

**Files:**
- Create: `frontend/src/utils/filaSalvamento.ts`
- Create: `frontend/tests/filaSalvamento.test.ts`
- Modify: `frontend/package.json` (script `test`)
- Modify: `frontend/src/hooks/useAutoSave.ts` (remover `timerRef`/`debounceMs`, usar a fila, exportar `descarregarAutosave`)
- Modify: `frontend/src/components/DataTable/FinancialTable.tsx:32` (`useAutoSave(2000)` → `useAutoSave()`)
- Modify: `frontend/src/pages/Dashboard.tsx` (`handleGerarPDF` e `handleGerarPDFDetalhado`)
- Modify: `frontend/src/hooks/useConsultarDados.ts` (`mutationFn`)

**Interfaces:**
- Produces: `criarFilaSalvamento<T>(debounceMs: number, relogio?: Relogio): FilaSalvamento<T>`; `FilaSalvamento<T> = { agendar(payload: T, enviar: (p: T) => Promise<unknown>): void; descarregar(): Promise<void>; temPendente(): boolean }`; em `hooks/useAutoSave.ts`: `export const descarregarAutosave: () => Promise<void>` e `useAutoSave()` sem parâmetro.

- [ ] **Step 1: Script de teste**

Em `frontend/package.json`, dentro de `"scripts"`, acrescentar depois de `"preview"`:

```json
    "test": "node --test \"tests/**/*.test.ts\""
```

- [ ] **Step 2: Escrever os testes (falham)**

`frontend/tests/filaSalvamento.test.ts`:

```ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { criarFilaSalvamento } from '../src/utils/filaSalvamento.ts';

// Relógio controlado: os timers só disparam quando o teste manda
const relogioFalso = () => {
  let proximo = 1;
  const timers = new Map<number, () => void>();
  return {
    relogio: {
      setTimeout: (fn: () => void) => {
        const id = proximo++;
        timers.set(id, fn);
        return id;
      },
      clearTimeout: (id: unknown) => {
        timers.delete(id as number);
      },
    },
    disparar: () => {
      const fns = [...timers.values()];
      timers.clear();
      fns.forEach((fn) => fn());
    },
    agendados: () => timers.size,
  };
};

const adiado = () => {
  let resolver!: () => void;
  let rejeitar!: (e: Error) => void;
  const promessa = new Promise<void>((res, rej) => {
    resolver = res;
    rejeitar = rej;
  });
  return { promessa, resolver, rejeitar };
};

test('envia só o último payload quando o timer dispara', async () => {
  const r = relogioFalso();
  const fila = criarFilaSalvamento<string>(2000, r.relogio);
  const enviados: string[] = [];
  const enviar = async (p: string) => {
    enviados.push(p);
  };
  fila.agendar('a', enviar);
  fila.agendar('b', enviar);
  assert.equal(r.agendados(), 1);
  r.disparar();
  await fila.descarregar();
  assert.deepEqual(enviados, ['b']);
});

test('envia o payload capturado no agendamento', async () => {
  const r = relogioFalso();
  const fila = criarFilaSalvamento<{ codigo: string }>(2000, r.relogio);
  const enviados: string[] = [];
  const payload = { codigo: '2900207' };
  fila.agendar(payload, async (p) => {
    enviados.push(p.codigo);
  });
  // Um novo agendamento de outro município só acontece com outro payload; o já
  // agendado é enviado como estava
  await fila.descarregar();
  assert.deepEqual(enviados, ['2900207']);
});

test('descarregar envia na hora e cancela o timer', async () => {
  const r = relogioFalso();
  const fila = criarFilaSalvamento<string>(2000, r.relogio);
  const enviados: string[] = [];
  fila.agendar('x', async (p) => {
    enviados.push(p);
  });
  await fila.descarregar();
  assert.deepEqual(enviados, ['x']);
  assert.equal(r.agendados(), 0);
  assert.equal(fila.temPendente(), false);
  r.disparar();
  assert.deepEqual(enviados, ['x']);
});

test('descarregar sem pendente resolve sem enviar', async () => {
  const fila = criarFilaSalvamento<string>(2000, relogioFalso().relogio);
  await fila.descarregar();
  assert.equal(fila.temPendente(), false);
});

test('descarregar espera o envio em curso', async () => {
  const r = relogioFalso();
  const fila = criarFilaSalvamento<string>(2000, r.relogio);
  const envio = adiado();
  let terminou = false;
  fila.agendar('x', () => envio.promessa);
  r.disparar();
  const espera = fila.descarregar().then(() => {
    terminou = true;
  });
  await Promise.resolve();
  assert.equal(terminou, false);
  envio.resolver();
  await espera;
  assert.equal(terminou, true);
});

test('descarregar rejeita quando o envio falha e a fila volta a funcionar', async () => {
  const fila = criarFilaSalvamento<string>(2000, relogioFalso().relogio);
  fila.agendar('x', async () => {
    throw new Error('falhou');
  });
  await assert.rejects(fila.descarregar(), /falhou/);
  assert.equal(fila.temPendente(), false);
  await fila.descarregar();
});

test('envios acontecem em ordem', async () => {
  const r = relogioFalso();
  const fila = criarFilaSalvamento<string>(2000, r.relogio);
  const ordem: string[] = [];
  const primeiro = adiado();
  fila.agendar('1', async (p) => {
    ordem.push(`inicio ${p}`);
    await primeiro.promessa;
    ordem.push(`fim ${p}`);
  });
  r.disparar();
  fila.agendar('2', async (p) => {
    ordem.push(`inicio ${p}`);
  });
  const espera = fila.descarregar();
  await Promise.resolve();
  primeiro.resolver();
  await espera;
  assert.deepEqual(ordem, ['inicio 1', 'fim 1', 'inicio 2']);
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `cd frontend && npm test`
Expected: FAIL — `Cannot find module '.../src/utils/filaSalvamento.ts'`.

- [ ] **Step 4: Implementar a fila**

`frontend/src/utils/filaSalvamento.ts`:

```ts
/**
 * Fila de salvamento com debounce (autosave da tabela de perdas).
 * Guarda só o último payload agendado e envia um de cada vez, em ordem.
 * `descarregar` envia o pendente na hora e espera o envio em curso: usado por quem
 * precisa do valor já gravado (PDF, nova consulta, saída da tela).
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
  let pendente: { payload: T; enviar: (payload: T) => Promise<unknown> } | null = null;
  let emCurso: Promise<unknown> | null = null;

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
    const envio = anterior.catch(() => undefined).then(() => item.enviar(item.payload));
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
      pendente = { payload, enviar };
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
```

- [ ] **Step 5: Rodar os testes**

Run: `cd frontend && npm test`
Expected: PASS, 7 testes.

- [ ] **Step 6: Ligar a fila no hook**

Em `frontend/src/hooks/useAutoSave.ts`:

1. Acrescentar import: `import { criarFilaSalvamento } from '../utils/filaSalvamento';`
2. Logo depois de `type SaveStatus = ...`, acrescentar:

```ts
// Uma fila para o app todo: a edição pendente sobrevive à desmontagem da tabela
// e pode ser gravada por quem precisa do valor salvo (PDF, nova consulta)
const filaAutosave = criarFilaSalvamento<MunicipioEditadoCreate>(2000);

/** Grava na hora a edição que ainda está no debounce e espera o envio em curso. */
export const descarregarAutosave = () => filaAutosave.descarregar();
```

3. Trocar `export const useAutoSave = (debounceMs = 2000) => {` por `export const useAutoSave = () => {` e remover `const timerRef = useRef<number | null>(null);` (e `useRef` do import do React, se não for mais usado).
4. Dentro de `triggerSave`, substituir o bloco de `// Clear existing timer` até o `}, debounceMs);` por:

```ts
      filaAutosave.agendar(payload, (p) => mutation.mutateAsync(p));
```

e as deps do `useCallback` passam a ser `[mutation, selectedCompetencia, selectedMunicipio?.codigo_ibge]`.

5. Substituir o effect `// Cleanup timer on unmount` por:

```ts
  // Ao sair da tela (troca de rota, de município ou "Limpar Seleções"), grava a
  // edição pendente em vez de descartá-la. O payload já tem o município da edição.
  useEffect(() => {
    return () => {
      filaAutosave.descarregar().catch(() => undefined);
    };
  }, []);
```

6. Em `frontend/src/components/DataTable/FinancialTable.tsx:32`, trocar `useAutoSave(2000)` por `useAutoSave()`.

- [ ] **Step 7: Gravar antes do PDF (C2)**

Em `frontend/src/pages/Dashboard.tsx`, importar `import { descarregarAutosave } from '../hooks/useAutoSave';` e, em `handleGerarPDF` e em `handleGerarPDFDetalhado`, logo depois de `setIsGenerating(true);` / `setIsGeneratingDetailed(true);` (dentro do `try`), acrescentar:

```ts
      // O PDF lê as perdas gravadas no servidor: grava antes a edição que está no debounce
      await descarregarAutosave();
```

Se o salvamento falhar, o `catch` existente mostra "Não foi possível gerar o relatório" e o PDF não é gerado.

- [ ] **Step 8: Gravar antes de nova consulta (C10)**

Em `frontend/src/hooks/useConsultarDados.ts`, importar `import { descarregarAutosave } from './useAutoSave';` e, no início do `mutationFn`, depois da checagem de parâmetros, acrescentar:

```ts
      // Grava a edição pendente antes de recarregar, para a tela não voltar a um valor antigo
      await descarregarAutosave();
```

(A Task 2 reescreve a assinatura do `mutationFn`; mantenha esta linha como primeira instrução depois da checagem.)

- [ ] **Step 9: Verificar**

Run: `cd frontend && npm test && npx tsc -p tsconfig.app.json --noEmit && npx eslint . | tail -3`
Expected: testes PASS; tsc sem saída; eslint com ≤ 16 erros, nenhum novo em `useAutoSave.ts`, `filaSalvamento.ts`, `Dashboard.tsx`, `useConsultarDados.ts`, `FinancialTable.tsx`, `tests/`.

- [ ] **Step 10: Commit**

```bash
git add frontend/package.json frontend/src/utils/filaSalvamento.ts frontend/tests/filaSalvamento.test.ts frontend/src/hooks/useAutoSave.ts frontend/src/components/DataTable/FinancialTable.tsx frontend/src/pages/Dashboard.tsx frontend/src/hooks/useConsultarDados.ts
git commit -m "fix(autosave): gravar a edição pendente ao sair da tela, antes do PDF e antes de nova consulta"
```

---

### Task 2: Descartar resposta de consulta de seleção antiga (C3)

**Files:**
- Create: `frontend/src/utils/selecao.ts`
- Create: `frontend/tests/selecao.test.ts`
- Modify: `frontend/src/hooks/useConsultarDados.ts`

**Interfaces:**
- Consumes: `descarregarAutosave` (Task 1), já chamado no `mutationFn`.
- Produces: `interface Selecao { codigo_ibge: string; competencia: string }`; `mesmaSelecao(a: Selecao, b: Selecao): boolean`. `useConsultarDados().consultar()` mantém a assinatura `() => void`.

- [ ] **Step 1: Testes (falham)**

`frontend/tests/selecao.test.ts`:

```ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mesmaSelecao } from '../src/utils/selecao.ts';

test('mesma seleção', () => {
  assert.equal(mesmaSelecao({ codigo_ibge: '290020', competencia: '202508' }, { codigo_ibge: '290020', competencia: '202508' }), true);
});

test('município diferente', () => {
  assert.equal(mesmaSelecao({ codigo_ibge: '290020', competencia: '202508' }, { codigo_ibge: '292740', competencia: '202508' }), false);
});

test('competência diferente', () => {
  assert.equal(mesmaSelecao({ codigo_ibge: '290020', competencia: '202508' }, { codigo_ibge: '290020', competencia: '202507' }), false);
});

test('seleção vazia nunca é igual', () => {
  assert.equal(mesmaSelecao({ codigo_ibge: '', competencia: '' }, { codigo_ibge: '', competencia: '' }), false);
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd frontend && npm test`
Expected: FAIL — módulo `selecao.ts` não encontrado.

- [ ] **Step 3: Implementar**

`frontend/src/utils/selecao.ts`:

```ts
/**
 * Município + competência de uma consulta. Usado para descartar respostas que chegam
 * depois de o usuário trocar a seleção.
 */
export interface Selecao {
  codigo_ibge: string;
  competencia: string;
}

export const mesmaSelecao = (a: Selecao, b: Selecao) =>
  !!a.codigo_ibge && !!a.competencia && a.codigo_ibge === b.codigo_ibge && a.competencia === b.competencia;
```

- [ ] **Step 4: Rodar os testes**

Run: `cd frontend && npm test`
Expected: PASS.

- [ ] **Step 5: Passar a seleção como variável da mutation**

Em `frontend/src/hooks/useConsultarDados.ts`:

1. Importar `import { mesmaSelecao, type Selecao } from '../utils/selecao';`.
2. Trocar o `mutationFn` para receber a seleção e usar só ela (não mais `selectedMunicipio`/`selectedCompetencia` do closure):

```ts
    mutationFn: async ({ codigo_ibge, competencia }: Selecao) => {
      if (!codigo_ibge || !competencia) {
        throw new Error('Parâmetros incompletos para consulta');
      }
      // Grava a edição pendente antes de recarregar, para a tela não voltar a um valor antigo
      await descarregarAutosave();

      const dados: DadosFinanciamento = await apiClient.consultarDadosFinanciamento(codigo_ibge, competencia);
      // ... resto igual, trocando selectedMunicipio.codigo_ibge por codigo_ibge
      //     e selectedCompetencia por competencia (inclusive no objeto `editados` do 404)
```

3. `onSuccess: ({ dados, editados }, selecao) => {` — atualizar o cache com `selecao.codigo_ibge`/`selecao.competencia` (sem o `if` sobre o closure) e, antes de mexer na store, acrescentar:

```ts
      // O usuário trocou de município/competência enquanto esta consulta estava em andamento
      const { selectedMunicipio: atualMun, selectedCompetencia: atualComp } = useMunicipioStore.getState();
      if (!mesmaSelecao(selecao, { codigo_ibge: atualMun?.codigo_ibge ?? '', competencia: atualComp })) return;
```

4. `onError: (err: any, selecao) => {` — mesma checagem no início (se a seleção mudou, `return` sem `setError`).
5. `consultar` lê a seleção da store no momento do clique:

```ts
    consultar: () => {
      const { selectedMunicipio: mun, selectedCompetencia: comp } = useMunicipioStore.getState();
      mutation.mutate({ codigo_ibge: mun?.codigo_ibge ?? '', competencia: comp });
    },
```

6. Remover da desestruturação de `useMunicipioStore()` o que deixar de ser usado (o `noUnusedLocals` acusa).

- [ ] **Step 6: Verificar**

Run: `cd frontend && npm test && npx tsc -p tsconfig.app.json --noEmit && npx eslint . | tail -3`
Expected: PASS; tsc sem saída; eslint ≤ 16 erros, nenhum novo nos arquivos tocados (os `no-explicit-any` pré-existentes do arquivo podem permanecer).

- [ ] **Step 7: Commit**

```bash
git add frontend/src/utils/selecao.ts frontend/tests/selecao.test.ts frontend/src/hooks/useConsultarDados.ts
git commit -m "fix(consulta): descartar resposta que chega depois de trocar município ou competência"
```

---

### Task 3: Relatórios em lote — duplo clique, polling, retomada e competência (C4–C7)

**Files:**
- Modify: `frontend/src/utils/municipiosLote.ts`
- Create: `frontend/tests/municipiosLote.test.ts`
- Modify: `frontend/src/pages/RelatoriosLote.tsx`
- Modify: `frontend/src/components/Selectors/SeletorVariosMunicipios.tsx:44-48`

**Interfaces:**
- Produces (em `utils/municipiosLote.ts`): `statusMaisRecente(atual: LoteStatus | null, novo: LoteStatus): LoteStatus`; `interface Armazenamento { getItem(k: string): string | null; setItem(k: string, v: string): void; removeItem(k: string): void }`; `guardarLoteAtivo(id: string | null, armazenamento?: Armazenamento | null): void`; `lerLoteAtivo(armazenamento?: Armazenamento | null): string | null`.

- [ ] **Step 1: Testes (falham)**

`frontend/tests/municipiosLote.test.ts`:

```ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { guardarLoteAtivo, lerLoteAtivo, statusMaisRecente } from '../src/utils/municipiosLote.ts';
import type { LoteStatus } from '../src/types/index.ts';

const lote = (mudanca: Partial<LoteStatus>): LoteStatus => ({
  id: 'l1',
  status: 'processando',
  competencia: '202508',
  tipos: ['prefeito'],
  total: 10,
  processados: 0,
  arquivos: 0,
  calculados: 0,
  erros: [],
  criado_em: '2026-09-24T10:00:00',
  ...mudanca,
});

test('aceita o primeiro status', () => {
  const novo = lote({ processados: 2 });
  assert.equal(statusMaisRecente(null, novo), novo);
});

test('ignora resposta com menos processados', () => {
  const atual = lote({ processados: 5 });
  assert.equal(statusMaisRecente(atual, lote({ processados: 3 })), atual);
});

test('não volta de concluído para processando', () => {
  const atual = lote({ status: 'concluido', processados: 10 });
  assert.equal(statusMaisRecente(atual, lote({ processados: 9 })), atual);
});

test('aceita avanço e conclusão', () => {
  const concluido = lote({ status: 'concluido', processados: 10 });
  assert.equal(statusMaisRecente(lote({ processados: 9 }), concluido), concluido);
});

test('outro lote substitui o atual', () => {
  const novo = lote({ id: 'l2' });
  assert.equal(statusMaisRecente(lote({ status: 'concluido' }), novo), novo);
});

const memoria = () => {
  const m = new Map<string, string>();
  return {
    getItem: (k: string) => m.get(k) ?? null,
    setItem: (k: string, v: string) => void m.set(k, v),
    removeItem: (k: string) => void m.delete(k),
  };
};

test('guarda, lê e limpa o lote ativo', () => {
  const a = memoria();
  guardarLoteAtivo('l1', a);
  assert.equal(lerLoteAtivo(a), 'l1');
  guardarLoteAtivo(null, a);
  assert.equal(lerLoteAtivo(a), null);
});

test('armazenamento indisponível não quebra', () => {
  const quebrado = {
    getItem: () => {
      throw new Error('bloqueado');
    },
    setItem: () => {
      throw new Error('bloqueado');
    },
    removeItem: () => {
      throw new Error('bloqueado');
    },
  };
  assert.doesNotThrow(() => guardarLoteAtivo('l1', quebrado));
  assert.equal(lerLoteAtivo(quebrado), null);
  assert.equal(lerLoteAtivo(null), null);
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd frontend && npm test`
Expected: FAIL — `statusMaisRecente` não exportado.

- [ ] **Step 3: Implementar em `utils/municipiosLote.ts`**

Trocar o import para `import type { LoteStatus, MunicipioLote } from '../types';` e acrescentar ao fim:

```ts
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
```

- [ ] **Step 4: Rodar os testes**

Run: `cd frontend && npm test`
Expected: PASS.

- [ ] **Step 5: Página de lote**

Em `frontend/src/pages/RelatoriosLote.tsx`:

1. Importar `guardarLoteAtivo, lerLoteAtivo, statusMaisRecente` de `../utils/municipiosLote`.
2. Novo estado `const [iniciando, setIniciando] = useState(false);` e `gerar` passa a ser:

```ts
  const gerar = async () => {
    if (iniciando) return;
    setIniciando(true);
    try {
      baixadoRef.current = null;
      const novo = await apiClient.criarLote({ competencia, tipos, municipios: listaSelecionados, sem_perdas: 'regras' });
      guardarLoteAtivo(novo.id);
      setLote(novo);
    } catch {
      message.error('Não foi possível iniciar a geração dos relatórios.');
    } finally {
      setIniciando(false);
    }
  };
```

3. Retomar ao montar (depois de `gerar`):

```ts
  // Retoma o acompanhamento de um lote iniciado antes de sair da página
  useEffect(() => {
    const id = lerLoteAtivo();
    if (!id) return;
    apiClient
      .statusLote(id)
      .then((status) => setLote((atual) => atual ?? status))
      .catch(() => guardarLoteAtivo(null));
  }, []);
```

4. Substituir o effect de polling (`setInterval`) por polling encadeado:

```ts
  // Acompanha o andamento. Uma chamada por vez; respostas fora de ordem são ignoradas
  // e só desiste depois de 3 falhas seguidas.
  const loteId = lote?.id;
  const loteStatus = lote?.status;
  useEffect(() => {
    if (!loteId || loteStatus !== 'processando') return;
    let cancelado = false;
    let falhas = 0;
    let timer: number | undefined;
    const acompanhar = async () => {
      try {
        const novo = await apiClient.statusLote(loteId);
        falhas = 0;
        if (!cancelado) setLote((atual) => statusMaisRecente(atual, novo));
      } catch {
        falhas += 1;
        if (falhas >= 3) {
          if (!cancelado) {
            message.error('Perdi o acompanhamento da geração. Gere novamente.');
            guardarLoteAtivo(null);
            setLote(null);
          }
          return;
        }
      }
      if (!cancelado) timer = window.setTimeout(acompanhar, 2000);
    };
    timer = window.setTimeout(acompanhar, 2000);
    return () => {
      cancelado = true;
      window.clearTimeout(timer);
    };
  }, [loteId, loteStatus, message]);
```

5. No effect de conclusão (o que usa `baixadoRef`), logo depois de `baixadoRef.current = lote.id;`, acrescentar `guardarLoteAtivo(null);`. Se houver tratamento de `status === 'erro'` em outro ponto, limpar ali também; se não houver, acrescentar ao mesmo effect: `if (lote?.status === 'erro') guardarLoteAtivo(null);` num effect próprio com deps `[lote?.status]` — escolha a forma que o eslint (`react-hooks/exhaustive-deps`) aceitar sem aviso novo.
6. Botão: `loading={iniciando || gerando}` e `disabled={!podeGerar || iniciando}`.

- [ ] **Step 6: Competência apagável (C5)**

Em `frontend/src/components/Selectors/SeletorVariosMunicipios.tsx`, importar `useRef` e trocar o effect das linhas 44-48 por:

```ts
  // Sugere a última competência uma única vez; depois o usuário pode apagar e digitar outra
  const competenciaSugeridaRef = useRef(false);
  useEffect(() => {
    if (competenciaSugeridaRef.current || !ultimaCompetencia?.competencia) return;
    competenciaSugeridaRef.current = true;
    if (!competencia) onCompetenciaChange(ultimaCompetencia.competencia);
  }, [ultimaCompetencia, competencia, onCompetenciaChange]);
```

- [ ] **Step 7: Verificar**

Run: `cd frontend && npm test && npx tsc -p tsconfig.app.json --noEmit && npx eslint . | tail -3`
Expected: PASS; tsc sem saída; eslint ≤ 16 erros, nenhum novo em `RelatoriosLote.tsx`, `SeletorVariosMunicipios.tsx`, `municipiosLote.ts`, `tests/`.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/utils/municipiosLote.ts frontend/tests/municipiosLote.test.ts frontend/src/pages/RelatoriosLote.tsx frontend/src/components/Selectors/SeletorVariosMunicipios.tsx
git commit -m "fix(lote): evitar lote duplicado, progresso que regride, lote perdido ao sair e competência que não apaga"
```

---

### Task 4: Modal de preenchimento e valores de referência (C8, C9)

**Files:**
- Modify: `frontend/src/components/DataTable/PreenchimentoAutomatico.tsx:45-58, 117-124`
- Modify: `frontend/src/pages/Admin/ValoresReferencia.tsx:26-29, 138-147`

**Interfaces:** nenhuma nova.

Sem teste automatizado (componentes React sem infraestrutura de teste no projeto); a verificação é `tsc` + `eslint` + roteiro manual no fim do plano.

- [ ] **Step 1: Limpar o estado a cada abertura e ignorar resposta antiga**

Em `PreenchimentoAutomatico.tsx`, trocar o effect das linhas 45-58 por:

```ts
  useEffect(() => {
    if (!open || !selectedMunicipio?.codigo_ibge || !selectedCompetencia) return;
    // Cada abertura começa do zero: nada da busca anterior fica na tela se esta falhar
    let atual = true;
    setCarregando(true);
    setErro(null);
    setAviso(null);
    setPlanos([]);
    setSelecionados({});
    apiClient
      .getSugestaoPreenchimento(selectedMunicipio.codigo_ibge, selectedCompetencia)
      .then((r) => {
        if (!atual) return;
        setPlanos(r.planos);
        setAviso(r.aviso ?? null);
        setSelecionados(Object.fromEntries(r.planos.filter((p) => p.aplicavel).map((p) => [p.indice, true])));
      })
      .catch((e) => {
        if (atual) setErro(e?.message || 'Não foi possível calcular a sugestão.');
      })
      .finally(() => {
        if (atual) setCarregando(false);
      });
    return () => {
      atual = false;
    };
  }, [open, selectedMunicipio?.codigo_ibge, selectedCompetencia]);
```

- [ ] **Step 2: Estado vazio e texto no carregamento**

No mesmo arquivo, importar `Empty` do `antd` e trocar o ramo `carregando ? (...) : (planos.map(...))` para:

```tsx
        {carregando ? (
          <div style={{ textAlign: 'center', padding: 32 }}>
            <Spin tip="Calculando a sugestão…">
              <div style={{ minHeight: 48 }} />
            </Spin>
          </div>
        ) : !erro && planos.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Nenhum plano com cálculo automático para este município." />
        ) : (
          planos.map((p) => {
            /* ...inalterado... */
          })
        )}
```

- [ ] **Step 3: Erro na listagem de valores de referência**

Em `ValoresReferencia.tsx`:

```ts
  const { data: valores = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['valores-referencia'],
    queryFn: () => apiClient.listarValoresReferencia(),
  });
```

e, dentro do `<Space direction="vertical">` do Card da tabela, antes do `Input.Search`:

```tsx
          {isError && (
            <Alert
              type="error"
              showIcon
              message="Não foi possível carregar os valores de referência. O cadastro fica indisponível até carregar."
              action={
                <Button size="small" onClick={() => refetch()}>
                  Tentar novamente
                </Button>
              }
            />
          )}
```

- [ ] **Step 4: Verificar**

Run: `cd frontend && npm test && npx tsc -p tsconfig.app.json --noEmit && npx eslint . | tail -3`
Expected: PASS; tsc sem saída; eslint ≤ 16 erros, nenhum novo nos dois arquivos.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/DataTable/PreenchimentoAutomatico.tsx frontend/src/pages/Admin/ValoresReferencia.tsx
git commit -m "fix(preenchimento): limpar sugestão antiga ao reabrir e mostrar erro ao listar valores de referência"
```

---

### Task 5: Atualizar o épico 2 (stories 2.1–2.5 e registro da revisão de UX)

**Files:**
- Create: `docs/qa/assessments/epic-2-ux-review.md`
- Modify: `docs/stories/2.1.fundacao-motion-e-revisao-ux.md` … `2.5.microinteracoes-e-acessibilidade.md`
- Modify: `docs/prd/epic-2-frontend-ux-animacoes.md` (seção "Estado atual", itens 30 e referências de linha)

**Interfaces:**
- Consumes: o código no HEAD depois das Tasks 1–4 (as linhas mudaram de novo) e `docs/qa/assessments/2026-09-24-revisao-frontend.md` (seções 2 e 3).

Documentação: sem testes. Não alterar status das stories (continuam Draft) nem as seções QA Results/Dev Agent Record.

- [ ] **Step 1: Registro da revisão de UX**

Criar `docs/qa/assessments/epic-2-ux-review.md` no formato do AC1 da story 2.1: os achados 1–50, cada um com arquivo:linha **reancorado no HEAD atual** (conferir com `grep -n`/leitura, não copiar do relatório), prioridade (Alta/Média/Baixa) e story responsável (2.2–2.5) ou "fora de escopo"/"nova story" com justificativa. Achado 30: "Resolvido em `9d19d19`; C1/C2/C10 corrigidos em `fix/revisao-frontend` — só regressão na 2.4". Achados 42 e C7 (lote perdido ao sair): registrar que a retomada foi implementada na Task 3 deste plano.

- [ ] **Step 2: Corrigir cada story**

Aplicar os itens "Crítico" e "Deveria" da seção 3 de `docs/qa/assessments/2026-09-24-revisao-frontend.md`, reancorando toda referência arquivo:linha no HEAD atual. Em especial:
- 2.1: AC1 aponta para `epic-2-ux-review.md` (50 achados); linha de base do bundle = "medir com `npx vite build --outDir /tmp/maispap-base` no HEAD antes de iniciar" (remover 1.349.737); decisão `LazyMotion` + `m` desde a 2.1; roteiro manual com Menu da Sidebar, `/relatorios-lote`, `/admin/valores-referencia`.
- 2.2: 5 rotas; as duas rotas admin com `requireSuperuser`; `Menu`/`Divider` da Sidebar nas Restrições.
- 2.3: preenchimento automático nos AC3/AC4; Task 3.4 obrigatória.
- 2.4: AC1 vira regressão (e mencionar a fila `utils/filaSalvamento.ts` e `descarregarAutosave`); remover a Task 1.2; AC2 com `itens`; AC3 substitui só o bloco Status preservando o botão "Preencher automaticamente" e `onAplicado`; preenchimento em lote no AC4/AC9; barra de status em 375 px no AC6. O indicador "Alterações pendentes" deve usar `temPendente()` da fila (expor pelo hook).
- 2.5: AC4 relativo à linha de base; AC11 restrito a `motion`/CSS do épico **ou** desligar o movimento do AntD com reduced-motion (registrar as duas opções para o PO); telas novas no AC3/AC8/AC10; AC2 "fechar também quando a consulta parte de `/dashboard`".
- Acrescentar em cada story uma linha no Change Log: `| 2026-09-24 | 1.1 | Atualizada após o épico 3 e a revisão do frontend | SM |`.

- [ ] **Step 3: Épico**

Em `docs/prd/epic-2-frontend-ux-animacoes.md`: marcar o item 30 como resolvido, acrescentar referência a `epic-2-ux-review.md` para os achados 31–50, e registrar as duas decisões pendentes do PO (cor da diferença; `colorPrimary`/contraste) numa seção "Decisões pendentes".

- [ ] **Step 4: Conferência**

Run: `grep -rn "1.349.737\|index-bSt5rp5M" docs/stories docs/prd/epic-2-frontend-ux-animacoes.md`
Expected: nenhuma ocorrência (exceto, se houver, em texto histórico explicitamente marcado como "valor antigo").

- [ ] **Step 5: Commit**

```bash
git add docs/qa/assessments/epic-2-ux-review.md docs/stories/2.*.md docs/prd/epic-2-frontend-ux-animacoes.md
git commit -m "docs(epic-2): atualizar stories 2.1–2.5 e revisão de UX após o épico 3"
```

---

## Verificação final (orquestrador + usuário)

1. Revisão da branch inteira (`git diff chore/limpeza-seguranca..fix/revisao-frontend`) por um agente revisor.
2. `cd frontend && npm test && npx tsc -p tsconfig.app.json --noEmit && npx eslint . | tail -3` e build de verificação `npx vite build --outDir /tmp/claude-1000/maispap-build` (registrar o tamanho do JS).
3. Roteiro manual (usuário, no navegador, aba Network aberta):
   - Editar uma perda e, em menos de 2 s, clicar em "Relatórios em lote" → um `PUT/POST` de município editado sai com o valor novo.
   - "Preencher automaticamente" → Aplicar → clicar logo em "Relatório PAP Prefeito" → o PDF traz os valores aplicados.
   - Consultar A, trocar para B antes da resposta → a tabela não mostra A com B selecionado.
   - Relatórios em lote: duplo clique em "Gerar" → só um lote; sair e voltar durante a geração → o progresso reaparece e o ZIP baixa; apagar a competência → o campo fica vazio.
   - Reabrir "Preencher automaticamente" com o backend fora do ar → só o erro aparece, "Aplicar" desabilitado.
