import React, { useState, useEffect } from 'react'
import { providerService } from '../services/api'

interface Model {
  id: string
  name: string
}

interface Provider {
  name: string
  models: Model[]
  requires_key: boolean
  key_env: string
}

interface ModelsDropdownProps {
  selectedModel: string
  onModelChange: (model: string) => void
}

const ModelsDropdown: React.FC<ModelsDropdownProps> = ({ selectedModel, onModelChange }) => {
  const [providers, setProviders] = useState<Record<string, Provider>>({})
  const [isOpen, setIsOpen] = useState(() => {
    // Inicialmente, o dropdown fica fechado
    return false
  })
  const [loading, setLoading] = useState(true)

  // Modelos padrão caso a API não retorne nenhum
  const defaultProviders: Record<string, Provider> = {
    "google": {
      "name": "Google",
      "models": [
        {"id": "gemini-2.5-pro-preview", "name": "Gemini 2.5 Pro Preview"},
        {"id": "gemini-2.5-flash-preview-04-17", "name": "Gemini 2.5 Flash"},
      ],
      "requires_key": true,
      "key_env": "GEMINI_API_KEY"
    },
    "openai": {
      "name": "OpenAI",
      "models": [
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4.1", "name": "GPT-4.1"},
      ],
      "requires_key": true,
      "key_env": "OPENAI_API_KEY"
    },
    "anthropic": {
      "name": "Anthropic",
      "models": [
        {"id": "claude-3.7-sonnet", "name": "Claude 3.7 Sonnet"},
        {"id": "claude-3.5", "name": "Claude 3.5"}
      ],
      "requires_key": true,
      "key_env": "ANTHROPIC_API_KEY"
    }
  }

  // Buscar provedores disponíveis
  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setLoading(true)
        const data = await providerService.getProviders()
        
        if (data && Object.keys(data).length > 0) {
          setProviders(data)
        } else {
          // Usar provedores padrão se a API não retornar dados
          setProviders(defaultProviders)
          console.warn('Usando provedores padrão devido à falha na API')
        }
      } catch (error) {
        console.error('Erro ao buscar provedores:', error)
        // Usar provedores padrão em caso de erro
        setProviders(defaultProviders)
      } finally {
        setLoading(false)
      }
    }

    fetchProviders()
  }, [])

  // Efeito para fechar o dropdown quando clicar fora dele
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (isOpen && !target.closest('.models-dropdown')) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // Encontrar o nome do modelo selecionado
  const getSelectedModelName = (): string => {
    // Se não houver modelo selecionado, usar o primeiro modelo do primeiro provedor
    if (!selectedModel && Object.keys(providers).length > 0) {
      const firstProviderId = Object.keys(providers)[0]
      if (providers[firstProviderId].models.length > 0) {
        // Se não houver modelo selecionado, selecionar o primeiro disponível
        const firstModel = providers[firstProviderId].models[0]
        setTimeout(() => onModelChange(firstModel.id), 0)
        return firstModel.name
      }
    }
    
    for (const providerId in providers) {
      const provider = providers[providerId]
      const model = provider.models.find(m => m.id === selectedModel)
      if (model) return model.name
    }
    return 'Selecionar modelo'
  }

  return (
    <div className="relative models-dropdown">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center text-blue-400 text-xs py-1 px-2 rounded-full hover:bg-blue-500/10 border border-blue-500/20 transition-all duration-300"
      >
        <span className="mr-1 flex items-center">
          <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
          {getSelectedModelName()}
        </span>
        <svg className={`w-3.5 h-3.5 transition-transform duration-300 ${isOpen ? 'transform rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
          <path
            fillRule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-black/80 backdrop-blur-lg border border-blue-500/30 rounded-xl shadow-lg shadow-blue-500/10 z-20 overflow-hidden animate-fadeIn">
          {loading ? (
            <div className="p-3 text-blue-300/70 text-sm font-light">Carregando modelos...</div>
          ) : (
            <div className="py-2">
              {Object.entries(providers).map(([providerId, provider]) => (
                <div key={providerId} className="px-2 py-1">
                  <div className="text-blue-300 text-xs font-semibold py-1 px-2 mb-1 border-b border-blue-500/20">
                    {provider.name}
                  </div>
                  <div className="space-y-1">
                    {provider.models.map(model => (
                      <button
                        key={model.id}
                        onClick={() => {
                          onModelChange(model.id)
                          setIsOpen(false)
                        }}
                        className={`w-full text-left px-3 py-1.5 text-sm rounded-lg ${
                          selectedModel === model.id
                            ? 'bg-gradient-to-r from-blue-600/80 to-blue-500/80 text-white'
                            : 'text-blue-200/80 hover:bg-blue-500/10 transition-all duration-300'
                        }`}
                      >
                        {model.name}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ModelsDropdown 