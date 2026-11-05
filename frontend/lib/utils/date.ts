/**
 * Date and timezone utility functions for Kynetic.
 * Guarantees dynamic browser timezone detection via Intl.DateTimeFormat
 * and safe parsing of UTC ISO timestamps.
 */

/**
 * Detects the user's device/browser timezone dynamically.
 * e.g., "Asia/Kolkata", "America/New_York", "Europe/London".
 */
export function getUserTimeZone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

/**
 * Safely parses any timestamp into a Date object representing the exact UTC moment.
 * If the input is an ISO string without timezone information (e.g. older naive DB records),
 * it treats it as UTC rather than falling back to local time.
 */
export function parseUtcDate(input: string | Date | number | null | undefined): Date {
  if (!input) return new Date();
  if (input instanceof Date) return input;
  if (typeof input === "number") return new Date(input);

  const str = String(input).trim();
  // Check if string is an ISO format without timezone offset or Z
  // E.g., "2026-11-04T04:01:22" or "2026-11-04 04:01:22.730125"
  if (/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?$/.test(str)) {
    return new Date(str.replace(" ", "T") + "Z");
  }
  return new Date(str);
}

/**
 * Formats a workspace activity timestamp for display in the Recent Activity feed and Progress views.
 * Automatically adapts to the user's dynamic device timezone.
 *
 * Suggested format: "05 Nov 2026, 10:30 PM" (full date and time).
 */
export function formatActivityDateTime(
  input: string | Date | number | null | undefined,
  targetTimeZone?: string
): string {
  const date = parseUtcDate(input);
  const timeZone = targetTimeZone || getUserTimeZone();

  return new Intl.DateTimeFormat("en-GB", {
    timeZone,
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  }).format(date);
}

/**
 * Full date/time string for tooltips or expanded views.
 */
export function formatFullDateTime(
  input: string | Date | number | null | undefined,
  targetTimeZone?: string
): string {
  const date = parseUtcDate(input);
  const timeZone = targetTimeZone || getUserTimeZone();

  return new Intl.DateTimeFormat(undefined, {
    timeZone,
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZoneName: "short",
  }).format(date);
}

