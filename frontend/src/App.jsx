import Navbar from './components/Navbar';
import ToSInput from './components/ToSInput';
import Results from './components/Results';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="container mx-auto p-6 flex-grow flex flex-col items-center">
        <h2 className="text-3xl font-bold text-gray-100 mb-6">ToS Analyzer</h2>
        <p className="text-gray-400 mb-8 max-w-2xl text-center">
          Paste or upload your app's Terms of Service to identify risky or unfair clauses.
        </p>
        <ToSInput />
        <ErrorBoundary>
          <Results />
        </ErrorBoundary>
      </main>
      <Footer />
    </div>
  );
}

export default App;