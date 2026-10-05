import "./HeroSection.scss";
import { Link } from "react-router-dom";
import arrowDown from "../../../assets/landing/arrow-down.svg";

export const HeroSection = () => {
  return (
    <header className="hero-section">
      <div className="hero-section__top">
        <div className="hero-section__top__title-box">
          <h1 className="hero-section__top__title-box__title">
            European electricity-price intelligence
          </h1>
          <h4 className="hero-section__top__title-box__subtitle">
            Explainable electricity-price forecasting for European traders,
            analysts and asset operators
          </h4>
          <Link
            to="/dashboard"
            className="hero-section__top__title-box__anchor"
          >
            Explore the market
          </Link>
        </div>

        <nav className="hero-section__top__nav-box">
          <a href="#products" className="hero-section__top__nav-box__item">
            Products
          </a>
          <a href="#workflow" className="hero-section__top__nav-box__item">
            How it works
          </a>
          <a href="#market" className="hero-section__top__nav-box__item">
            Coverage
          </a>
        </nav>
      </div>

      <div className="hero-section__bottom">
        <div className="hero-section__bottom__explore-box">
          <div className="hero-section__bottom__explore-box__anchor">
            Explore
            <img
              src={arrowDown}
              alt="arrow-down"
              className="hero-section__bottom__explore-box__anchor__arrow"
            />
          </div>
        </div>
      </div>
    </header>
  );
};
