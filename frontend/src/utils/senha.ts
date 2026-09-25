/**
 * Regras de senha (as mesmas do backend) e gerador de senha forte
 */

export const REGRAS_SENHA = 'Mínimo 8 caracteres, com letras maiúsculas, minúsculas e números';

/** Retorna o motivo de a senha ser fraca, ou null se ela atende às regras */
export const problemaNaSenha = (senha: string): string | null => {
  if (!senha) return 'Por favor, insira uma senha';
  if (senha.length < 8) return 'A senha deve ter no mínimo 8 caracteres';
  if (!/[A-Z]/.test(senha)) return 'A senha deve conter pelo menos uma letra maiúscula';
  if (!/[a-z]/.test(senha)) return 'A senha deve conter pelo menos uma letra minúscula';
  if (!/[0-9]/.test(senha)) return 'A senha deve conter pelo menos um número';
  return null;
};

/** Validador para as `rules` do Form do antd */
export const validarSenha = (_: unknown, value: string) => {
  const problema = problemaNaSenha(value);
  return problema ? Promise.reject(new Error(problema)) : Promise.resolve();
};

// Sem caracteres que se confundem ao ditar ou copiar à mão (I, l, O, 0, 1)
const MAIUSCULAS = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
const MINUSCULAS = 'abcdefghijkmnopqrstuvwxyz';
const NUMEROS = '23456789';
const TODOS = MAIUSCULAS + MINUSCULAS + NUMEROS;

/** Índice aleatório uniforme em [0, n) usando crypto (rejeita o viés do módulo) */
const indiceAleatorio = (n: number): number => {
  const limite = Math.floor(0x100000000 / n) * n;
  const buf = new Uint32Array(1);
  do {
    crypto.getRandomValues(buf);
  } while (buf[0] >= limite);
  return buf[0] % n;
};

const sortear = (conjunto: string) => conjunto[indiceAleatorio(conjunto.length)];

/** Gera uma senha aleatória de 12 caracteres que sempre atende às regras */
export const gerarSenha = (tamanho = 12): string => {
  const chars = [sortear(MAIUSCULAS), sortear(MINUSCULAS), sortear(NUMEROS)];
  while (chars.length < tamanho) chars.push(sortear(TODOS));
  // Embaralha (Fisher–Yates) para as classes obrigatórias não ficarem sempre no início
  for (let i = chars.length - 1; i > 0; i--) {
    const j = indiceAleatorio(i + 1);
    [chars[i], chars[j]] = [chars[j], chars[i]];
  }
  return chars.join('');
};
