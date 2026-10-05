import "./Drivers.scss";
import windIcon from "../../../assets/wind-with-background-icon.svg";
import arrowIcon from "../../../assets/solar-arrow-right-linear.svg";
import sunIcon from "../../../assets/sun-with-background-icon.svg";
import peopleIcon from "../../../assets/people-background-icon.svg";
import gasIcon from "../../../assets/gas-background.svg";
import type { DriversData } from "../../../types/types";
import classNames from "classnames";
// import blueArrowRightIcon from "../../../assets/blue-arrow-right-icon.svg";

type Props = {
  drivers: DriversData;
};

export const Drivers: React.FC<Props> = ({ drivers }) => {
  function getIcon(type: string) {
    switch (type) {
      case "Wind Generation":
        return windIcon;
      case "Solar Generation":
        return sunIcon;
      case "Electricity Demand":
        return peopleIcon;
      default:
        return gasIcon;
    }
  }

  return (
    <div className="drivers">
      <div className="drivers__textBox">
        <div className="drivers__textBox__titleBox">
          <h4 className="drivers__textBox__titleBox__title">Price Drivers</h4>
          <p className="drivers__textBox__titleBox__text">{drivers?.summary}</p>
        </div>

        {/*
        <button className="drivers__textBox__button">
          View detailed drivers
          <img src={blueArrowRightIcon} alt="" />
        </button>
        */}
      </div>

      {drivers?.drivers.map((element, index) => (
        <div className="drivers__infoPanel" key={index}>
          <div className="drivers__infoPanel__textContainer">
            <img
              src={getIcon(element.name)}
              alt=""
              className="drivers__infoPanel__textContainer__icon"
            />

            <div className="drivers__infoPanel__textContainer__textBox">
              <p className="drivers__infoPanel__textContainer__textBox__mainText">
                {element.name}
              </p>
              <p className="drivers__infoPanel__textContainer__textBox__secondaryText">
                {element.description}
              </p>
            </div>
          </div>

          <div className="drivers__infoPanel__infoBox">
            <div className="drivers__infoPanel__infoBox__unitsBox">
              <p className="drivers__infoPanel__infoBox__unitsBox__text">
                {(element.previous_value / 1000).toFixed(2)} GW
              </p>
              <img
                src={arrowIcon}
                alt=""
                className="drivers__infoPanel__infoBox__unitsBox__arrow"
              />
              <p className="drivers__infoPanel__infoBox__unitsBox__text">
                {(element.current_value / 1000).toFixed(2)} GW
              </p>
            </div>

            <p
              className={classNames("drivers__infoPanel__infoBox__changeText", {
                red: element.trend === "down",
                green: element.trend === "up",
              })}
            >
              {element.change_text}
            </p>
          </div>
        </div>
      ))}
      <div className="drivers__infoPanel">
        <div className="drivers__infoPanel__textContainer">
          <img
            src={gasIcon}
            alt=""
            className="drivers__infoPanel__textContainer__icon"
          />

          <div className="drivers__infoPanel__textContainer__textBox">
            <p className="drivers__infoPanel__textContainer__textBox__mainText">
              Gas Prices
            </p>
            <p className="drivers__infoPanel__textContainer__textBox__secondaryText">
              Gas output impact
            </p>
          </div>
        </div>

        <div className="drivers__infoPanel__infoBox">
          <div className="drivers__infoPanel__infoBox__unitsBox">
            <p className="drivers__infoPanel__infoBox__unitsBox__text">+0%</p>
          </div>

          <p className="drivers__infoPanel__infoBox__changeText green">+0€</p>
        </div>
      </div>
    </div>
  );
};
