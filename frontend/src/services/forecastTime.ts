// The backend is configured for the Polish electricity market.
export const FORECAST_TIME_ZONE = "Europe/Warsaw";

const calendarFormatter = new Intl.DateTimeFormat("en-GB", {
  timeZone: FORECAST_TIME_ZONE,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hourCycle: "h23",
});

// UTC fields are used only as a container for market calendar arithmetic.
export function getForecastCalendarDate(instant: Date): Date {
  const parts = calendarFormatter.formatToParts(instant);
  const value = (type: Intl.DateTimeFormatPartTypes) =>
    Number(parts.find((part) => part.type === type)?.value);

  return new Date(Date.UTC(
    value("year"), value("month") - 1, value("day"),
    value("hour"), value("minute"), value("second"),
  ));
}

// Resolve each boundary separately so periods can cross a DST change.
export function forecastCalendarToTimestamp(calendar: Date): number {
  const target = calendar.getTime();
  let timestamp = target;

  for (let attempt = 0; attempt < 3; attempt += 1) {
    const difference = target - getForecastCalendarDate(new Date(timestamp)).getTime();
    if (difference === 0) return timestamp;
    timestamp += difference;
  }

  return timestamp;
}
