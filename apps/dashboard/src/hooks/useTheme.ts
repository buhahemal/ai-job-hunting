import { useCallback, useSyncExternalStore } from 'react';

type Theme = 'light' | 'dark';

export const THEME_STORAGE_KEY = 'theme';

function readStoredTheme(): Theme | null {
  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : null;
  } catch {
    return null;
  }
}

function persistTheme(theme: Theme): void {
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // Storage can be unavailable (private browsing, opaque origins); theme still applies for the session.
  }
}

export function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light';
  const stored = readStoredTheme();
  if (stored) return stored;
  if (typeof window.matchMedia === 'function') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'light';
}

// Module-level store so every useTheme consumer (e.g. the mobile and desktop
// toggles) shares one theme value instead of holding divergent copies.
const listeners = new Set<() => void>();
let currentTheme: Theme | null = null;

function getSnapshot(): Theme {
  currentTheme ??= getInitialTheme();
  return currentTheme;
}

function subscribe(notify: () => void): () => void {
  listeners.add(notify);
  return () => listeners.delete(notify);
}

function setTheme(theme: Theme): void {
  currentTheme = theme;
  const root = document.documentElement;
  root.classList.toggle('dark', theme === 'dark');
  root.style.colorScheme = theme;
  persistTheme(theme);
  listeners.forEach((notify) => notify());
}

/** Test-only: forget the cached theme so the next read re-derives it from storage. */
export function resetThemeStore(): void {
  currentTheme = null;
}

export default function useTheme() {
  const theme = useSyncExternalStore(subscribe, getSnapshot, () => 'light' as const);

  const toggleTheme = useCallback(() => {
    setTheme(getSnapshot() === 'dark' ? 'light' : 'dark');
  }, []);

  return { theme, toggleTheme };
}
