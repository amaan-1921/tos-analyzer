import Navbar from '../components/Navbar';
import Footer from '../components/Footer';


function About({ setCurrentPage, goHome }) {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-black via-gray-900 to-black pb-20">
      <Navbar setCurrentPage={setCurrentPage} goHome={goHome} />
      <main className="flex-grow container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-medium text-white mb-8 font-serif text-center">
            About RiskWise
          </h1>
          
          <div className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-xl shadow-2xl border border-gray-700/50 mb-8">
            <h2 className="text-2xl font-semibold text-white mb-6">What is RiskWise?</h2>
            <p className="text-gray-300 text-lg leading-relaxed mb-6">
              RiskWise is an AI-powered Terms of Service analyzer designed to help users identify potential risks, 
              unfair clauses, and legal concerns in complex legal documents. Our advanced artificial intelligence 
              technology breaks down lengthy terms of service into easy-to-understand risk assessments.
            </p>
            
            <h2 className="text-2xl font-semibold text-white mb-6">Why RiskWise?</h2>
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div className="bg-gray-900/50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-teal-400 mb-3">Time-Saving</h3>
                <p className="text-gray-300">
                  No more spending hours reading through complex legal jargon. Get instant analysis 
                  and understand the key risks in minutes.
                </p>
              </div>
              <div className="bg-gray-900/50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-teal-400 mb-3">Risk Identification</h3>
                <p className="text-gray-300">
                  Our AI identifies potentially problematic clauses related to data privacy, 
                  liability, content rights, and more.
                </p>
              </div>
              <div className="bg-gray-900/50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-teal-400 mb-3">Interactive Analysis</h3>
                <p className="text-gray-300">
                  Ask questions about specific clauses and get detailed explanations 
                  through our intelligent chat interface.
                </p>
              </div>
              <div className="bg-gray-900/50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-teal-400 mb-3">User-Friendly</h3>
                <p className="text-gray-300">
                  Complex legal language translated into plain English that anyone can understand 
                  and act upon.
                </p>
              </div>
            </div>
            
            <h2 className="text-2xl font-semibold text-white mb-6">Our Mission</h2>
            <p className="text-gray-300 text-lg leading-relaxed">
              We believe that everyone should understand the legal agreements they're entering into. 
              RiskWise democratizes legal analysis by making it accessible, fast, and reliable for 
              everyday users, small businesses, and organizations alike.
            </p>
          </div>
          
          <div className="text-center">
            <button 
              onClick={() => goHome ? goHome() : setCurrentPage('home')}
              className="px-8 py-3 bg-gradient-to-r from-teal-500 to-blue-500 hover:from-teal-400 hover:to-blue-400 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              Back to Home
            </button>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default About;