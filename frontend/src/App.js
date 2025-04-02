import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.BACKEND_URL || "https://multiagentapp.onrender.com";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [urls, setUrls] = useState([]);
  const [urlInput, setUrlInput] = useState("");
  const [message, setMessage] = useState("");

  const fetchAnswer = async (question) => {
    try {
      setLoading(true);
      setError("");
      setAnswer("");

      const response = await axios.post(`${API_BASE_URL}/query`, { question },
        {
          headers: {
              "Content-Type": "application/json",
          },
          withCredentials: false,
        }
      );
      setAnswer(response.data.answer);
    } catch (error) {
      console.error("Error fetching answer:", error);
      setError("Failed to fetch answer. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAskClick = () => {
    if (question.trim() === "") {
      setError("Please enter a question.");
    } else {
      fetchAnswer(question);
    }
  };

  // Add a URL to the list
  const handleAddUrl = () => {
    if (urlInput) {
      setUrls([...urls, urlInput]);
      setUrlInput(""); // Reset input field
    }
  };

  // Ingest data from the provided URLs
  const handleIngestData = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ingest`, { urls },
        {
          headers: {
              "Content-Type": "application/json",
          },
          withCredentials: false,
      }
      );
      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error ingesting data.");
    }
  };

  // Clear the database
  const handleClearDatabase = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/clear`,{},
        {
            headers: {
                "Content-Type": "application/json",
            },
            withCredentials: false,
        });
      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error clearing database.");
    }
  };

  return (
    <div className="container">
      <div className="card response-card">
        <h2>Ask your question</h2>
        <div className="input-group">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter your question"
          />
          <button onClick={handleAskClick} disabled={loading}>
            {loading ? "Asking..." : "Ask"}
          </button>
        </div>

        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error-message">{error}</div>}
        {answer && <div className="answer">{answer}</div>}
      </div>

      <div className="card ingestion-card">
        <h2>Data Ingestion</h2>
        <div className="input-group">
          <input
            type="text"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="Enter URL"
          />
          <button onClick={handleAddUrl}>Add URL</button>
        </div>

        <div>
          <h3>URLs to Ingest:</h3>
          <ul>
            {urls.map((url, index) => (
              <li key={index}>{url}</li>
            ))}
          </ul>
        </div>

        <div className="action-buttons">
          <button onClick={handleIngestData} disabled={urls.length === 0}>
            Ingest Data
          </button>
          <button onClick={handleClearDatabase}>Clear Database</button>
        </div>
      </div>

      {message && <div className="message">{message}</div>}
    </div>
  );
}

export default App;
