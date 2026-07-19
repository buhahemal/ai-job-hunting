import { Moon, Sun } from 'lucide-react';
import useTheme from '../hooks/useTheme';

interface ThemeToggleProps {
  className?: string;
  iconClassName?: string;
}

export default function ThemeToggle({
  className = '',
  iconClassName = 'h-4 w-4',
}: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className={`p-2 rounded-xl flex items-center justify-center transition-colors ${className}`}
    >
      {isDark ? <Sun className={iconClassName} /> : <Moon className={iconClassName} />}
    </button>
  );
}
