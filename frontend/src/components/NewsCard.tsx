import React from 'react'

interface NewsCardProps {
  title: string
  image: string
}

const NewsCard: React.FC<NewsCardProps> = ({ title, image }) => {
  // Imagem base64 simples para fallback
  const fallbackImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjMzQ5OGRiIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiNmZmZmZmYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiPk48L3RleHQ+PC9zdmc+';

  return (
    <div className="bg-black/30 backdrop-blur-lg rounded-2xl p-3 flex items-center hover:bg-blue-500/5 transition-all duration-300 cursor-pointer border border-blue-500/10 hover:border-blue-500/30 shadow-lg shadow-blue-500/5 group relative overflow-hidden">
      {/* Efeito de luz de fundo */}
      <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-2xl blur-md opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
      
      <div className="flex-shrink-0 mr-3 relative z-10">
        <div className="rounded-full overflow-hidden bg-gradient-to-br from-blue-500/20 to-purple-500/20 p-0.5">
          <img 
            src={image} 
            alt="News thumbnail" 
            className="w-10 h-10 object-cover rounded-full ring-1 ring-blue-500/20 group-hover:ring-blue-500/40 transition-all duration-300"
            onError={(e) => {
              // Fallback para imagem local em base64
              (e.target as HTMLImageElement).src = fallbackImage;
            }}
          />
        </div>
      </div>
      <div className="text-sm text-blue-100/90 line-clamp-2 flex-1 relative z-10 font-light">
        {title}
      </div>
    </div>
  )
}

export default NewsCard 