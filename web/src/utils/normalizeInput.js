// Convert fullwidth digits (０-９) to halfwidth (0-9)
// by subtracting the Unicode offset between them
export function normalizeFullwidthDigits(value) {
  return value.replace(/[０-９]/g, (s) => String.fromCharCode(s.charCodeAt(0) - 0xfee0));
}
