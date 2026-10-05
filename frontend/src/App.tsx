import { Route, Routes } from "react-router-dom";
import "./App.scss";
import { PageNotFound } from "./components/PageNotFound";
import { Dashboard } from "./components/Dashboard";
import { Homepage } from "./components/Homepage";

export const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Homepage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="*" element={<PageNotFound />} />
    </Routes>
  );
};
