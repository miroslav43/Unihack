// src/App.tsx
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "./App.css";
import LandingPage from "./components/LandingPage";
import LlamaChatPage from "./components/LlamaChatPage";
import TimparkHCLPage from "./components/TimparkHCLPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/general" element={<LlamaChatPage />} />
        <Route path="/timpark" element={<TimparkHCLPage />} />
      </Routes>
    </Router>
  );
}

export default App;
