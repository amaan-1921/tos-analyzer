import { useState } from 'react';
import { useResults } from './ResultsContext';

function ToSInput() {
    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState(0);
    const [progressMessage, setProgressMessage] = useState('');
    const [useCloud, setUseCloud] = useState(true); // Demo-friendly default (local remains available)
    const [showDetails, setShowDetails] = useState(false);
    const { setResults, setIsLoading, isLoading, setError, setHasAnalysisResults, setDocId } = useResults();

    const pollAnalysisProgress = async (docId) => {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`http://localhost:8000/analysis/${docId}`);
                if (!response.ok) throw new Error('Failed to fetch progress');
                
                const data = await response.json();
                
                // Use actual backend progress directly (0-100)
                setProgress(data.progress || 0);
                setProgressMessage(data.message);
                
                if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    setProgress(100);
                    setProgressMessage('Analysis complete!');
                    setResults(data.result || []);
                    setDocId(docId);
                    setHasAnalysisResults(true);
                    setIsLoading(false);
                    
                    // Keep final state visible for a moment
                    setTimeout(() => {
                        setProgress(0);
                        setProgressMessage('');
                    }, 2000);
                } else if (data.status === 'failed') {
                    clearInterval(pollInterval);
                    setError(`Analysis failed: ${data.message}`);
                    setIsLoading(false);
                    setProgress(0);
                    setProgressMessage('');
                }
            } catch (err) {
                console.error('Poll error:', err);
            }
        }, 500); // Poll every 500ms
    };

    const handleAnalyze = async () => {
        if (!file) {
            setError('Please upload a file.');
            return;
        }
        
        setIsLoading(true);
        setError(null);
        setHasAnalysisResults(false);
        setProgress(0);
        setProgressMessage('Initializing...');

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('use_cloud', useCloud);

            const response = await fetch('http://localhost:8000/ingest', {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            const docId = data.doc_id;
            
            setProgress(10);
            setProgressMessage(data.message);
            
            // Start polling for progress
            pollAnalysisProgress(docId);
        } catch (err) {
            setError(`Failed to start analysis: ${err.message}`);
            setResults([]);
            setHasAnalysisResults(false);
            setIsLoading(false);
            setProgress(0);
            setProgressMessage('');
        }
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        if (selectedFile) {
            // Reset previous results when new file is selected
            setResults([]);
            setHasAnalysisResults(false);
            setError(null);
            setProgress(0);
            setProgressMessage('');
        }
    };

    const handleFileRemove = () => {
        setFile(null);
        setResults([]);
        setHasAnalysisResults(false);
        setError(null);
        setProgress(0);
        setProgressMessage('');
        // Reset the file input
        const fileInput = document.getElementById('tos-file');
        if (fileInput) {
            fileInput.value = '';
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto text-center">
            <div className="flex flex-col items-center space-y-4">
                {/* Processing Mode Selection */}
                <div className="w-full max-w-md bg-gray-800/40 border border-gray-700/50 rounded-xl p-4 backdrop-blur-sm">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-200 font-medium">Processing Mode</span>
                        <button
                            onClick={() => setShowDetails(!showDetails)}
                            className="text-xs text-teal-400 hover:text-teal-300 transition-colors flex items-center space-x-1"
                        >
                            <span>{showDetails ? 'Hide' : 'View'} Details</span>
                            <svg 
                                className={`w-4 h-4 transition-transform duration-200 ${showDetails ? 'rotate-180' : ''}`}
                                fill="none" 
                                stroke="currentColor" 
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                    </div>
                    
                    {/* Toggle Switch */}
                    <div className="flex items-center justify-center space-x-3 py-2">
                        <span className={`text-sm ${!useCloud ? 'text-teal-400 font-semibold' : 'text-gray-400'}`}>
                            Local
                        </span>
                        <button
                            onClick={() => setUseCloud(!useCloud)}
                            disabled={isLoading}
                            className={`relative w-14 h-7 rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 focus:ring-offset-gray-900 ${
                                useCloud ? 'bg-blue-500' : 'bg-teal-500'
                            } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                        >
                            <span
                                className={`absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full transition-transform duration-300 ${
                                    useCloud ? 'translate-x-7' : 'translate-x-0'
                                }`}
                            />
                        </button>
                        <span className={`text-sm ${useCloud ? 'text-blue-400 font-semibold' : 'text-gray-400'}`}>
                            Cloud
                        </span>
                    </div>

                    {/* Details Section */}
                    {showDetails && (
                        <div className="mt-3 pt-3 border-t border-gray-700/50 space-y-3 text-left">
                            {/* Local Mode */}
                            <div className={`p-3 rounded-lg border transition-all ${
                                !useCloud ? 'bg-teal-500/10 border-teal-500/30' : 'bg-gray-800/20 border-gray-700/30'
                            }`}>
                                <h4 className="text-sm font-semibold text-teal-400 mb-2">🔒 Local Mode</h4>
                                <div className="space-y-1 text-xs">
                                    <div className="flex items-start space-x-2">
                                        <span className="text-green-400 mt-0.5">✓</span>
                                        <span className="text-gray-300">100% Private (never leaves your device)</span>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <span className="text-green-400 mt-0.5">✓</span>
                                        <span className="text-gray-300">Completely Free</span>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <span className="text-yellow-400 mt-0.5">⚠</span>
                                        <span className="text-gray-400">Longer processing time</span>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <span className="text-gray-500 mt-0.5">•</span>
                                        <span className="text-gray-500">Uses local Ollama models</span>
                                    </div>
                                </div>
                            </div>

                            {/* Cloud Mode */}
                            <div className={`p-3 rounded-lg border transition-all ${
                                useCloud ? 'bg-blue-500/10 border-blue-500/30' : 'bg-gray-800/20 border-gray-700/30'
                            }`}>
                                <h4 className="text-sm font-semibold text-blue-400 mb-2">☁️ Cloud Mode</h4>
                                <div className="space-y-1 text-xs">
                                    <div className="flex items-start space-x-2">
                                        <span className="text-green-400 mt-0.5">✓</span>
                                        <span className="text-gray-300">Much faster processing</span>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <span className="text-green-400 mt-0.5">✓</span>
                                        <span className="text-gray-300">Free tier (Groq API)</span>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <span className="text-yellow-400 mt-0.5">⚠</span>
                                        <span className="text-gray-400">ToS data shared with Groq</span>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <span className="text-yellow-400 mt-0.5">⚠</span>
                                        <span className="text-gray-400">Rate limits apply (batch processing)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <label
                    htmlFor="tos-file"
                    className="group px-8 py-4 bg-gray-800/50 hover:bg-gray-700/50 text-gray-200 font-semibold border-2 border-gray-600/50 hover:border-teal-500/50 rounded-xl transition-all duration-300 cursor-pointer flex items-center space-x-3 backdrop-blur-sm transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                    <svg
                        className="w-6 h-6 text-teal-400 group-hover:text-teal-300 transition-colors duration-300"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                    </svg>
                    <span>Upload Terms of Service</span>
                </label>
                
                <input
                    id="tos-file"
                    type="file"
                    accept=".txt,.pdf,.html,.htm"
                    className="hidden"
                    onChange={handleFileChange}
                    disabled={isLoading}
                />
                
                <button
                    className={`px-10 py-4 bg-gradient-to-r text-white font-bold rounded-xl flex items-center space-x-3 ${
                        file && !isLoading
                            ? 'from-teal-500 to-blue-500 hover:from-teal-400 hover:to-blue-400 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl cursor-pointer'
                            : 'from-gray-600 to-gray-700 cursor-not-allowed opacity-60'
                    }`}
                    onClick={handleAnalyze}
                    disabled={isLoading || !file}
                >
                    {isLoading ? (
                        <>
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            <span>Analyzing...</span>
                        </>
                    ) : (
                        <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>Start Analysis</span>
                        </>
                    )}
                </button>

                {/* Progress Bar and Info */}
                {isLoading && (
                    <div className="w-full max-w-md space-y-3">
                        <div className="bg-gray-800/40 p-4 rounded-lg border border-gray-700/50">
                            <div className="flex items-center space-x-2 mb-3 pb-3 border-b border-gray-700/50">
                                <svg className="w-4 h-4 text-teal-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <span className="text-sm font-medium text-teal-300 truncate">{file?.name}</span>
                            </div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm text-gray-300">{progressMessage}</span>
                                <span className="text-sm font-semibold text-teal-400">{Math.round(progress)}%</span>
                            </div>
                            <div className="w-full bg-gray-700/50 rounded-full h-2 overflow-hidden border border-gray-600/30">
                                <div
                                    className="bg-gradient-to-r from-teal-500 to-blue-500 h-full transition-all duration-300 ease-out"
                                    style={{ width: `${progress}%` }}
                                ></div>
                            </div>
                            <p className="text-xs text-gray-400 mt-2">
                                Expected time: {useCloud ? '2-3 minutes' : '15-20 minutes'}
                            </p>
                        </div>
                    </div>
                )}
            </div>
            
            {file && !isLoading && (
                <div className="relative group text-gray-300 text-sm mt-4 bg-gray-800/30 px-4 py-3 rounded-lg mx-auto max-w-md cursor-pointer transition-all duration-200 hover:bg-gray-800/40">
                    <div className="text-center">
                        <span className="text-gray-400">Selected: </span>
                        <span className="font-medium text-teal-300">{file.name}</span>
                    </div>
                    {/* X button that appears on hover */}
                    <button
                        onClick={handleFileRemove}
                        className="absolute top-2 right-2 w-4 h-4 bg-gray-600/80 hover:bg-gray-500 text-gray-300 hover:text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200 text-xs font-normal leading-none"
                        title="Remove file"
                    >
                        ×
                    </button>
                </div>
            )}
        </div>
    );
}

export default ToSInput;