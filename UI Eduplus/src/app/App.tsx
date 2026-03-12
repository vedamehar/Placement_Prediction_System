import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router";
import { ThemeProvider } from "next-themes";
import { Dashboard } from "./components/Dashboard";
import { ChatbotInterface } from "./components/ChatbotInterface";
import { PredictionResult } from "./components/PredictionResult";
import { PlacementProbability } from "./components/PlacementProbability";

export default function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chatbot" element={<ChatbotInterface />} />
          <Route path="/predictions" element={<PredictionResult />} />
          <Route path="/placement-probability" element={<PlacementProbability />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}