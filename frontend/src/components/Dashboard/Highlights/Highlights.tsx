import "./Highlights.scss";
import rateUpIcon from "../../../assets/rate-up-icon.svg";
import rateDownIcon from "../../../assets/rate-down-icon.svg";
import type { HighlightsData } from "../../../types/types";

type Props = {
  highlights: HighlightsData;
};

export const Highlights: React.FC<Props> = ({ highlights }) => {
  return (
    <div className="highlights">
      <div className="highlights__titleBox">
        <h4 className="highlights__titleBox__title">Today’s Highlights</h4>
      </div>

      <div className="highlights__currentPriceBox">
        <p className="highlights__currentPriceBox__text">Current price</p>

        <div className="highlights__currentPriceBox__priceContainer">
          <h3 className="highlights__currentPriceBox__priceContainer__price">
            €{highlights?.current_price.toFixed(2)}
          </h3>
          <p className="highlights__currentPriceBox__priceContainer__unit">
            /MWh
          </p>
        </div>
      </div>

      <div className="highlights__todaysPanelBox">
        <div className="highlights__todaysPanelBox__leftContainer">
          <p className="highlights__todaysPanelBox__leftContainer__text">
            Today’s Average
          </p>

          <div className="highlights__todaysPanelBox__leftContainer__priceContainer">
            <h3 className="highlights__todaysPanelBox__leftContainer__priceContainer__price">
              €{highlights?.today_average.value.toFixed(2)}
            </h3>
            <p className="highlights__todaysPanelBox__leftContainer__priceContainer__unit">
              /MWh
            </p>
          </div>
        </div>

        <div className="highlights__todaysPanelBox__infoContainer">
          {highlights?.today_average.trend === "up" ? (
            <div className="highlights__todaysPanelBox__infoContainer__trendBox">
              <img
                src={rateUpIcon}
                alt=""
                className="highlights__todaysPanelBox__infoContainer__trendBox__infoIcon"
              />
              <p className="highlights__todaysPanelBox__infoContainer__trendBox__changeText green">
                {highlights?.today_average.change_text}
              </p>
            </div>
          ) : (
            <div className="highlights__todaysPanelBox__infoContainer__trendBox">
              <img
                src={rateDownIcon}
                alt=""
                className="highlights__todaysPanelBox__infoContainer__trendBox__infoIcon"
              />
              <p className="highlights__todaysPanelBox__infoContainer__trendBox__changeText red">
                {highlights?.today_average.change_text}
              </p>
            </div>
          )}

          <p className="highlights__todaysPanelBox__infoContainer__text">
            vs yesterday
          </p>
        </div>
      </div>

      <div className="highlights__todaysPanelBox">
        <div className="highlights__todaysPanelBox__leftContainer">
          <p className="highlights__todaysPanelBox__leftContainer__text">
            Today’s Peak
          </p>

          <div className="highlights__todaysPanelBox__leftContainer__priceContainer">
            <h3 className="highlights__todaysPanelBox__leftContainer__priceContainer__price">
              €{highlights?.today_peak.value.toFixed(2)}
            </h3>
            <p className="highlights__todaysPanelBox__leftContainer__priceContainer__unit">
              /MWh
            </p>
          </div>
        </div>

        <div className="highlights__todaysPanelBox__infoContainer">
          {highlights?.today_peak.trend === "up" ? (
            <div className="highlights__todaysPanelBox__infoContainer__trendBox">
              <img
                src={rateUpIcon}
                alt=""
                className="highlights__todaysPanelBox__infoContainer__trendBox__infoIcon"
              />
              <p className="highlights__todaysPanelBox__infoContainer__trendBox__changeText green">
                {highlights?.today_peak.change_text}
              </p>
            </div>
          ) : (
            <div className="highlights__todaysPanelBox__infoContainer__trendBox">
              <img
                src={rateDownIcon}
                alt=""
                className="highlights__todaysPanelBox__infoContainer__trendBox__infoIcon"
              />
              <p className="highlights__todaysPanelBox__infoContainer__trendBox__changeText red">
                {highlights?.today_peak.change_text}
              </p>
            </div>
          )}
          <p className="highlights__todaysPanelBox__infoContainer__text">
            vs yesterday
          </p>
        </div>
      </div>

      <div className="highlights__todaysPanelBox">
        <div className="highlights__todaysPanelBox__leftContainer">
          <p className="highlights__todaysPanelBox__leftContainer__text">
            Today’s Low
          </p>

          <div className="highlights__todaysPanelBox__leftContainer__priceContainer">
            <h3 className="highlights__todaysPanelBox__leftContainer__priceContainer__price">
              €{highlights?.today_low.value.toFixed(2)}
            </h3>
            <p className="highlights__todaysPanelBox__leftContainer__priceContainer__unit">
              /MWh
            </p>
          </div>
        </div>

        <div className="highlights__todaysPanelBox__infoContainer">
          {highlights?.today_low.trend === "up" ? (
            <div className="highlights__todaysPanelBox__infoContainer__trendBox">
              <img
                src={rateUpIcon}
                alt=""
                className="highlights__todaysPanelBox__infoContainer__trendBox__infoIcon"
              />
              <p className="highlights__todaysPanelBox__infoContainer__trendBox__changeText green">
                {highlights?.today_low.change_text}
              </p>
            </div>
          ) : (
            <div className="highlights__todaysPanelBox__infoContainer__trendBox">
              <img
                src={rateDownIcon}
                alt=""
                className="highlights__todaysPanelBox__infoContainer__trendBox__infoIcon"
              />
              <p className="highlights__todaysPanelBox__infoContainer__trendBox__changeText red">
                {highlights?.today_low.change_text}
              </p>
            </div>
          )}
          <p className="highlights__todaysPanelBox__infoContainer__text">
            vs yesterday
          </p>
        </div>
      </div>
    </div>
  );
};
