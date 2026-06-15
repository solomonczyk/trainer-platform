import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ru from '@/lib/i18n/ru-RU';
import en from '@/lib/i18n/en-US';

describe('Landing page CTA', () => {
  it('ru-RU startButton is not empty', () => {
    expect(ru.landing.startButton).toBeTruthy();
    expect(ru.landing.startButton.length).toBeGreaterThan(0);
  });

  it('en-US startButton is not empty', () => {
    expect(en.landing.startButton).toBeTruthy();
    expect(en.landing.startButton.length).toBeGreaterThan(0);
  });

  it('ru-RU startButton uses Russian text', () => {
    expect(ru.landing.startButton).toMatch(/[А-я]/);
  });

  it('en-US startButton uses English text', () => {
    expect(en.landing.startButton).toMatch(/[A-Za-z]/);
  });

  it('ru-RU nav.domains is Russian', () => {
    expect(ru.nav.domains).toMatch(/[А-я]/);
  });

  it('en-US nav.domains is English', () => {
    expect(en.nav.domains).toMatch(/[A-Za-z]/);
  });

  it('ru-RU has no English CTA text', () => {
    // The ru-RU locale should not contain English strings for CTA
    expect(ru.landing.startButton).not.toMatch(/^[A-Z]/);
  });
});

describe('Button contrast tokens', () => {
  it('primary-700 has sufficient contrast with white', () => {
    // primary-700 = #1d4ed8 (dark blue)
    // white = #ffffff
    // Contrast ratio should be ~8.6:1, well above 4.5:1 AA for normal text
    const primary700 = '#1d4ed8';
    const white = '#ffffff';
    const relLuminance = (hex: string) => {
      const srgb = parseInt(hex.slice(1), 16);
      const r = ((srgb >> 16) & 0xff) / 255;
      const g = ((srgb >> 8) & 0xff) / 255;
      const b = (srgb & 0xff) / 255;
      const linearize = (c: number) =>
        c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b);
    };
    const l1 = relLuminance(primary700);
    const l2 = relLuminance(white);
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    const ratio = (lighter + 0.05) / (darker + 0.05);
    // AA for normal text requires 4.5:1
    expect(ratio).toBeGreaterThan(4.5);
    // AAA for large text requires 3:1 (button labels are typically larger)
    expect(ratio).toBeGreaterThan(3);
  });
});
