export const API_BASE =
  (import.meta as any).env?.VITE_API_BASE ||
  window.location.origin; // same origin when using single Docker Space