import { Route, Routes } from "react-router-dom";
import "./App.scss";
import { Homepage } from "./components/Homepage";
import { PageNotFound } from "./components/PageNotFound";
import { Dashboard } from "./components/Dashboard";

export const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Homepage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="*" element={<PageNotFound />} />
    </Routes>
  );
};
