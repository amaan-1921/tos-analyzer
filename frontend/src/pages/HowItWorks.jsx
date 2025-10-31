import Footer from '../components/Footer';
import Navbar from '../components/Navbar';

function HowItWorks({ setCurrentPage, goHome }) {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-black via-gray-900 to-black pb-20">
      <Navbar setCurrentPage={setCurrentPage} goHome={goHome} />
      <main className="flex-grow container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-medium text-white mb-8 font-serif text-center">
            How It Works
          </h1>
          
          <div className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-xl shadow-2xl border border-gray-700/50 mb-8">
            <p className="text-gray-300 text-lg leading-relaxed mb-8 text-center">
              RiskWise makes Terms of Service analysis simple and accessible. Follow these easy steps 
              to understand the risks in any legal document.
            </p>
            
            <div className="space-y-8">
              <div className="flex items-start space-x-6">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-teal-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  1
                </div>
                <div>
                  <h3 className="text-2xl font-semibold text-white mb-3">Upload Your Document</h3>
                  <p className="text-gray-300 text-lg leading-relaxed">
                    Simply upload your Terms of Service document in any supported format (.txt, .pdf, .doc, .docx). 
                    You can also use our demo mode to see how the analysis works with a sample document.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-6">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-teal-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  2
                </div>
                <div>
                  <h3 className="text-2xl font-semibold text-white mb-3">AI Analysis Process</h3>
                  <p className="text-gray-300 text-lg leading-relaxed">
                    Our advanced AI processes your document, breaking it down into individual clauses and analyzing 
                    each one for potential risks. The system categorizes risks into areas like Data & Privacy, 
                    Liability, Content & IP, Dispute Resolution, and more.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-6">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-teal-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  3
                </div>
                <div>
                  <h3 className="text-2xl font-semibold text-white mb-3">Review Detailed Results</h3>
                  <p className="text-gray-300 text-lg leading-relaxed">
                    Get a comprehensive analysis with color-coded risk levels. Each clause is labeled as Risky, 
                    Fair, or Neutral, with detailed reasoning explaining why it matters and what it means for you.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-6">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-teal-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  4
                </div>
                <div>
                  <h3 className="text-2xl font-semibold text-white mb-3">Ask Questions</h3>
                  <p className="text-gray-300 text-lg leading-relaxed">
                    Use our interactive chat interface to ask specific questions about any clause or concern. 
                    Get instant, contextual answers that help you understand the implications of the terms.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-12 bg-gradient-to-r from-teal-500/10 to-blue-500/10 border border-teal-500/30 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-3">What Makes Our Analysis Special?</h3>
              <ul className="text-gray-300 space-y-2">
                <li>• <strong>Knowledge Graph Technology:</strong> We don't just analyze text - we understand relationships and context</li>
                <li>• <strong>Risk Categorization:</strong> Each clause is categorized by risk type for easy understanding</li>
                <li>• <strong>Plain English Explanations:</strong> Complex legal language translated into understandable terms</li>
                <li>• <strong>Interactive Q&A:</strong> Get personalized answers to your specific concerns</li>
              </ul>
            </div>
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

export default HowItWorks;