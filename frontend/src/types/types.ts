export type PricePoint = {
  slot?: number;
  time: string;
  date?: string;
  actual?: number;
  forecast?: number;
  rangeBase?: number;
  rangeDiff?: number;
};

export type ChartPoint = PricePoint & {
  slot: number;
};

type HighlightMetric = {
  value: number;
  trend: string;
  change_text: string;
};

export type HighlightsData = {
  current_price: number;
  today_average: HighlightMetric;
  today_peak: HighlightMetric;
  today_low: HighlightMetric;
};

type DriversMetric = {
  name: string;
  description: string;
  previous_value: number;
  current_value: number;
  unit: string;
  change_text: string;
  trend: string;
};

export type DriversData = {
  summary: string;
  drivers: DriversMetric[];
};

export type ForecastData = {
  timestamp: string;
  price: number;
};
