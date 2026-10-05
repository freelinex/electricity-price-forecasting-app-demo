# About Forecast.tsx

The `Forecast.tsx` component currently functions as a static, interactive graph of electricity prices. It does not yet retrieve data from the backend.

## 1. Static Data Is Generated

The `pricePoints` array contains 25 time points hard-coded directly in the code:

- `00:00–11:00` — actual prices in the `actual` field;
- `11:00` — a transition point containing both `actual: 90` and `forecast: 90`;
- `12:00–00:00` — forecast prices in the `forecast` field;
- a range of possible prices is also specified for the forecast:
  - `rangeBase` — the lower bound;
  - `rangeDiff` — the range width.
    For example:
    ```jsx
    time: “12:00”,
    forecast: 94,
    rangeBase: 84,
    rangeDiff: 20,
    ```
    On the chart, the forecast price is `94`, and the range is from `84` to `104`, because the upper limit is calculated as:
    ```jsx
    rangeBase + rangeDiff
    84 + 20 = 104
    ```

## 2. A numerical index is added to each data point

The array is converted to `data`:

```jsx
const data = pricePoints.map((point, slot) => ({ ...point, slot }));
```

Each point receives a `slot` field:

```jsx
slot: 0,
time: “00:00”,
actual: 56
```

`slot` is used as the X-axis coordinate. This also allows for two points with the same time, `00:00`: the start of the current day and the end of the next.

## 3. The component stores the selected point

A state is created inside the component:

```jsx
const [selectedPoint, setSelectedPoint] = useState<ChartPoint>();
```

Initially, `selectedPoint` is `undefined`, so the guide lines are not displayed.
When the user moves the cursor over the chart, Recharts calls:

```jsx
onMouseMove = { handleChartMouseMove };
```

## 4. The point under the cursor is determined

Recharts passes `activeLabel`, which corresponds to `slot` in this chart.

```jsx
const slot = Number(event.activeLabel);
```

Next, the component checks whether the received value is an integer:

```jsx
if (!Number.isInteger(slot)) {
  return;
}
```

After that, it finds the corresponding point:

```jsx
const point = data[slot];
```

and stores it in state:

```jsx
setSelectedPoint(point);
```

The state change triggers a re-render of the component.

## 5. The chart header is displayed

The header contains:

- the `Price Forecast` title;
- the `24h`, `1w`, and `1m` period buttons;
- the `15 min`, `30 min`, and `hourly` interval options.
  Currently, these elements do not have event handlers:
- `24h` always has an active CSS class;
- clicking `1w` or `1m` does not change anything;
- changing the interval also does not reload the data.

In other words, these are currently only visual controls.

## 6. Creating a Responsive Chart

`ResponsiveContainer` stretches the chart to fill the entire width and height of its parent container:

```jsx
<ResponsiveContainer width="100%" height="100%">
```

CSS sets the chart container’s height to `340px`.
`ComposedChart` allows you to display the following simultaneously:

- lines;
- filled areas;
- a coordinate grid;
- tooltips;
- auxiliary guides.
  Animation for all series is disabled via `isAnimationActive={false}`.

## 7. Customizable Axes

The X-axis uses `slot` but displays time to the user:

```jsx
<XAxis
  dataKey="slot"
  tickFormatter={(slot) => data[slot]?.time.trim() ?? “”}
  interval={3}
/>
```

Thus, the coordinate is an index, but the label is taken from `time`. `interval={3}` means that approximately every fourth label is displayed.

The Y-axis has a fixed range:

```jsx
domain={[0, 160]}
ticks={[0, 40, 80, 120, 160]}
```

If the price goes beyond the `0–160` range, the scale will not automatically expand to accommodate it.

## 8. The projected range is drawn

The range is created by two `Area` elements with the same `stackId=“range”`.

The first area:

```jsx
<Area dataKey="rangeBase" fill="transparent" />
```

is invisible and raises the start of the second area to the lower boundary.

The second:

```jsx
<Area dataKey="rangeDiff" fill="#f0f0f8" />
```

draws the visible width of the range.

As a result, the area is filled:

```jsx
from rangeBase
to rangeBase + rangeDiff
```

Since there are no actual values for `rangeBase` and `rangeDiff`, the range is displayed only in the forecast section.

## 9. Actual Price and Forecast Lines Are Drawn

Actual price:

```jsx
<Line dataKey="actual" stroke="#6E55FF" name="Actual price" />
```

is displayed as a solid purple line.

Forecast:

```jsx
<Line
  dataKey="forecast"
  stroke="#007DFF"
  strokeDasharray="3 3"
  name="Forecast"
/>
```

is displayed as a blue dashed line.

Both series have:

```jsx
connectNulls={true}
```

Therefore, Recharts connects the available values, skipping points where the corresponding field is missing.

The common point at `11:00` provides a visual connection between the actual and forecast lines.

## 10. Guides are displayed for the selected point

When the cursor hovers over a point, two dotted lines are drawn.
The horizontal line uses the actual price, and if that’s not available, the forecast:

```jsx
y={selectedPoint?.actual ?? selectedPoint?.forecast}
```

The vertical line uses the point’s position:

```jsx
x={selectedPoint?.slot}
```

This way, they intersect at the current price.

After the cursor leaves the chart, `selectedPoint` is not cleared, so the guides may remain at the last selected point.

## 11. Tooltip Displays the Price

The chart uses `CustomTooltip.tsx`

```jsx
<Tooltip content={<CustomTooltip />} cursor={false} />
```

Tooltip:

1. Checks if it is active.
2. Searches the payload for the value `actual` or `forecast`.
3. Retrieves the time from the start point.
4. Formats the price to two decimal places.
5. Displays the date, time, and unit of measurement.

Example:

```jsx
July 28, 2026 at 2:00 PM
€112.00 /MWh
```

The date `July 28, 2026` is hardcoded. Also, the `if (!priceItem?.value)` check will hide the `tooltip` if the price is `0`, even though zero may be a valid price.

## 12. Static information is displayed at the bottom

The footer contains:

- `Forecast generated today, 10:15 AM`;
- `Data sources: ENTSO-E`.

These values are not calculated or loaded—they are hard-coded directly in JSX.

So, right now, `Forecast` is a ready-to-use visualization with interactive tooltips, but without an API, actual period switching, interval changes, or a dynamic forecast generation date.
