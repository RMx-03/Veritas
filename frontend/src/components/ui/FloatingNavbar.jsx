function FloatingNavbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <img 
                  src="/VeritasLogo.png" 
                  alt="Veritas - Pocket Nutrition Scientist" 
                  className="h-10 w-auto"
                />
              </div>
              
              <div className="hidden md:flex items-center space-x-8">
                <a href="#" className="text-primary-800 hover:text-primary-900 transition-all duration-300 font-medium hover:scale-105 relative group">
                  How it Works
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-primary-500 to-secondary-500 transition-all duration-300 group-hover:w-full"></span>
                </a>
                <a href="#" className="text-primary-800 hover:text-primary-900 transition-all duration-300 font-medium hover:scale-105 relative group">
                  About
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-primary-500 to-secondary-500 transition-all duration-300 group-hover:w-full"></span>
                </a>
                <a href="#" className="text-primary-800 hover:text-primary-900 transition-all duration-300 font-medium hover:scale-105 relative group">
                  Contact
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-primary-500 to-secondary-500 transition-all duration-300 group-hover:w-full"></span>
                </a>
              </div>

              {/* Mobile menu button */}
              <button className="md:hidden p-2 rounded-xl bg-white/20 backdrop-blur-sm border border-white/30 hover:bg-white/30 transition-all duration-300 shadow-lg">
                <svg className="w-5 h-5 text-primary-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default FloatingNavbar
