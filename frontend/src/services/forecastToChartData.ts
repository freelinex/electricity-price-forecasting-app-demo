import type { ChartPoint, ForecastData } from "../types/types";
import { FORECAST_TIME_ZONE } from "./forecastTime";

type ForecastChartPoint = ChartPoint & {
  timestamp: string;
};

const timeFormatter = new Intl.DateTimeFormat("en-GB", {
  timeZone: FORECAST_TIME_ZONE,
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

const dateFormatter = new Intl.DateTimeFormat("en-GB", {
  timeZone: FORECAST_TIME_ZONE,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

export function getForecastDate(date: Date): string {
  return dateFormatter.format(date);
}

export function mapForecastToChartData(
  items: ForecastData[],
): ForecastChartPoint[] {
  const now = Date.now();

  return [...items]
    .sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
    )
    .map((item, slot) => {
      const date = new Date(item.timestamp);
      const isActual = date.getTime() <= now;

      return {
        slot,
        timestamp: item.timestamp,
        time: timeFormatter.format(date),
        date: getForecastDate(date),
        actual: isActual ? item.price : undefined,
        forecast: isActual ? undefined : item.price,
      };
    });
}
