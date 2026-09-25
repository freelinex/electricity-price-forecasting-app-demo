import { useId, useState } from "react";
import type { ChartPoint, ForecastData } from "../../../types/types";
import { CustomTooltip } from "./CustomTooltip";
import "./Forecast.scss";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { mapForecastToChartData } from "../../../services/forecastToChartData";
import {
  FORECAST_TIME_ZONE,
  forecastCalendarToTimestamp,
  getForecastCalendarDate,
} from "../../../services/forecastTime";
import { ChartPeriods } from "../../../types/enums";
import classNames from "classnames";
import { Bars } from "react-loader-spinner";

type Props = {
  rawData: ForecastData[];
  loadedAt: Date;
  period: ChartPeriods;
  onPeriodChange: (period: ChartPeriods) => void;
  isLoading: boolean;
  hasError: boolean;
  onRetry: () => void;
};

export const Forecast: React.FC<Props> = ({
  rawData,
  loadedAt,
  period,
  onPeriodChange,
  isLoading,
  hasError,
  onRetry,
}) => {
  const [selectedPoint, setSelectedPoint] = useState<ChartPoint>();

  const [forecastInterval, setForecastInterval] = useState("60");

  const actualPriceGradientId = useId();
  const forecastGradientId = useId();

  const start = getForecastCalendarDate(new Date());
  start.setUTCHours(0, 0, 0, 0);
  const end = new Date(start);
  end.setUTCHours(23, 45, 0, 0);

  switch (period) {
    case ChartPeriods.day:
      break;

    case ChartPeriods.week:
      end.setUTCDate(end.getUTCDate() + 6);
      break;

    case ChartPeriods.month:
      end.setUTCDate(end.getUTCDate() + 29);
      break;
  }

  const startMs = forecastCalendarToTimestamp(start);
  const endMs = forecastCalendarToTimestamp(end);

  const transformedData = mapForecastToChartData(rawData ?? []);

  const visibleData = transformedData
    .filter((point) => {
      const timestamp = new Date(point.timestamp).getTime();

      return timestamp >= startMs && timestamp <= endMs;
    })
    .filter((point) => {
      const timestamp = new Date(point.timestamp).getTime();
      const [hour, minute] = point.time.split(":").map(Number);

      if (timestamp === endMs) {
        return true;
      }

      if (forecastInterval === "60") {
        return minute === 0;
      }

      if (forecastInterval === "30") {
        return minute % 30 === 0;
      }

      if (forecastInterval === "day") {
        return hour === 0 && minute === 0;
      }

      return true;
    })
    .map((point) => ({
      ...point,
      timestampMs: new Date(point.timestamp).getTime(),
    }));

  const firstForecastIndex = visibleData.findIndex(
    (point) => point.forecast != null,
  );

  const bridgeIndex =
    firstForecastIndex > 0 && visibleData[firstForecastIndex - 1].actual != null
      ? firstForecastIndex - 1
      : -1;

  const chartData = visibleData.map((point, index) =>
    index === bridgeIndex ? { ...point, forecast: point.actual } : point,
  );

  const yTickStep = 40;
  const { minPrice, maxPrice } = visibleData.reduce(
    (bounds, point) => {
      const price = point.actual ?? point.forecast;
      if (price == null || !Number.isFinite(price)) return bounds;

      return {
        minPrice: Math.min(bounds.minPrice, price),
        maxPrice: Math.max(bounds.maxPrice, price),
      };
    },
    { minPrice: 0, maxPrice: 0 },
  );
  const yAxisMin = Math.floor(minPrice / yTickStep) * yTickStep;
  const yAxisMax = Math.max(
    yAxisMin + yTickStep,
    Math.ceil(maxPrice / yTickStep) * yTickStep,
  );
  const yTicks = Array.from(
    { length: (yAxisMax - yAxisMin) / yTickStep + 1 },
    (_, index) => yAxisMin + index * yTickStep,
  );

  const xTicks: number[] = [];

  if (period === ChartPeriods.day) {
    for (const tick = new Date(start); tick.getTime() < end.getTime(); ) {
      xTicks.push(forecastCalendarToTimestamp(tick));
      tick.setUTCHours(tick.getUTCHours() + 4);
    }
    xTicks.push(endMs);
  } else {
    const tickCount = period === ChartPeriods.week ? 7 : 8;
    for (let index = 0; index < tickCount; index += 1) {
      xTicks.push(startMs + ((endMs - startMs) * index) / (tickCount - 1));
    }
  }

  const axisFormatter = new Intl.DateTimeFormat(
    "en-GB",
    period === ChartPeriods.day
      ? {
          timeZone: FORECAST_TIME_ZONE,
          hour: "2-digit",
          minute: "2-digit",
          hourCycle: "h23",
        }
      : {
          timeZone: FORECAST_TIME_ZONE,
          day: "2-digit",
          month: "short",
        },
  );

  const shortTime = loadedAt.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

  const handleChartMouseMove = (event: { activeLabel?: string | number }) => {
    if (event.activeLabel == null) {
      return;
    }

    const timestamp = Number(event.activeLabel);
    const point = visibleData.find((point) => point.timestampMs === timestamp);

    if (point) {
      setSelectedPoint(point);
    }
  };

  const handlePeriodChange = (nextPeriod: ChartPeriods) => {
    if (nextPeriod === period) return;
    setSelectedPoint(undefined);
    setForecastInterval("60");
    onPeriodChange(nextPeriod);
  };

  return (
    <section className="price-forecast">
      <header className="price-forecast__header">
        <div>
          <h2 className="price-forecast__title">Price Forecast</h2>
        </div>

        <div className="price-forecast__controls">
          <div
            className="price-forecast__periods"
            role="group"
            aria-label="Forecast period"
            data-active-index={[
              ChartPeriods.day,
              ChartPeriods.week,
              ChartPeriods.month,
            ].indexOf(period)}
          >
            <button
              type="button"
              onClick={() => handlePeriodChange(ChartPeriods.day)}
              aria-pressed={period === ChartPeriods.day}
              className={classNames("price-forecast__period-button", {
                "price-forecast__period-button--active":
                  period === ChartPeriods.day,
              })}
            >
              24h
            </button>

            <button
              type="button"
              onClick={() => handlePeriodChange(ChartPeriods.week)}
              aria-pressed={period === ChartPeriods.week}
              className={classNames("price-forecast__period-button", {
                "price-forecast__period-button--active":
                  period === ChartPeriods.week,
              })}
            >
              1w
            </button>

            <button
              type="button"
              onClick={() => handlePeriodChange(ChartPeriods.month)}
              aria-pressed={period === ChartPeriods.month}
              className={classNames("price-forecast__period-button", {
                "price-forecast__period-button--active":
                  period === ChartPeriods.month,
              })}
            >
              1m
            </button>
          </div>

          <select
            className="price-forecast__interval"
            aria-label="Forecast interval"
            value={forecastInterval}
            onChange={(e) => setForecastInterval(e.target.value)}
          >
            {period !== ChartPeriods.week && period !== ChartPeriods.month && (
              <option value="15">15 min</option>
            )}
            {period !== ChartPeriods.month && (
              <option value="30">30 min</option>
            )}
            <option value="60">hourly</option>
            {period === ChartPeriods.month && (
              <option value="day">daily</option>
            )}
          </select>
        </div>
      </header>

      <div className="price-forecast__unit">€/MWh</div>

      <div className="price-forecast__chart">
        {isLoading ? (
          <div role="status">
            <Bars color="#0047F4" />
          </div>
        ) : hasError ? (
          <div className="errorBox" role="alert">
            <p className="errorBox__text">Unable to load forecast</p>
            <button
              className="errorBox__button"
              type="button"
              onClick={onRetry}
            >
              Retry
            </button>
          </div>
        ) : rawData.length === 0 ? (
          <p>No forecast data available</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              accessibilityLayer={false}
              onMouseMove={handleChartMouseMove}
              margin={{
                top: 20,
                right: 18,
                left: -12,
                bottom: 5,
              }}
            >
              <defs>
                <linearGradient
                  id={actualPriceGradientId}
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="15%" stopColor="#494FDF" stopOpacity={0.22} />
                  <stop offset="100%" stopColor="#494FDF" stopOpacity={0} />
                </linearGradient>
                <linearGradient
                  id={forecastGradientId}
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="15%" stopColor="#007DFF" stopOpacity={0.22} />
                  <stop offset="100%" stopColor="#007DFF" stopOpacity={0} />
                </linearGradient>
              </defs>

              <CartesianGrid stroke="#ececf2" vertical={false} />

              <XAxis
                dataKey="timestampMs"
                type="number"
                scale="time"
                domain={[startMs, endMs]}
                ticks={xTicks}
                tickFormatter={(timestamp: number) =>
                  axisFormatter.format(new Date(timestamp))
                }
                axisLine={false}
                tickLine={false}
                interval={0}
                tick={({ x, y, payload }) => {
                  const isFirst = payload.value === xTicks[0];
                  const isLast = payload.value === xTicks[xTicks.length - 1];

                  return (
                    <text
                      x={x}
                      y={y}
                      dy={10}
                      textAnchor={isFirst ? "start" : isLast ? "end" : "middle"}
                      fill="#808080"
                      fontSize={12}
                    >
                      {axisFormatter.format(new Date(payload.value))}
                    </text>
                  );
                }}
              />

              <YAxis
                domain={[yAxisMin, yAxisMax]}
                ticks={yTicks}
                interval={0}
                allowDataOverflow
                axisLine={false}
                tickLine={false}
                tick={{
                  fill: "#808080",
                  fontSize: 12,
                }}
              />

              <Tooltip content={<CustomTooltip />} cursor={false} />

              <Area
                type="linear"
                dataKey="actual"
                baseValue={0}
                stroke="none"
                fill={`url(#${actualPriceGradientId})`}
                fillOpacity={1}
                dot={false}
                activeDot={false}
                legendType="none"
                tooltipType="none"
                connectNulls={true}
                isAnimationActive={false}
              />

              <Area
                type="linear"
                dataKey="forecast"
                baseValue={0}
                stroke="none"
                fill={`url(#${forecastGradientId})`}
                fillOpacity={1}
                dot={false}
                activeDot={false}
                legendType="none"
                tooltipType="none"
                connectNulls={true}
                isAnimationActive={false}
              />

              <ReferenceLine
                y={selectedPoint?.actual ?? selectedPoint?.forecast}
                stroke="#9d9da7"
                strokeDasharray="6 6"
              />

              <ReferenceLine
                x={
                  visibleData.find(
                    (point) => point.slot === selectedPoint?.slot,
                  )?.timestampMs
                }
                stroke="#b8b8c0"
                strokeDasharray="6 6"
              />

              <Line
                type="linear"
                dataKey="actual"
                stroke="#6E55FF"
                strokeWidth={1.2}
                dot={false}
                activeDot={{
                  r: 4,
                  fill: "#EAF5FF",
                  stroke: "#007DFF",
                  strokeWidth: 1,
                }}
                name="Actual price"
                connectNulls={true}
                isAnimationActive={false}
              />

              <Line
                type="linear"
                dataKey="forecast"
                stroke="#007DFF"
                strokeWidth={1.2}
                strokeDasharray="3 3"
                dot={false}
                activeDot={{
                  r: 4,
                  fill: "#EAF5FF",
                  stroke: "#007DFF",
                  strokeWidth: 1,
                }}
                name="Forecast"
                connectNulls={true}
                isAnimationActive={false}
              />

              <Legend
                verticalAlign="bottom"
                height={44}
                iconType="plainline"
                wrapperStyle={{
                  display: "flex",
                  justifyContent: "center",
                  fontSize: "12px",
                  color: "#777780",
                  paddingTop: "16px",
                }}
                labelStyle={{
                  color: "#535353",
                }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      <footer className="price-forecast__footer">
        {!isLoading && !hasError && rawData.length > 0 && (
          <span>Forecast loaded at, {shortTime.toUpperCase()}</span>
        )}

        <span>Data sources: ENTSO-E</span>
      </footer>
    </section>
  );
};
