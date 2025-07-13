import { useResults } from './ResultsContext';

function Results() {
  const { results, isLoading, error } = useResults();

  if (isLoading) {
    return (
      <div className="w-full max-w-2xl text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-accent-teal border-r-transparent"></div>
        <p className="mt-2 text-gray-400">Analyzing ToS...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-2xl bg-red-500/20 p-4 rounded-md border-l-4 border-red-500">
        <p className="text-red-200 font-semibold">Error: {error}</p>
      </div>
    );
  }

  if (results.length === 0) return null;

  return (
    <div className="w-full max-w-2xl bg-dark-secondary p-6 rounded-md shadow-md">
      <h3 className="text-2xl font-bold text-gray-100 mb-4">Analysis Results</h3>
      {results.map((result, index) => (
        <div
          key={index}
          className={`p-4 mb-4 rounded-md animate-fade-in ${
            result.label === 'Risky'
              ? 'bg-risky-red/20 border-l-4 border-risky-red'
              : result.label === 'Unfair'
              ? 'bg-unfair-yellow/20 border-l-4 border-unfair-yellow'
              : 'bg-gray-700'
          }`}
        >
          <p className="text-light-text font-semibold">
            Clause {result.clause_number}: {result.text}
          </p>
          <p className="text-gray-400">
            <span className="font-bold">{result.label}</span>: {result.explanation}
          </p>
        </div>
      ))}
    </div>
  );
}

export default Results;