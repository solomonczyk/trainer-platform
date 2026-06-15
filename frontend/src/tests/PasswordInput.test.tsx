import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PasswordInput from '@/components/ui/PasswordInput';
import ru from '@/lib/i18n/ru-RU';
import en from '@/lib/i18n/en-US';

describe('PasswordInput', () => {
  it('renders with type="password" by default', () => {
    render(<PasswordInput id="test-pw" />);
    const el = document.getElementById('test-pw') as HTMLInputElement;
    expect(el).toBeInTheDocument();
    expect(el.type).toBe('password');
  });

  it('toggle changes type to text', () => {
    render(<PasswordInput id="test-toggle" />);
    const input = document.getElementById('test-toggle') as HTMLInputElement;
    expect(input.type).toBe('password');

    // Click the toggle button
    const toggle = screen.getByRole('button');
    fireEvent.click(toggle);
    expect(input.type).toBe('text');
  });

  it('toggle changes type back to password on second click', () => {
    render(<PasswordInput id="test-toggle2" />);
    const input = document.getElementById('test-toggle2') as HTMLInputElement;

    const toggle = screen.getByRole('button');
    fireEvent.click(toggle); // password → text
    expect(input.type).toBe('text');

    fireEvent.click(toggle); // text → password
    expect(input.type).toBe('password');
  });

  it('preserves value when toggling visibility', () => {
    render(<PasswordInput id="test-value" defaultValue="secret123" />);
    const input = document.getElementById('test-value') as HTMLInputElement;
    expect(input.value).toBe('secret123');

    // Toggle to visible
    const toggle = screen.getByRole('button');
    fireEvent.click(toggle);
    expect(input.type).toBe('text');
    expect(input.value).toBe('secret123');

    // Toggle back to hidden
    fireEvent.click(toggle);
    expect(input.type).toBe('password');
    expect(input.value).toBe('secret123');
  });

  it('renders label when provided', () => {
    render(<PasswordInput id="test-label" label="Password" />);
    expect(screen.getByText('Password')).toBeInTheDocument();
  });

  it('renders placeholder when provided', () => {
    render(<PasswordInput id="test-placeholder" placeholder="Enter password" />);
    const input = document.getElementById('test-placeholder') as HTMLInputElement;
    expect(input.placeholder).toBe('Enter password');
  });

  it('toggle button has aria-label', () => {
    render(<PasswordInput id="test-aria" />);
    const toggle = screen.getByRole('button');
    expect(toggle).toHaveAttribute('aria-label');
  });

  it('shows error message when error prop is set', () => {
    render(<PasswordInput id="test-error" error="Password is required" />);
    expect(screen.getByText('Password is required')).toBeInTheDocument();
  });

  it('forwards autocomplete attribute', () => {
    render(<PasswordInput id="test-ac" autoComplete="new-password" />);
    const input = document.getElementById('test-ac') as HTMLInputElement;
    expect(input.autocomplete).toBe('new-password');
  });
});

describe('Password i18n strings', () => {
  it('ru-RU has showPassword key', () => {
    expect(ru.auth.showPassword).toBe('Показать пароль');
  });

  it('ru-RU has hidePassword key', () => {
    expect(ru.auth.hidePassword).toBe('Скрыть пароль');
  });

  it('ru-RU has no English placeholder text', () => {
    // The passwordPlaceholder and confirmPasswordPlaceholder must use Russian
    expect(ru.auth.passwordPlaceholder).not.toMatch(/[A-Za-z]/);
    expect(ru.auth.confirmPasswordPlaceholder).not.toMatch(/[A-Za-z]/);
  });

  it('ru-RU confirmPasswordPlaceholder is Russian', () => {
    expect(ru.auth.confirmPasswordPlaceholder).toBe('Повторите пароль');
  });

  it('en-US has showPassword key', () => {
    expect(en.auth.showPassword).toBe('Show password');
  });

  it('en-US has hidePassword key', () => {
    expect(en.auth.hidePassword).toBe('Hide password');
  });

  it('en-US passwordPlaceholder is correct', () => {
    expect(en.auth.passwordPlaceholder).toBe('At least 6 characters');
  });

  it('en-US confirmPasswordPlaceholder is correct', () => {
    expect(en.auth.confirmPasswordPlaceholder).toBe('Repeat password');
  });
});
