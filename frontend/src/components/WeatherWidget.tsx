import React from 'react'

interface WeatherWidgetProps {
  temp: string
  condition: string
  location: string
}

const WeatherWidget: React.FC<WeatherWidgetProps> = ({ temp, condition, location }) => {
  return (
    <div className="bg-black/30 backdrop-blur-lg rounded-2xl p-4 flex items-center text-white border border-blue-500/20 shadow-lg shadow-blue-500/5 relative overflow-hidden group transition-all duration-300 hover:border-blue-500/30">
      {/* Efeito de luz de fundo */}
      <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
      
      {/* Background circular para o ícone */}
      <div className="mr-4 relative z-10">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center border border-blue-400/20">
          {condition === 'Clear' ? (
            <svg className="w-7 h-7 text-yellow-300 animate-pulse-slow" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3v1m0 16v1m-9-9H2m17 0h1M5.6 5.6l.7.7m12.1-.7l-.7.7M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          ) : condition === 'Cloudy' ? (
            <svg className="w-7 h-7 text-gray-300" viewBox="0 0 24 24" fill="currentColor">
              <path d="M4 14a1 1 0 100-2 1 1 0 000 2zm11-4a5 5 0 100 10h1a7 7 0 10-8-8 3 3 0 100 6h7a3 3 0 100-6h-1a5.06 5.06 0 011-2z" />
            </svg>
          ) : (
            <svg className="w-7 h-7 text-blue-300" viewBox="0 0 24 24" fill="currentColor">
              <path d="M13 9.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zm-2 3a1.5 1.5 0 110 3 1.5 1.5 0 010-3zm-8-7a5 5 0 1010 0 5 5 0 00-10 0zm2 17a5 5 0 1110 0 5 5 0 01-10 0z" />
            </svg>
          )}
        </div>
      </div>

      {/* Informações de temperatura */}
      <div className="flex flex-col relative z-10">
        <div className="flex items-center">
          <span className="text-xl font-light bg-clip-text text-transparent bg-gradient-to-r from-blue-300 to-blue-100">{temp}</span>
          <span className="ml-2 text-blue-300/70">{condition}</span>
        </div>
        <div className="text-sm text-blue-300/60 font-light">
          H: 26° L: 15°
        </div>
        <div className="text-xs text-blue-400/50">
          {location}
        </div>
      </div>
    </div>
  )
}

export default WeatherWidget 