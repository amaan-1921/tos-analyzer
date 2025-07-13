function Navbar() {
  return (
    <nav className="bg-dark-secondary p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-100">ToS Analyzer</h1>
        <div className="space-x-4">
          <a href="#" className="text-gray-300 hover:text-accent-teal">Home</a>
          <a href="#" className="text-gray-300 hover:text-accent-teal">About</a>
          <a href="#" className="text-gray-300 hover:text-accent-teal">How It Works</a>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;