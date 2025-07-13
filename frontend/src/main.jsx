import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import { ResultsProvider } from './components/ResultsContext.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ResultsProvider>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </ResultsProvider>
  </React.StrictMode>
);
