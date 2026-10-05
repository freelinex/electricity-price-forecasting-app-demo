import "./Header.scss";
import logo from "../../../assets/logo.svg";
import backButton from "../../../assets/arrow-left-active.svg";
import { Link } from "react-router-dom";
// import headphonesIcon from "../../../assets/headphones-button.svg";
// import fileIcon from "../../../assets/file-button.svg";
// import searchIcon from "../../../assets/search-icon.svg";

export const Header = () => {
  return (
    <header className="header">
      <a href="" className="header__logo">
        <img className="header__logo__img" src={logo} alt="" />
      </a>

      <div className="header__buttonBox">
        {/*
          <div className="header__buttonBox__search">
            <img
              src={searchIcon}
              alt=""
              className="header__buttonBox__search__icon"
            />
            <input
              type="text"
              placeholder="Search..."
              className="header__buttonBox__search__searchField"
            />
          </div>

          <a
            onClick={(e) => e.preventDefault()}
            href=""
            className="header__buttonBox__button"
          >
            <img
              src={fileIcon}
              alt=""
              className="header__buttonBox__button__img"
              />
          </a>
              */}
        <Link to="/" className="header__buttonBox__button">
          <img
            src={backButton}
            alt=""
            className="header__buttonBox__button__img"
          />
          Back
        </Link>
      </div>
    </header>
  );
};
