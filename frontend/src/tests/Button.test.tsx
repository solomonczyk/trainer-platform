import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Button from '@/components/ui/Button';

describe('Button', () => {
  it('renders children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('applies variant classes', () => {
    render(<Button variant="primary">Primary</Button>);
    const btn = screen.getByText('Primary');
    expect(btn.className).toContain('bg');
  });

  it('renders as submit type', () => {
    render(<Button type="submit">Submit</Button>);
    const btn = screen.getByText('Submit');
    expect(btn.getAttribute('type')).toBe('submit');
  });
});
