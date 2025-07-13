import { useState } from 'react';
import { useResults } from './ResultsContext';

function ToSInput() {
    const [tosText, setTosText] = useState('');
    const [file, setFile] = useState(null);
    const { setResults, setIsLoading, isLoading, setError } = useResults();

    const handleAnalyze = async () => {
        if (!tosText && !file) {
            setError('Please enter ToS text or upload a file.');
            return;
        }
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: tosText }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            setResults(data.results || []);
        } catch (err) {
            setError(`Failed to analyze ToS: ${err.message}`);
            setResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        if (selectedFile) {
            if (selectedFile.type === "text/plain") {
                const reader = new FileReader();
                reader.onload = (event) => setTosText(event.target.result);
                reader.readAsText(selectedFile);
            } else if (selectedFile.type === "application/pdf") {
                setError("PDF support coming soon! Please use a .txt file.");
            } else {
                setError("Please upload a .txt file.");
            }
        }
    };

    return (
        <div className="w-full max-w-2xl mb-6">
            <textarea
                className="w-full h-40 p-4 bg-dark-secondary text-light-text border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-teal"
                placeholder="Paste ToS text here..."
                value={tosText}
                onChange={(e) => setTosText(e.target.value)}
            ></textarea>
            <div className="mt-4 flex items-center space-x-4">
                <label
                    htmlFor="tos-file"
                    className="animate-button px-6 py-3 bg-dark-secondary text-light-text font-semibold border border-gray-700 rounded-md hover:bg-gray-600 transition duration-300 cursor-pointer flex items-center space-x-2"
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
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                    </svg>
                    <span>Upload ToS File</span>
                </label>
                <input
                    id="tos-file"
                    type="file"
                    accept=".txt"
                    className="hidden"
                    onChange={handleFileChange}
                />
                <button
                    className="px-6 py-3 bg-accent-teal text-gray-900 font-semibold rounded-md hover:bg-teal-400 transition duration-300 disabled:opacity-50"
                    onClick={handleAnalyze}
                    disabled={isLoading || (!tosText && !file)}
                >
                    {isLoading ? "Analyzing..." : "Analyze"}
                </button>
                {file && (
                    <p className="text-gray-400 text-sm mt-2">Selected: {file.name}</p>
                )}
            </div>
        </div>
    );
}

export default ToSInput;