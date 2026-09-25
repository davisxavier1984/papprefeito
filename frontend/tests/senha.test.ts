import { test } from 'node:test';
import assert from 'node:assert/strict';
import { gerarSenha, problemaNaSenha } from '../src/utils/senha.ts';

test('senha forte não tem problema', () => {
  assert.equal(problemaNaSenha('Senha123'), null);
});

test('aponta cada regra de força', () => {
  assert.match(problemaNaSenha('')!, /insira/);
  assert.match(problemaNaSenha('Ab1')!, /8 caracteres/);
  assert.match(problemaNaSenha('senha123')!, /maiúscula/);
  assert.match(problemaNaSenha('SENHA123')!, /minúscula/);
  assert.match(problemaNaSenha('SenhaForte')!, /número/);
});

test('senha gerada sempre passa nas regras e varia', () => {
  const geradas = new Set<string>();
  for (let i = 0; i < 200; i++) {
    const s = gerarSenha();
    assert.equal(problemaNaSenha(s), null, s);
    assert.equal(s.length, 12);
    geradas.add(s);
  }
  assert.ok(geradas.size > 190);
});
