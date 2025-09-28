/**
 * CurrencyInput
 * - Melhor experiência de digitação para valores monetários (pt-BR)
 * - Sem formatação enquanto digitando; formata ao sair (blur)
 * - Aceita vírgula ou ponto como separador decimal
 * - Enter confirma; Esc cancela; Clear zera
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Input, type InputRef } from 'antd';

type Props = {
  value: number;
  onCommit: (value: number) => void;
  min?: number;
  disabled?: boolean;
  placeholder?: string;
  size?: 'small' | 'middle' | 'large';
  onEnter?: () => void;
  onEscape?: () => void;
  id?: string;
  name?: string;
};

const numberFormatter = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
const toNumberString = (n: number) => numberFormatter.format(Number.isFinite(n) ? n : 0);

const sanitizeDraft = (s: string) => s.replace(/[^0-9,.-]/g, '').replace(/\s+/g, '');

const parseNumber = (s: string): number => {
  if (!s) return 0;
  // Remove currency and espaços, remove milhar, troca vírgula por ponto
  const raw = sanitizeDraft(s).replace(/\./g, '').replace(',', '.');
  const n = Number(raw);
  if (!Number.isFinite(n)) return 0;
  return n < 0 ? 0 : n;
};

const formatDraftFromNumber = (n: number) => {
  // Mostra como número simples com vírgula enquanto edita
  const fixed = (Number.isFinite(n) ? n : 0).toFixed(2);
  const [int, dec] = fixed.split('.');
  return `${Number(int).toString()}${dec ? `,${dec}` : ''}`;
};

const CurrencyInput: React.FC<Props> = ({
  value,
  onCommit,
  min = 0,
  disabled,
  placeholder = '0,00',
  size = 'middle',
  onEnter,
  onEscape,
  id,
  name,
}) => {
  const [focused, setFocused] = useState(false);
  const [draft, setDraft] = useState<string>('');
  const lastCommitted = useRef<number>(value ?? 0);
  const inputRef = useRef<InputRef>(null);

  // Mantém rastro do valor externo para resetar em ESC
  useEffect(() => {
    if (!focused) {
      lastCommitted.current = value ?? 0;
    }
  }, [value, focused]);

  const displayValue = useMemo(() => {
    if (focused) return draft;
    return toNumberString(value ?? 0);
  }, [focused, draft, value]);

  const commit = useCallback(() => {
    const parsed = parseNumber(draft);
    const rounded = Math.round(parsed * 100) / 100; // 2 casas decimais
    const safe = Math.max(min, rounded);
    onCommit(safe);
  }, [draft, min, onCommit]);

  const handleFocus = () => {
    setFocused(true);
    setDraft(formatDraftFromNumber(value ?? 0));
    // posiciona caret no fim
    requestAnimationFrame(() => {
      const el = inputRef.current;
      if (el?.input) {
        const len = el.input.value.length;
        el.input.setSelectionRange(len, len);
      }
    });
  };

  const handleBlur = () => {
    commit();
    setFocused(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const next = sanitizeDraft(e.target.value);
    // Permite vírgula/ponto final sem quebrar digitação
    // Limita a um separador decimal
    const parts = next.split(/[,.]/);
    let normalized = parts[0];
    if (parts.length > 1) {
      normalized += ',' + parts.slice(1).join('').replace(/,/g, '').replace(/\./g, '');
    }
    setDraft(normalized);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      commit();
      onEnter?.();
    } else if (e.key === 'Escape') {
      // Cancela: volta ao valor anterior
      setDraft(formatDraftFromNumber(lastCommitted.current));
      onEscape?.();
      // Também encerra edição
      (e.target as HTMLInputElement).blur();
    }
  };

  const allowClear = focused && draft.length > 0;

  return (
    <Input
      ref={inputRef}
      id={id || 'currency-input'}
      name={name || 'currency'}
      value={displayValue}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      placeholder={placeholder}
      size={size}
      disabled={disabled}
      allowClear={allowClear}
      prefix="R$"
      style={{ width: '100%', textAlign: 'right' }}
      inputMode="decimal"
      pattern="[0-9.,]*"
    />
  );
};

export default CurrencyInput;
