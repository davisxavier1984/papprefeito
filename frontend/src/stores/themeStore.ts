/**
 * Store Zustand para o tema (claro/escuro/sistema)
 * - Padrão: 'system' (segue o prefers-color-scheme do SO)
 * - A escolha manual ('light'/'dark') é persistida em localStorage
 * - Aplica o atributo data-theme no <html> para as variáveis CSS comutarem
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeMode = 'light' | 'dark' | 'system';

const prefersDark = (): boolean =>
  typeof window !== 'undefined' &&
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(prefers-color-scheme: dark)').matches;

const resolveIsDark = (mode: ThemeMode): boolean =>
  mode === 'system' ? prefersDark() : mode === 'dark';

const applyDomTheme = (isDark: boolean): void => {
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }
};

interface ThemeState {
  mode: ThemeMode;
  isDark: boolean;
  setMode: (mode: ThemeMode) => void;
  toggle: () => void;
  /** Recalcula isDark a partir do SO (usado pelo listener de matchMedia em modo 'system') */
  syncSystem: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: 'system',
      isDark: resolveIsDark('system'),

      setMode: (mode) => {
        const isDark = resolveIsDark(mode);
        applyDomTheme(isDark);
        set({ mode, isDark });
      },

      toggle: () => {
        const next: ThemeMode = get().isDark ? 'light' : 'dark';
        get().setMode(next);
      },

      syncSystem: () => {
        if (get().mode !== 'system') return;
        const isDark = prefersDark();
        applyDomTheme(isDark);
        set({ isDark });
      },
    }),
    {
      name: 'theme-storage',
      partialize: (state) => ({ mode: state.mode }),
      // Ao reidratar do localStorage, reaplica o tema resolvido ao DOM/estado
      onRehydrateStorage: () => (state) => {
        if (!state) return;
        const isDark = resolveIsDark(state.mode);
        applyDomTheme(isDark);
        state.isDark = isDark;
      },
    }
  )
);

// Aplica o tema imediatamente no carregamento do módulo (evita flash antes da hidratação)
applyDomTheme(useThemeStore.getState().isDark);

// Reage à mudança do tema do SO quando em modo 'system'
if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
  window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', () => useThemeStore.getState().syncSystem());
}

/** Hook utilitário: retorna true se o tema atual é escuro */
export const useIsDark = (): boolean => useThemeStore((s) => s.isDark);
