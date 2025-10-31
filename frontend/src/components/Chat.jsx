import { useState } from 'react';
import { useResults } from './ResultsContext';

function Chat() {
  const [inputMessage, setInputMessage] = useState('');
  const { chatMessages, setChatMessages, isChatLoading, setIsChatLoading, setError, setShowChat } = useResults();

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim()
    };

    // Add user message immediately
    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsChatLoading(true);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: inputMessage.trim() }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response || 'No response received',
        chunks: data.chunks || []
      };

      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(`Failed to get response: ${err.message}`);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Sorry, I encountered an error while processing your question.',
        chunks: []
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-gray-700/50 bg-gradient-to-r from-teal-500/10 to-blue-500/10">
        <div className="flex items-center">
          <svg className="w-5 h-5 mr-3 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <div>
            <h3 className="text-xl font-bold text-white">Discussion</h3>
            <p className="text-gray-300 text-sm">Ask questions about the analyzed document</p>
          </div>
        </div>
        <button
          onClick={() => setShowChat(false)}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded-lg transition-colors duration-200"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900/30">
        {chatMessages.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <p className="text-lg">Ready to discuss the analysis!</p>
            <p className="text-sm mt-2">
              Example: "What are the main risks in this document?"
            </p>
          </div>
        )}
        
        {chatMessages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-4 rounded-2xl backdrop-blur-sm border ${
                message.type === 'user'
                  ? 'bg-gradient-to-r from-teal-500/20 to-blue-500/20 text-white border-teal-500/30 rounded-br-md'
                  : 'bg-gray-800/60 text-gray-100 border-gray-600/50 rounded-bl-md'
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
              {message.chunks && message.chunks.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-600/30">
                  <p className="text-xs text-gray-400">Based on {message.chunks.length} relevant sections</p>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isChatLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800/60 text-gray-100 p-4 rounded-2xl rounded-bl-md border border-gray-600/50">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                <span className="text-sm text-gray-300 ml-2">Analyzing...</span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Input Area */}
      <div className="p-4 border-t border-gray-700/50 bg-gray-900/20">
        <div className="flex space-x-3">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about the document..."
            className="flex-1 p-3 bg-gray-800/70 text-gray-100 border border-gray-600/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50 resize-none backdrop-blur-sm"
            rows="2"
            disabled={isChatLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isChatLoading || !inputMessage.trim()}
            className="px-6 py-3 bg-gradient-to-r from-teal-500 to-blue-500 hover:from-teal-400 hover:to-blue-400 text-white font-semibold rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 shadow-lg"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;