import "./PageNotFound.scss";
import backgroundImage from "../../assets/404/404-page-not-found.png";
import { Link } from "react-router-dom";

export const PageNotFound = () => {
  return (
    <div className="page-not-found">
      <img src={backgroundImage} alt="" className="page-not-found__image" />
      <Link className="page-not-found__button" to="/">
        Return to Home Page
      </Link>
    </div>
  );
};
