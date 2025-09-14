import { useState } from 'react';
import Navbar from './components/Navbar';
import ToSInput from './components/ToSInput';
import Results from './components/Results';
import Chat from './components/Chat';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import About from './pages/About';
import HowItWorks from './pages/HowItWorks';
import { useResults } from './components/ResultsContext';

function App() {
  const { hasAnalysisResults, showChat, setShowChat } = useResults();
  const [currentPage, setCurrentPage] = useState('home');

  const closeChat = () => {
    setShowChat(false);
  };

  // Handle page navigation
  if (currentPage === 'about') {
    return <About setCurrentPage={setCurrentPage} />;
  }
  
  if (currentPage === 'how-it-works') {
    return <HowItWorks setCurrentPage={setCurrentPage} />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-black via-gray-900 to-black pb-20 relative">
      <Navbar setCurrentPage={setCurrentPage} />
      <main className={`flex-grow flex flex-col transition-all duration-500 ${showChat ? 'pt-4' : 'justify-center items-center px-6'}`}>
        {!hasAnalysisResults ? (
          <div className="w-full max-w-4xl mx-auto text-center">
            <div className="mb-8">
              <h1 className="text-5xl font-medium text-white mb-4 tracking-tight font-serif">
                RiskWise
              </h1>
              <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
                Intelligent Terms of Service analysis powered by AI
              </p>
              <p className="text-gray-400 mt-4 max-w-xl mx-auto">
                Upload your Terms of Service document to identify potential risks, unfair clauses, and legal concerns
              </p>
            </div>
            <ToSInput />
          </div>
        ) : (
          <div className="w-full max-w-6xl mx-auto px-6">
            <ErrorBoundary>
              <Results />
            </ErrorBoundary>
          </div>
        )}
      </main>
      
      {/* Drawer-style Chat Overlay */}
      {showChat && (
        <div className="fixed inset-0 z-50 flex items-end">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-fade-in cursor-pointer"
            onClick={closeChat}
          ></div>
          
          {/* Chat Drawer */}
          <div className="relative w-full h-[70vh] bg-gray-800/95 backdrop-blur-md border-t border-gray-700/50 rounded-t-2xl shadow-2xl animate-slide-up">
            <ErrorBoundary>
              <Chat />
            </ErrorBoundary>
          </div>
        </div>
      )}
      
      <Footer />
    </div>
  );
}

export default App;