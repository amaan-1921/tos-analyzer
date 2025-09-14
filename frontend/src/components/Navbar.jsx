function Navbar({ setCurrentPage, goHome }) {
  const handleHomeClick = () => {
    if (goHome) {
      goHome();
    } else if (setCurrentPage) {
      setCurrentPage('home');
    }
  };

  const handleAboutClick = () => {
    if (setCurrentPage) {
      setCurrentPage('about');
    }
  };

  const handleHowItWorksClick = () => {
    if (setCurrentPage) {
      setCurrentPage('how-it-works');
    }
  };

  return (
    <nav className="bg-black/95 backdrop-blur-sm border-b border-gray-700/50 p-4 shadow-xl">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-medium text-white flex items-center font-serif">
          RiskWise
          <span className="ml-3 text-sm font-normal text-gray-400 font-sans">Advanced ToS Analysis</span>
        </h1>
        <div className="space-x-6">
          <button 
            onClick={handleHomeClick}
            className="text-gray-300 hover:text-teal-400 transition-colors duration-300 font-medium cursor-pointer"
          >
            Home
          </button>
          <button 
            onClick={handleAboutClick}
            className="text-gray-300 hover:text-teal-400 transition-colors duration-300 font-medium cursor-pointer"
          >
            About
          </button>
          <button 
            onClick={handleHowItWorksClick}
            className="text-gray-300 hover:text-teal-400 transition-colors duration-300 font-medium cursor-pointer"
          >
            How It Works
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;