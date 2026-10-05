import "./Sidebar.scss";
import tvIcon from "../../../assets/tv-icon.svg";
import compassIcon from "../../../assets/compass-icon.svg";
import fastForwardIcon from "../../../assets/fast-forward-icon.svg";
import barChartIcon from "../../../assets/bar-chart-icon.svg";
import barLineChartIcon from "../../../assets/bar-line-chart-icon.svg";
import charBreakoutIcon from "../../../assets/chart-breakout-circle-icon.svg";
import dataFlowIcon from "../../../assets/dataflow-icon.svg";
import fileIcon from "../../../assets/file-icon.svg";
import bellIcon from "../../../assets/bell-icon.svg";
import presentationChartIcon from "../../../assets/presentation-chart-icon.svg";
import coinsIcon from "../../../assets/coins-icon.svg";
import settingsIcon from "../../../assets/settings-icon.svg";
import arrowRightIcon from "../../../assets/arrow-right-icon.svg";

export const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="sidebar__buttonsContainer">
        <div className="sidebar__buttonsContainer__mainButtonBox">
          <a
            href=""
            className="sidebar__buttonsContainer__mainButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__mainButtonBox__button__icon"
              src={tvIcon}
              alt=""
            />
            Overview
          </a>
        </div>

        <div className="sidebar__buttonsContainer__secondaryButtonBox">
          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={compassIcon}
              alt=""
            />
            Live-prices
          </a>

          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={fastForwardIcon}
              alt=""
            />
            Day-Ahead
          </a>

          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={barChartIcon}
              alt=""
            />
            Intraday
          </a>

          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={barLineChartIcon}
              alt=""
            />
            Forward Curve
          </a>
        </div>

        <div className="sidebar__buttonsContainer__secondaryButtonBox">
          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={charBreakoutIcon}
              alt=""
            />
            Price Drivers
          </a>

          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={dataFlowIcon}
              alt=""
            />
            Forecasts
          </a>

          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={fileIcon}
              alt=""
            />
            Prices History
          </a>
        </div>

        <div className="sidebar__buttonsContainer__secondaryButtonBox">
          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={bellIcon}
              alt=""
            />
            Alerts
          </a>

          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={presentationChartIcon}
              alt=""
            />
            Watchlist
          </a>

          <a
            href=""
            className="sidebar__buttonsContainer__secondaryButtonBox__button"
          >
            <img
              className="sidebar__buttonsContainer__secondaryButtonBox__button__icon"
              src={coinsIcon}
              alt=""
            />
            Compare markets
          </a>
        </div>

        <a href="" className="sidebar__buttonsContainer__settingsButtonBox">
          <div className="sidebar__buttonsContainer__settingsButtonBox__mainBox">
            <div className="sidebar__buttonsContainer__settingsButtonBox__mainBox__button">
              <img
                className="sidebar__buttonsContainer__settingsButtonBox__mainBox__button__icon"
                src={settingsIcon}
                alt=""
              />
              Settings
            </div>
          </div>
          <img
            className="sidebar__buttonsContainer__settingsButtonBox__arrow"
            src={arrowRightIcon}
            alt=""
          />
        </a>
      </div>
    </div>
  );
};
