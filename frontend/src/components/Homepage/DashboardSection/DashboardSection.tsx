import { Link } from "react-router-dom";
import "./DashboardSection.scss";
import arrowRight from "../../../assets/landing/cta-arrow-right.svg";
import background from "../../../assets/landing/desktop-background.png";

export const DashboardSection = () => {
  return (
    <>
      <section id="products" className="info-dashboard">
        <div className="info-dashboard__title-box">
          <h2 className="info-dashboard__title-box__title">
            Know what changed.
            <br />
            Understand what matter
          </h2>
        </div>

        <div className="info-dashboard__text-box">
          <p className="info-dashboard__text-box__text">
            Monitor European electricity-price forecasts,
            <br />
            understand revisions and evaluate confidence —<br />
            all in one place
          </p>

          <Link to="/dashboard" className="info-dashboard__text-box__anchor">
            Open dashboard
            <img
              src={arrowRight}
              alt=""
              className="info-dashboard__text-box__anchor__arrow"
            />
          </Link>
        </div>

        <div className="info-dashboard__image-box">
          <img
            src={background}
            alt=""
            className="info-dashboard__image-box__image"
          />
        </div>
      </section>
    </>
  );
};
