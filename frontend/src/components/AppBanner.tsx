import React from 'react'

const AppBanner: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-black/40 to-blue-900/10 backdrop-blur-lg rounded-2xl p-4 flex justify-between items-center border border-blue-500/20 shadow-lg shadow-blue-500/5 relative overflow-hidden group hover:border-blue-500/30 transition-all duration-300">
      {/* Efeito de luz pulsante */}
      <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
      
      {/* Efeito de grid futurista */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="flex-1 relative z-10">
        <h3 className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 font-medium text-sm">Introducing our Windows App</h3>
        <p className="text-blue-300/60 text-xs font-light">Install the native Windows App</p>
      </div>
      
      <div className="flex-shrink-0 relative z-10">
        <button className="bg-gradient-to-br from-blue-500/20 to-blue-800/20 hover:from-blue-500/30 hover:to-blue-600/30 p-2 rounded-xl transition-all duration-300 border border-blue-500/30 group-hover:shadow-lg group-hover:shadow-blue-500/20">
          <svg className="w-8 h-8 text-blue-400 group-hover:text-blue-300 transition-all duration-300" viewBox="0 0 24 24" fill="currentColor">
            <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/>
          </svg>
        </button>
      </div>
    </div>
  )
}

export default AppBanner 