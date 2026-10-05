import { useEffect, useState } from "react";
import {
  getDrivers,
  getForecast,
  getHighlights,
} from "../../services/fetchAPI";
import { Drivers } from "./Drivers";
import { Forecast } from "./Forecast";
import { Header } from "./Header";
import { Highlights } from "./Highlights";
import "./Dashboard.scss";
import type {
  DriversData,
  ForecastData,
  HighlightsData,
} from "../../types/types";
import { Bars } from "react-loader-spinner";
import { ChartPeriods } from "../../types/enums";
import type { ForecastPeriod } from "../../services/fetchAPI";
import { Skeleton } from "@mui/material";
// import { Sidebar } from "./Sidebar";

const apiPeriods: Record<ChartPeriods, ForecastPeriod> = {
  [ChartPeriods.day]: "24h",
  [ChartPeriods.week]: "1w",
  [ChartPeriods.month]: "1m",
};

type ForecastCacheEntry = {
  data: ForecastData[];
  loadedAt: Date;
};

export const Dashboard = () => {
  const [highlights, setHighlights] = useState<HighlightsData | null>(null);
  const [drivers, setDrivers] = useState<DriversData | null>(null);
  const [period, setPeriod] = useState(ChartPeriods.day);
  const [forecastRetry, setForecastRetry] = useState(0);
  const [initialForecastSettled, setInitialForecastSettled] = useState(false);
  const [forecastCache, setForecastCache] = useState<
    Partial<Record<ChartPeriods, ForecastCacheEntry>>
  >({});
  const [forecastError, setForecastError] = useState<{
    period: ChartPeriods;
    retry: number;
  } | null>(null);

  const cachedForecast = forecastCache[period];

  const hasForecastError =
    forecastError?.period === period && forecastError.retry === forecastRetry;

  const forecastLoading = !cachedForecast && !hasForecastError;

  const [isLoading, setIsLoading] = useState(true);
  const dashboardLoading = isLoading || !initialForecastSettled;

  const [updatedAt, setUpdatedAt] = useState(new Date());

  useEffect(() => {
    if (cachedForecast) return;

    const controller = new AbortController();
    let active = true;

    getForecast(apiPeriods[period], controller.signal)
      .then((data) => {
        if (!active) return;
        setForecastCache((cache) => ({
          ...cache,
          [period]: {
            data,
            loadedAt: new Date(),
          },
        }));
        setInitialForecastSettled(true);
      })
      .catch(() => {
        if (!active) return;
        setForecastError({
          period,
          retry: forecastRetry,
        });
        setInitialForecastSettled(true);
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [period, forecastRetry, cachedForecast]);

  useEffect(() => {
    Promise.allSettled([getHighlights(), getDrivers()])
      .then(([highlightsResult, driversResult]) => {
        if (highlightsResult.status === "fulfilled") {
          setHighlights(highlightsResult.value);
        }

        if (driversResult.status === "fulfilled") {
          setDrivers(driversResult.value);
        }
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [updatedAt]);

  const reload = () => {
    setIsLoading(true);
    setUpdatedAt(new Date());
  };

  return (
    <div className="app">
      <Header />

      {dashboardLoading && (
        <div className="app__loader-overlay">
          <div className="app__loader-overlay__loader">
            <Bars color="#0047F4" />
          </div>
        </div>
      )}
      <div className="app__body">
        {/*<Sidebar />*/}

        <main className="app__body__content">
          {dashboardLoading ? (
            <div className="app__body__content__loading-box">
              <Skeleton variant="rounded" height={38} width="25%" />
              <Skeleton variant="rounded" height={75} width="100%" />
              <Skeleton variant="rounded" height={60} width="100%" />
              <Skeleton variant="rounded" height={60} width="100%" />
              <Skeleton variant="rounded" height={60} width="100%" />
            </div>
          ) : highlights !== null ? (
            <Highlights highlights={highlights} />
          ) : (
            <div className="app__body__content__errorBox highlight">
              Unable to load Highlights
              <button
                onClick={() => reload()}
                className="app__body__content__errorBox__reloadBtn"
              >
                Retry
              </button>
            </div>
          )}

          {dashboardLoading ? (
            <div className="app__body__content__loading-box">
              <Skeleton variant="rounded" height={38} width="25%" />
              <Skeleton variant="rounded" height={28} width="40%" />
              <Skeleton variant="rounded" height={50} width="100%" />
              <Skeleton variant="rounded" height={50} width="100%" />
              <Skeleton variant="rounded" height={50} width="100%" />
              <Skeleton variant="rounded" height={50} width="100%" />
            </div>
          ) : drivers !== null ? (
            <Drivers drivers={drivers} />
          ) : (
            <div className="app__body__content__errorBox price-drivers">
              Unable to load Price Drivers
              <button
                onClick={() => reload()}
                className="app__body__content__errorBox__reloadBtn"
              >
                Retry
              </button>
            </div>
          )}

          {dashboardLoading ? (
            <div
              className="app__body__content__loading-box chart"
              role="status"
              aria-label="Loading Price Forecast"
            >
              <div className="price-forecast__header">
                <Skeleton variant="rounded" height={38} width="25%" />
                <Skeleton variant="rounded" height={38} width="20%" />
              </div>
              <Skeleton variant="rounded" height={20} width={60} />
              <Skeleton variant="rounded" height={320} width="100%" />
            </div>
          ) : (
            <Forecast
              rawData={cachedForecast?.data ?? []}
              loadedAt={cachedForecast?.loadedAt ?? updatedAt}
              period={period}
              onPeriodChange={(nextPeriod) => {
                setPeriod(nextPeriod);
                setForecastRetry((value) => value + 1);
              }}
              isLoading={forecastLoading}
              hasError={!cachedForecast && hasForecastError}
              onRetry={() => setForecastRetry((value) => value + 1)}
            />
          )}
        </main>
      </div>
    </div>
  );
};
