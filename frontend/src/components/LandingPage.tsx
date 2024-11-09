// src/components/LandingPage.tsx
import React from "react";
import { useNavigate } from "react-router-dom";

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-blue-500 to-purple-600">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-white mb-10">
          Welcome to HCL Chat
        </h1>
        <div>
          <button
            onClick={() => navigate("/general")}
            className="w-64 py-4 bg-white text-blue-600 font-semibold rounded-lg shadow-md hover:bg-gray-100 transition duration-300"
          >
            General HCL
          </button>
          <button
            onClick={() => navigate("/timpark")}
            className="w-64 py-4 bg-white text-purple-600 font-semibold rounded-lg shadow-md hover:bg-gray-100 transition duration-300 mt-6"
          >
            Timpark HCL
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
