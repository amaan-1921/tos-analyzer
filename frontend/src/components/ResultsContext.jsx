import { createContext, useContext, useState } from 'react';

const ResultsContext = createContext();

export function ResultsProvider({ children }) {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [hasAnalysisResults, setHasAnalysisResults] = useState(false);
  const [showChat, setShowChat] = useState(false);

  return (
    <ResultsContext.Provider value={{ 
      results, 
      setResults, 
      isLoading, 
      setIsLoading, 
      error, 
      setError,
      chatMessages,
      setChatMessages,
      isChatLoading,
      setIsChatLoading,
      hasAnalysisResults,
      setHasAnalysisResults,
      showChat,
      setShowChat
    }}>
      {children}
    </ResultsContext.Provider>
  );
}

export function useResults() {
  return useContext(ResultsContext);
}