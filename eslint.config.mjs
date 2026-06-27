import js from '@eslint/js';
import prettier from 'eslint-config-prettier';
import reactHooks from 'eslint-plugin-react-hooks';
import unicorn from 'eslint-plugin-unicorn';
import tseslint from 'typescript-eslint';

const namingRules = {
  '@typescript-eslint/naming-convention': [
    'error',
    {
      selector: 'default',
      format: ['camelCase'],
      leadingUnderscore: 'allow',
      trailingUnderscore: 'allow',
    },
    {
      selector: 'variable',
      format: ['camelCase', 'UPPER_CASE'],
      leadingUnderscore: 'allow',
    },
    {
      selector: 'function',
      format: ['camelCase', 'PascalCase'],
    },
    {
      selector: 'parameter',
      format: ['camelCase'],
      leadingUnderscore: 'allow',
    },
    {
      selector: 'typeLike',
      format: ['PascalCase'],
    },
    {
      selector: 'enumMember',
      format: ['PascalCase', 'UPPER_CASE'],
    },
    {
      selector: 'typeProperty',
      format: ['camelCase', 'snake_case', 'UPPER_CASE'],
    },
    {
      selector: 'objectLiteralProperty',
      filter: { regex: '^__html$', match: true },
      format: null,
    },
    {
      selector: 'objectLiteralProperty',
      modifiers: ['requiresQuotes'],
      format: null,
    },
    {
      selector: 'objectLiteralProperty',
      format: ['camelCase', 'snake_case'],
    },
    {
      selector: 'import',
      format: null,
    },
  ],
  'unicorn/filename-case': [
    'error',
    {
      cases: {
        camelCase: true,
        pascalCase: true,
        kebabCase: true,
      },
    },
  ],
};

export default tseslint.config(
  { ignores: ['**/dist/**', '**/node_modules/**', '**/coverage/**'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    plugins: {
      unicorn,
    },
    rules: {
      ...namingRules,
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', caughtErrorsIgnorePattern: '^_' },
      ],
    },
  },
  {
    files: ['apps/dashboard/src/**/*.{ts,tsx}'],
    plugins: {
      'react-hooks': reactHooks,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-hooks/set-state-in-effect': 'off',
    },
  },
  prettier,
);
