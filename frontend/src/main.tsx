import { createRoot } from "react-dom/client";
import "./index.scss";
import { Root } from "./Root";

// createRoot(document.getElementById("root")!).render();

createRoot(document.getElementById("root") as HTMLElement).render(<Root />);
