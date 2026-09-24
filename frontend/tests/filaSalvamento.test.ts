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
