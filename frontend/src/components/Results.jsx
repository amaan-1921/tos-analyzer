import { useResults } from './ResultsContext';

function Results() {
  const { results, isLoading, error, showChat, setShowChat } = useResults();

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-accent-teal border-r-transparent"></div>
        <p className="mt-2 text-gray-400">Analyzing ToS...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl bg-red-500/20 p-4 rounded-md border-l-4 border-red-500">
        <p className="text-red-200 font-semibold">Error: {error}</p>
      </div>
    );
  }

  if (results.length === 0) return null;

  const getRiskColor = (label) => {
    if (label?.toLowerCase().includes('risky')) {
      return 'bg-red-500/20 border-l-4 border-red-500';
    } else if (label?.toLowerCase().includes('unfair') || label?.toLowerCase().includes('warning')) {
      return 'bg-yellow-500/20 border-l-4 border-yellow-500';
    } else if (label?.toLowerCase().includes('fair') || label?.toLowerCase().includes('neutral')) {
      return 'bg-green-500/20 border-l-4 border-green-500';
    }
    return 'bg-gray-700';
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-gray-800/50 backdrop-blur-sm p-6 rounded-xl shadow-2xl border border-gray-700/50 mb-6">
      <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
        <div className="w-2 h-2 bg-teal-400 rounded-full mr-3 animate-pulse"></div>
        Analysis Results
      </h3>
      {results.map((result, index) => (
        <div
          key={index}
          className={`p-5 mb-4 rounded-lg animate-fade-in backdrop-blur-sm border transition-all duration-300 hover:scale-[1.01] ${
            getRiskColor(result.label)
          }`}
        >
          <div className="mb-3">
            <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-gray-700/50 text-gray-200 mr-3 border border-gray-600">
              {result.risk_category || 'General'}
            </span>
            <span className={`inline-block px-3 py-1 text-xs font-semibold rounded-full border ${
              result.label?.toLowerCase().includes('risky') ? 'bg-red-500/20 text-red-300 border-red-500/50' :
              result.label?.toLowerCase().includes('unfair') ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50' :
              'bg-green-500/20 text-green-300 border-green-500/50'
            }`}>
              {result.label}
            </span>
          </div>
          <p className="text-gray-100 font-medium mb-3 leading-relaxed">
            {result.clause_text}
          </p>
          <p className="text-gray-300 text-sm leading-relaxed">
            <span className="font-semibold text-gray-200">Analysis:</span> {result.reasoning}
          </p>
        </div>
      ))}
      
      {!showChat && (
        <div className="mt-8 text-center border-t border-gray-700/50 pt-6">
          <button
            onClick={() => setShowChat(true)}
            className="px-8 py-4 bg-gradient-to-r from-teal-500 to-blue-500 hover:from-teal-400 hover:to-blue-400 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center mx-auto space-x-3"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span>Discuss Analysis</span>
          </button>
          <p className="text-gray-400 text-sm mt-3">
            Have questions about the analysis? Start a conversation to learn more.
          </p>
        </div>
      )}
    </div>
  );
}

export default Results;