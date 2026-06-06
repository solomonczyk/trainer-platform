'use client';

import React from 'react';
import Input from "@/components/ui/Input";

interface NumericActivityProps {
  value: string;
  onAnswer: (value: string) => void;
  disabled: boolean;
}

export function NumericActivity({ value, onAnswer, disabled }: NumericActivityProps) {
  return (
    <div className="max-w-xs">
      <Input
        type="number"
        value={value}
        onChange={(e) => onAnswer(e.target.value)}
        disabled={disabled}
        placeholder="Введите число..."
        className="text-lg"
      />
    </div>
  );
}
