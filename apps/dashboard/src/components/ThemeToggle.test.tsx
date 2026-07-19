// @vitest-environment jsdom
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { describe, expect, it, beforeEach, afterEach } from 'vitest';
import ThemeToggle from './ThemeToggle';
import { getInitialTheme, resetThemeStore, THEME_STORAGE_KEY } from '../hooks/useTheme';

function createStorageMock(): Storage {
  let store: Record<string, string> = {};
  return {
    get length() {
      return Object.keys(store).length;
    },
    key: (index: number) => Object.keys(store)[index] ?? null,
    getItem: (key: string) => (key in store ? store[key] : null),
    setItem: (key: string, value: string) => {
      store[key] = String(value);
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
}

describe('ThemeToggle Component & Theme Persistence', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'localStorage', {
      value: createStorageMock(),
      configurable: true,
      writable: true,
    });
    resetThemeStore();
    document.documentElement.classList.remove('dark');
  });

  afterEach(cleanup);

  it('defaults to light mode and renders the switch-to-dark control', () => {
    render(<ThemeToggle />);

    expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeDefined();
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('toggles to dark mode: adds the dark class and persists the choice', () => {
    render(<ThemeToggle />);

    fireEvent.click(screen.getByRole('button', { name: /switch to dark mode/i }));

    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe('dark');
    expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeDefined();
  });

  it('toggles back to light mode and persists it', () => {
    window.localStorage.setItem(THEME_STORAGE_KEY, 'dark');
    render(<ThemeToggle />);

    fireEvent.click(screen.getByRole('button', { name: /switch to light mode/i }));

    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe('light');
  });

  it('keeps multiple toggle instances in sync when one is clicked', () => {
    render(
      <>
        <ThemeToggle />
        <ThemeToggle />
      </>,
    );

    const [first] = screen.getAllByRole('button', { name: /switch to dark mode/i });
    fireEvent.click(first);

    expect(screen.getAllByRole('button', { name: /switch to light mode/i })).toHaveLength(2);
    expect(screen.queryAllByRole('button', { name: /switch to dark mode/i })).toHaveLength(0);
  });

  it('getInitialTheme honors a stored preference over any system default', () => {
    window.localStorage.setItem(THEME_STORAGE_KEY, 'dark');
    expect(getInitialTheme()).toBe('dark');

    window.localStorage.setItem(THEME_STORAGE_KEY, 'light');
    expect(getInitialTheme()).toBe('light');
  });

  it('getInitialTheme falls back to light when storage is unavailable', () => {
    Object.defineProperty(window, 'localStorage', {
      value: undefined,
      configurable: true,
      writable: true,
    });
    expect(getInitialTheme()).toBe('light');
  });
});
