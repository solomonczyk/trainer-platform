import React from "react";

interface FormattedContentProps {
  text: string;
  className?: string;
}

/**
 * Renders text content, automatically detecting numbered list patterns
 * like "(1)... (2)... (3)..." 1. ... 2. ... or 1) ... 2) ... and
 * rendering them as semantic <ol><li> lists.
 *
 * Falls back to a plain <p> if no numbered list pattern is detected.
 * Normal paragraphs that are not lists are preserved.
 */
export function FormattedContent({ text, className = "" }: FormattedContentProps) {
  if (!text) return null;

  const split = trySplitNumberedList(text);
  if (!split) {
    return <p className={className}>{text}</p>;
  }

  const { preamble, items } = split;

  return (
    <>
      {preamble && (
        <p className={className}>{preamble}</p>
      )}
      <ol className={`list-inside list-decimal space-y-1.5 ${className}`}>
        {items.map((item, i) => (
          <li key={i} className={className}>{item}</li>
        ))}
      </ol>
    </>
  );
}

/**
 * Attempts to split text into a numbered list.
 *
 * Supports patterns:
 *   - "(1) ... (2) ... (3) ..."
 *   - "1. ... 2. ... 3. ..."
 *   - "1) ... 2) ... 3) ..."
 *
 * Returns null if fewer than 2 numbered items are found
 * (i.e. the text is not a numbered list).
 */
function trySplitNumberedList(text: string): { preamble: string; items: string[] } | null {
  // Match all numbered markers: (1), 1., 1)
  const markerRegex = /(?:\((\d+)\)|(?<!\d)(\d+)\.(?!\d)|(?<!\d)(\d+)\))/g;

  const markers: { index: number; endIndex: number }[] = [];
  let match;

  while ((match = markerRegex.exec(text)) !== null) {
    markers.push({
      index: match.index,
      endIndex: match.index + match[0].length,
    });
    if (markers.length >= 20) break; // safety limit
  }

  // Need at least 2 consecutive markers to be a list
  if (markers.length < 2) return null;

  // Preamble: text before first marker
  const preamble = text.substring(0, markers[0].index).replace(/[,:\s]+$/, "").trim();

  // Items: text between markers
  const items = markers.map((m, i) => {
    const start = m.endIndex;
    const end = i < markers.length - 1 ? markers[i + 1].index : text.length;
    return text.substring(start, end).replace(/^[,:\s]+|[,:\s]+$/g, "").trim();
  });

  return { preamble, items };
}
