import React from 'react'
import ReactMarkdown from 'react-markdown'

interface ResultsPanelProps {
  results: string | null
  loading: boolean
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results, loading }) => {
  if (loading) {
    return (
      <div className="bg-black/30 backdrop-blur-lg rounded-2xl p-6 mt-4 border border-blue-500/20 shadow-lg shadow-blue-500/5 overflow-hidden relative">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-2xl blur-xl"></div>
        <div className="flex flex-col justify-center items-center h-32 relative z-10">
          {/* Círculo pulsante */}
          <div className="relative">
            <div className="absolute -inset-4 rounded-full bg-blue-500/20 blur-md animate-pulse-slow"></div>
            <div className="animate-spin rounded-full h-10 w-10 border-2 border-blue-500 border-t-transparent relative"></div>
          </div>
          <span className="mt-4 text-blue-300/80 font-light">Pesquisando...</span>
        </div>
      </div>
    )
  }

  if (!results) {
    return null
  }

  return (
    <div className="bg-black/30 backdrop-blur-lg rounded-2xl p-6 mt-4 border border-blue-500/20 shadow-lg shadow-blue-500/5 relative overflow-hidden group hover:border-blue-500/30 transition-all duration-300">
      {/* Efeito de luz de fundo */}
      <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
      
      <div className="prose prose-invert max-w-none relative z-10">
        <ReactMarkdown className="text-blue-100/90 prose-headings:text-transparent prose-headings:bg-clip-text prose-headings:bg-gradient-to-r prose-headings:from-blue-300 prose-headings:to-purple-300 prose-headings:font-light prose-p:text-blue-100/80 prose-p:font-light prose-a:text-blue-400 prose-a:no-underline hover:prose-a:text-blue-300 prose-a:transition-colors prose-a:duration-300 prose-strong:text-blue-200 prose-code:text-blue-300 prose-pre:bg-black/50 prose-pre:border prose-pre:border-blue-500/20">
          {results}
        </ReactMarkdown>
      </div>
    </div>
  )
}

export default ResultsPanel 