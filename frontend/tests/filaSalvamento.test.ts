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

// Dá tempo para as cadeias de promises internas da fila (não controladas pelo
// relógio falso, que só controla os `setTimeout` do debounce) terminarem de assentar.
const aguardarMicrotarefas = () => new Promise((res) => setTimeout(res, 0));

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
  const enviar = async (p: { codigo: string }) => {
    enviados.push(p.codigo);
  };

  fila.agendar({ codigo: '2900207' }, enviar);
  r.disparar();
  await fila.descarregar();

  // Um segundo agendamento, com outro payload, feito depois de o primeiro já ter sido
  // enviado: cada envio deve levar o payload que estava vigente no momento do agendar
  fila.agendar({ codigo: '3100104' }, enviar);
  await fila.descarregar();

  assert.deepEqual(enviados, ['2900207', '3100104']);
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
  let chamadas = 0;
  fila.agendar('x', async () => {
    chamadas++;
  });
  await fila.descarregar();
  assert.equal(chamadas, 1);

  chamadas = 0;
  await fila.descarregar();
  assert.equal(chamadas, 0);
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

test('descarregar rejeita quando o envio falha e a fila volta a funcionar depois da retentativa', async () => {
  const fila = criarFilaSalvamento<string>(2000, relogioFalso().relogio);
  fila.agendar('x', async () => {
    throw new Error('falhou');
  });
  // Primeira falha: o item volta a ser pendente para uma retentativa
  await assert.rejects(fila.descarregar(), /falhou/);
  assert.equal(fila.temPendente(), true);

  // A retentativa também falha: descarta o item, a fila não fica travada
  await assert.rejects(fila.descarregar(), /falhou/);
  assert.equal(fila.temPendente(), false);
  await fila.descarregar();
});

test('falha no envio pelo timer → descarregar reenvia e resolve quando o reenvio dá certo', async () => {
  const r = relogioFalso();
  const fila = criarFilaSalvamento<string>(2000, r.relogio);
  let tentativa = 0;
  const enviados: string[] = [];
  fila.agendar('x', async (p) => {
    tentativa++;
    if (tentativa === 1) throw new Error('falhou');
    enviados.push(p);
  });
  r.disparar();
  await aguardarMicrotarefas();
  assert.equal(fila.temPendente(), true, 'item falho deve voltar a ser pendente');

  await fila.descarregar();
  assert.deepEqual(enviados, ['x']);
  assert.equal(tentativa, 2);
  assert.equal(fila.temPendente(), false);
});

test('falha no envio pelo timer e no reenvio → descarregar rejeita e a próxima descarga resolve', async () => {
  const r = relogioFalso();
  const fila = criarFilaSalvamento<string>(2000, r.relogio);
  let tentativas = 0;
  fila.agendar('x', async () => {
    tentativas++;
    throw new Error('falhou de novo');
  });
  r.disparar();
  await aguardarMicrotarefas();
  assert.equal(fila.temPendente(), true);

  await assert.rejects(fila.descarregar(), /falhou de novo/);
  assert.equal(tentativas, 2);
  assert.equal(fila.temPendente(), false);

  // A fila não fica travada: a próxima descarga resolve mesmo sem pendente
  await fila.descarregar();
});

test('falha com pendente mais novo → só o mais novo é enviado', async () => {
  const r = relogioFalso();
  const fila = criarFilaSalvamento<string>(2000, r.relogio);
  const primeiraTentativa = adiado();
  const enviados: string[] = [];

  fila.agendar('a', () => primeiraTentativa.promessa);
  r.disparar(); // dispara o envio de 'a', que fica pendurado até rejeitarmos

  // Enquanto 'a' ainda está em voo, chega uma edição mais nova
  fila.agendar('b', async (p) => {
    enviados.push(p);
  });

  primeiraTentativa.rejeitar(new Error('falhou'));
  await aguardarMicrotarefas();

  // 'a' falhou, mas 'b' já é o pendente mais novo: 'a' não deve substituí-lo
  assert.equal(fila.temPendente(), true);

  await fila.descarregar();
  assert.deepEqual(enviados, ['b']);
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
