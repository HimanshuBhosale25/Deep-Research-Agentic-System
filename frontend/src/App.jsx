import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const answerTextRef = useRef(null);
  const [animatedAnswer, setAnimatedAnswer] = useState('');
  const [answerAnimationComplete, setAnswerAnimationComplete] = useState(false);

  const handleInputChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setResults(null);
    setError(null);
    setAnimatedAnswer('');
    setAnswerAnimationComplete(false);

    try {
      const response = await fetch('http://127.0.0.1:8000/research/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch results');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (results?.drafted_answer && answerTextRef.current) {
      const fullText = results.drafted_answer;
      let currentIndex = 0;
      const animationSpeed = 0.05;

      const intervalId = setInterval(() => {
        if (currentIndex < fullText.length) {
          setAnimatedAnswer(fullText.substring(0, currentIndex + 1));
          currentIndex++;
        } else {
          clearInterval(intervalId);
          setAnswerAnimationComplete(true);
        }
      }, animationSpeed);

      return () => clearInterval(intervalId);
    } else {
      setAnimatedAnswer('');
      setAnswerAnimationComplete(false);
    }
  }, [results]);

  return (
    <div className="app-container">
      <header className="header">
        <h1 className="title">AI Research Hub</h1>
        <p className="tagline">Explore the depths of knowledge.</p>
      </header>

      <section className="input-area">
        <input
          type="text"
          placeholder="Enter your query..."
          value={query}
          onChange={handleInputChange}
          className="query-input"
        />
        <button onClick={handleSubmit} disabled={loading} className="search-button">
          {loading ? <div className="spinner"></div> : 'Search'}
        </button>
      </section>

      {error && <div className="error-message">Error: {error}</div>}

      {results && (
        <section className="results-area">
          <div className="drafted-answer">
            <h2 className="section-title">Answer</h2>
            {results.drafted_answer ? (
              <p ref={answerTextRef} className="answer-text-generating">{animatedAnswer}</p>
            ) : (
              <p className="no-answer">No answer available.</p>
            )}
          </div>

          {answerAnimationComplete && (
            <div className="research-results">
              <h2 className="section-title">Sources</h2>
              {results.research_results && results.research_results.length > 0 ? (
                <ul className="results-list">
                  {results.research_results.map((item, index) => (
                    <li key={index} className="result-item">
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="result-title">{item.title}</a>
                      <p className="result-content">{item.content}...</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-results">No sources found.</p>
              )}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default App;