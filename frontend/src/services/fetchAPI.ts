import type { DriversData, ForecastData, HighlightsData } from "../types/types";

const BASE_URL = "/api";

const DRIVERS = "/drivers.json";
const HIGHLIGHTS = "/highlights.json";
const FORECAST = "/forecast.json";

export type ForecastPeriod = "24h" | "1w" | "1m";

export function getDrivers(): Promise<DriversData> {
  return fetch(BASE_URL + DRIVERS).then((response) => {
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    return response.json();
  });
}

export function getHighlights(): Promise<HighlightsData> {
  return fetch(BASE_URL + HIGHLIGHTS).then((response) => {
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    return response.json();
  });
}

export async function getForecast(
  period: ForecastPeriod = "24h",
  signal?: AbortSignal,
): Promise<ForecastData[]> {
  const response = await fetch(`${BASE_URL}${FORECAST}?period=${period}`, {
    signal,
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.forecast;
}
