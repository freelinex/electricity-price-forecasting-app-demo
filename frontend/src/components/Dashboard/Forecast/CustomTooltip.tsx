import type { PricePoint } from "../../../types/types";
import "./Forecast.scss";

type TooltipProps = {
  active?: boolean;
  payload?: {
    value?: number;
    dataKey?: string;
    payload?: PricePoint;
  }[];
  label?: number;
};

export function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) {
    return null;
  }

  const priceItem = payload.find(
    (item) =>
      (item.dataKey === "actual" || item.dataKey === "forecast") &&
      item.value != null &&
      Number.isFinite(item.value),
  );

  if (priceItem?.value == null) {
    return null;
  }

  const time = priceItem.payload?.time.trim();
  const rawDate = priceItem.payload?.date;
  let date = "";

  if (rawDate) {
    const [day, month, year] = rawDate.split("/").map(Number);
    const parsed = new Date(year, month - 1, day);

    if (
      Number.isFinite(parsed.getTime()) &&
      parsed.getFullYear() === year &&
      parsed.getMonth() === month - 1 &&
      parsed.getDate() === day
    ) {
      date = new Intl.DateTimeFormat("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }).format(parsed);
    }
  }

  return (
    <div className="price-chart__tooltip">
      {date && time && (
        <p className="price-chart__tooltip-date">
          {date} at {time}
        </p>
      )}

      <div className="price-chart__tooltip__container">
        <p className="price-chart__tooltip__container__price">
          €{priceItem.value.toFixed(2)}
        </p>
        <p className="price-chart__tooltip__container__unit">/MWh</p>
      </div>
    </div>
  );
}
