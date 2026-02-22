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

  // Categorize by risk score
  const highRiskItems = results.filter(r => r.risk_score >= 8);
  const unfairItems = results.filter(r => r.risk_score >= 6 && r.risk_score < 8);
  const acceptableItems = results.filter(r => r.risk_score < 6);
  
  // Calculate statistics
  const avgRiskScore = results.length > 0 
    ? (results.reduce((sum, r) => sum + (r.risk_score || 0), 0) / results.length).toFixed(1)
    : 0;
  
  // Group by risk category for high risk items only
  const riskCategoryCount = {};
  highRiskItems.forEach(r => {
    if (r.risk_category) {
      riskCategoryCount[r.risk_category] = (riskCategoryCount[r.risk_category] || 0) + 1;
    }
  });

  const getRiskScoreColor = (score) => {
    if (score >= 7) return 'text-red-400';
    if (score >= 4) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="bg-gradient-to-br from-red-500/20 to-red-600/10 p-4 rounded-lg border border-red-500/30">
          <p className="text-gray-400 text-sm">🚨 High Risk</p>
          <p className={`text-3xl font-bold ${highRiskItems.length > 0 ? 'text-red-400' : 'text-gray-400'}`}>
            {highRiskItems.length}
          </p>
          <p className="text-xs text-gray-500 mt-1">8-10/10 severity</p>
        </div>
        <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 p-4 rounded-lg border border-yellow-500/30">
          <p className="text-gray-400 text-sm">⚠️ Unfair</p>
          <p className="text-3xl font-bold text-yellow-400">{unfairItems.length}</p>
          <p className="text-xs text-gray-500 mt-1">6-7/10 severity</p>
        </div>
        <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 p-4 rounded-lg border border-blue-500/30">
          <p className="text-gray-400 text-sm">Avg Risk Score</p>
          <p className={`text-3xl font-bold ${getRiskScoreColor(parseFloat(avgRiskScore))}`}>
            {avgRiskScore}/10
          </p>
          <p className="text-xs text-gray-500 mt-1">{results.length} clauses analyzed</p>
        </div>
      </div>

      <p className="text-xs text-gray-500">
        Note: LLM analysis can vary slightly between runs. Uploading the same PDF will reuse cached results.
      </p>

      {/* Risk Category Breakdown - Only for High Risk */}
      {Object.keys(riskCategoryCount).length > 0 && (
        <div className="bg-red-900/20 backdrop-blur-sm p-5 rounded-xl border border-red-500/30">
          <h4 className="text-lg font-semibold text-red-300 mb-4">⚠️ High Risk Categories</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(riskCategoryCount).map(([category, count]) => (
              <div key={category} className="bg-red-800/40 p-3 rounded-lg border border-red-600/30">
                <p className="text-red-300 text-sm font-medium">{category}</p>
                <p className="text-2xl font-bold text-red-400">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* High Risk Clauses - Highlighted First */}
      {highRiskItems.length > 0 && (
        <div className="bg-red-900/30 backdrop-blur-sm p-6 rounded-xl shadow-2xl border-2 border-red-500/50">
          <h3 className="text-2xl font-bold text-red-300 mb-6 flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-3 animate-pulse"></div>
            🚨 HIGH RISK CLAUSES ({highRiskItems.length})
          </h3>
          <p className="text-gray-300 text-sm mb-6 bg-red-900/30 p-3 rounded-lg border-l-4 border-red-500">
            These clauses could seriously harm you. Consider avoiding this service or proceed with extreme caution.
          </p>
          
          {highRiskItems.map((result, index) => (
            <div
              key={index}
              className="p-5 mb-4 rounded-lg animate-fade-in backdrop-blur-sm border bg-red-500/10 border-red-500/40 transition-all duration-300 hover:scale-[1.01]"
            >
              <div className="mb-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-red-700/50 text-red-200 border border-red-600">
                    {result.risk_category || 'Critical'}
                  </span>
                  <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-red-500/20 text-red-300 border border-red-500/50">
                    High Risk
                  </span>
                </div>
                {result.risk_score !== undefined && (
                  <div className="text-lg font-bold px-3 py-1 rounded-full bg-red-700/50 text-red-300">
                    Risk: {result.risk_score}/10
                  </div>
                )}
              </div>
              <p className="text-gray-100 font-medium mb-3 leading-relaxed">
                "{result.clause_text}"
              </p>
              <p className="text-gray-300 text-sm leading-relaxed">
                <span className="font-semibold text-red-300">⚠️ Why This Is Risky:</span> {result.reasoning}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Unfair Clauses */}
      {unfairItems.length > 0 && (
        <div className="bg-yellow-900/20 backdrop-blur-sm p-6 rounded-xl shadow-xl border border-yellow-500/40">
          <h3 className="text-2xl font-bold text-yellow-300 mb-6 flex items-center">
            <div className="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
            ⚠️ UNFAIR CLAUSES ({unfairItems.length})
          </h3>
          <p className="text-gray-300 text-sm mb-6 bg-yellow-900/30 p-3 rounded-lg border-l-4 border-yellow-500">
            These clauses significantly favor the company over you. Read carefully before accepting.
          </p>
          
          {unfairItems.map((result, index) => (
            <div
              key={index}
              className="p-5 mb-4 rounded-lg backdrop-blur-sm border bg-yellow-500/10 border-yellow-500/30 transition-all duration-300 hover:scale-[1.01]"
            >
              <div className="mb-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-yellow-700/50 text-yellow-200 border border-yellow-600">
                    {result.risk_category || 'One-Sided'}
                  </span>
                  <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-yellow-500/20 text-yellow-300 border border-yellow-500/50">
                    Unfair
                  </span>
                </div>
                {result.risk_score !== undefined && (
                  <div className="text-lg font-bold px-3 py-1 rounded-full bg-yellow-700/50 text-yellow-300">
                    Risk: {result.risk_score}/10
                  </div>
                )}
              </div>
              <p className="text-gray-100 font-medium mb-3 leading-relaxed">
                "{result.clause_text}"
              </p>
              <p className="text-gray-300 text-sm leading-relaxed">
                <span className="font-semibold text-yellow-300">⚠️ Why This Is Unfair:</span> {result.reasoning}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Acceptable Clauses Footer */}
      {acceptableItems.length > 0 && (
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50 text-center">
          <p className="text-gray-400 text-sm">
            ✓ <span className="font-semibold text-gray-300">{acceptableItems.length}</span> acceptable clause{acceptableItems.length !== 1 ? 's' : ''} (risk score &lt; 6/10) — no action needed
          </p>
        </div>
      )}
      
      {!showChat && (
        <div className="mt-8 text-center border-t border-gray-700/50 pt-6">
          <button
            onClick={() => setShowChat(true)}
            className="px-8 py-4 bg-gradient-to-r from-teal-500 to-blue-500 hover:from-teal-400 hover:to-blue-400 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center mx-auto space-x-3"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span>Ask Questions About These Risks</span>
          </button>
          <p className="text-gray-400 text-sm mt-3">
            Want to understand more about these risky clauses? Chat with the analyzer.
          </p>
        </div>
      )}
    </div>
  );
}

export default Results;