import { useState } from 'react';
import { useResults } from './ResultsContext';

function ToSInput() {
    const [file, setFile] = useState(null);
    const { setResults, setIsLoading, isLoading, setError, setHasAnalysisResults } = useResults();

    const handleAnalyze = async () => {
        if (!file) {
            setError('Please upload a file.');
            return;
        }
        
        setIsLoading(true);
        setError(null);
        setHasAnalysisResults(false);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('http://localhost:8000/ingest', {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            setResults(data || []);
            setHasAnalysisResults(true);
        } catch (err) {
            setError(`Failed to analyze ToS: ${err.message}`);
            setResults([]);
            setHasAnalysisResults(false);
        } finally {
            setIsLoading(false);
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
        }
    };

    const handleFileRemove = () => {
        setFile(null);
        setResults([]);
        setHasAnalysisResults(false);
        setError(null);
        // Reset the file input
        const fileInput = document.getElementById('tos-file');
        if (fileInput) {
            fileInput.value = '';
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto text-center">
            <div className="flex flex-col items-center space-y-4">
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
            </div>
            
            {file && (
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