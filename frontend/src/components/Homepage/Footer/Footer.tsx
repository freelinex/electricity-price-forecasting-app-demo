import "./Footer.scss";
import githubIcon from "../../../assets/landing/github-icon.svg";
import youtubeIcon from "../../../assets/landing/youtube-icon.svg";
import linkedinIcon from "../../../assets/landing/linkedin-icon.svg";
import type { MouseEvent } from "react";

export const Footer = () => {
  const scrollToTop = (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <footer className="footer">
      <div className="footer__logo-box">
        <a
          href="#"
          onClick={scrollToTop}
          className="footer__logo-box__logo-text"
        >
          Voltio
        </a>
      </div>

      <div className="footer__links-box">
        <div className="footer__links-box__buttons">
          <div className="footer__links-box__buttons__column">
            <p className="footer__links-box__buttons__column__button main">
              Explore
            </p>
            <a href="#" className="footer__links-box__buttons__column__button">
              Price Forecast
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Day-Ahead
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Intraday
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Forward Curve
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Market Overview
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Countries & Markets
            </a>
          </div>

          <div className="footer__links-box__buttons__column">
            <p className="footer__links-box__buttons__column__button main">
              Resources
            </p>
            <a href="#" className="footer__links-box__buttons__column__button">
              Energy Insights
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Market Reports
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Price Guides
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Methodology
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              FAQs
            </a>
          </div>

          <div className="footer__links-box__buttons__column">
            <p className="footer__links-box__buttons__column__button main">
              Documentation
            </p>
            <a href="#" className="footer__links-box__buttons__column__button">
              Getting started
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Methodology
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Data Sources
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              API Documentation
            </a>
          </div>

          <div className="footer__links-box__buttons__column">
            <p className="footer__links-box__buttons__column__button main">
              Company
            </p>
            <a href="#" className="footer__links-box__buttons__column__button">
              About Us
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Contact
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Careers
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Partners
            </a>
          </div>

          <div className="footer__links-box__buttons__column">
            <p className="footer__links-box__buttons__column__button main">
              Legal
            </p>
            <a href="#" className="footer__links-box__buttons__column__button">
              Privacy policy
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Terms of Service
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Cookie Policy
            </a>
            <a href="#" className="footer__links-box__buttons__column__button">
              Data Usage
            </a>
          </div>
        </div>
        <div className="footer__links-box__links">
          <a href="#" className="footer__links-box__links__link">
            <img src={githubIcon} alt="" />
          </a>
          <a href="#" className="footer__links-box__links__link">
            <img src={youtubeIcon} alt="" />
          </a>
          <a href="#" className="footer__links-box__links__link">
            <img src={linkedinIcon} alt="" />
          </a>
        </div>
      </div>
    </footer>
  );
};
