// src/TimparkHCLPage.tsx
import React, { useEffect, useState } from "react";
import { FiMoon, FiSend, FiSun } from "react-icons/fi";

const TimparkHCLPage: React.FC = () => {
  const [prompt, setPrompt] = useState<string>("");
  const [response, setResponse] = useState<string>("");
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  const handleSubmit = async () => {
    setLoading(true);
    setResponse("");

    try {
      const res = await fetch(
        "http://localhost:8003/extrage_timpark_informatii/",
        {
          // New API endpoint
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            interogare_utilizator: prompt,
            english: false,
          }),
        }
      );

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setResponse(data.raspuns_final);
    } catch (error) {
      console.error("Error:", error);
      setResponse("Error occurred while fetching response");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-white dark:bg-gray-900 relative">
      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="flex flex-col items-center space-y-4">
            <div className="loader"></div>
            <p className="text-white text-2xl font-semibold animate-pulse">
              Loading...
            </p>
          </div>
        </div>
      )}

      {/* Navigation Bar */}
      <nav className="bg-transparent">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-blue-600 dark:text-blue-300">
                Timpark HCL Info
              </span>
            </div>
            <div>
              <button
                className="text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white"
                onClick={() => setDarkMode(!darkMode)}
              >
                {darkMode ? <FiSun size={24} /> : <FiMoon size={24} />}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex flex-grow">
        {/* Left Column */}
        <div className="w-1/2 p-6 bg-gradient-to-r from-blue-500 to-purple-600 dark:from-blue-900 dark:to-purple-900 text-white flex flex-col">
          <h2 className="text-3xl font-semibold mb-4">Enter Prompt</h2>
          <textarea
            className="flex-grow p-4 rounded-md bg-white text-black resize-none mb-4 focus:outline-none focus:ring-2 focus:ring-blue-300"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type your message..."
          />
          <button
            className="py-3 px-6 bg-green-500 hover:bg-green-600 rounded-md text-white font-semibold flex items-center space-x-2 transition duration-300 ease-in-out transform hover:-translate-y-1 hover:scale-105 self-end"
            onClick={handleSubmit}
          >
            <span>Send</span>
            <FiSend size={20} />
          </button>
        </div>

        {/* Right Column */}
        <div className="w-1/2 p-6 bg-gray-100 dark:bg-gray-800 overflow-auto">
          <h2 className="text-3xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
            Response
          </h2>
          <div
            className="bg-white dark:bg-gray-700 p-6 rounded-md shadow-md transition duration-500 ease-in-out transform hover:-translate-y-1 hover:shadow-lg"
            style={{ color: darkMode ? "#f0f0f0" : "#333" }}
            dangerouslySetInnerHTML={{ __html: response }}
          ></div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-transparent p-4">
        <div className="max-w-full mx-auto flex justify-center space-x-6">
          {/* Footer content or social media icons */}
        </div>
      </footer>

      {/* Loader Styles */}
      <style>{`
        .loader {
          border: 8px solid rgba(255, 255, 255, 0.3);
          border-top: 8px solid white;
          border-radius: 50%;
          width: 80px;
          height: 80px;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default TimparkHCLPage;
