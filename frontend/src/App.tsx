import React, { useState, useEffect } from 'react'
import './App.css'
import { weatherService, newsService, searchService, providerService } from './services/api'

// Componentes
import { WeatherWidget, NewsCard, AppBanner, ModelsDropdown, ResultsPanel } from './components'

// Lista de modelos compatíveis com o modo de pesquisa profunda (DeepResearcher)
const SUPPORTED_RESEARCH_MODELS = ['gemini-2.5-flash-preview-04-17', 'gemini-2.0-flash'];

// Interface para itens de notícias
interface NewsItem {
  id: number;
  title: string;
  image: string;
  url?: string;
}

function App() {
  // Usar localStorage para persistir a consulta
  const [query, setQuery] = useState<string>(() => {
    const savedQuery = localStorage.getItem('lastQuery')
    return savedQuery || ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [isResearching, setIsResearching] = useState(false)
  // Usar localStorage para persistir o modelo selecionado
  const [model, setModel] = useState<string>(() => {
    const savedModel = localStorage.getItem('selectedModel')
    // Usar gemini-2.5-pro-preview por padrão, pois é o único com API key configurada
    return savedModel || 'gemini-2.5-pro-preview'
  })
  // Usar localStorage para persistir o modo de pesquisa
  const [mode, setMode] = useState<'search' | 'research'>(() => {
    const savedMode = localStorage.getItem('searchMode') as 'search' | 'research'
    return savedMode || 'search'
  })
  // Estado para controlar o uso do planner
  const [usePlanner, setUsePlanner] = useState<boolean>(() => 
    localStorage.getItem('usePlanner') !== 'false'
  )
  // Estado para controlar o modo headless (navegador visível ou não)
  const [headless, setHeadless] = useState<boolean>(() => 
    localStorage.getItem('headlessMode') !== 'false'
  )
  const [weather, setWeather] = useState({ temp: '18°C', condition: 'Clear', location: 'Estalo' })
  
  // Estado para o ID da pesquisa atual
  const [researchId, setResearchId] = useState<string | null>(null)
  
  // Estado para controlar a exibição do modal de configurações
  const [showConfigModal, setShowConfigModal] = useState<boolean>(false)
  
  // Estado para notificação de feedback
  const [notification, setNotification] = useState<{
    show: boolean,
    type?: 'success' | 'warning' | 'error',
    message: string
  }>({
    show: false,
    type: 'success',
    message: ''
  })
  
  // Imagem base64 simples para notícias (quadrado azul com 'N')
  const defaultNewsImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjMzQ5OGRiIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiNmZmZmZmYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiPk48L3RleHQ+PC9zdmc+';
  
  const [news, setNews] = useState<NewsItem[]>([
    {
      id: 1,
      title: 'Trump blocks Musk from Pentagon briefing',
      image: defaultNewsImage
    },
    {
      id: 2,
      title: 'Elon Musk seeks more children via social media',
      image: defaultNewsImage
    }
  ])
  // Usar localStorage para persistir os resultados da pesquisa
  const [results, setResults] = useState<string | null>(() => {
    const savedResults = localStorage.getItem('lastResults')
    return savedResults
  })

  // Atualizar localStorage quando o modelo mudar
  useEffect(() => {
    localStorage.setItem('selectedModel', model)
  }, [model])
  
  // Atualizar localStorage quando o modo mudar
  useEffect(() => {
    localStorage.setItem('searchMode', mode)
  }, [mode])
  
  // Atualizar localStorage quando o planner mudar
  useEffect(() => {
    localStorage.setItem('usePlanner', String(usePlanner))
  }, [usePlanner])
  
  // Atualizar localStorage quando a consulta mudar
  useEffect(() => {
    if (query) {
      localStorage.setItem('lastQuery', query)
    }
  }, [query])
  
  // Atualizar localStorage quando os resultados mudarem
  useEffect(() => {
    if (results) {
      localStorage.setItem('lastResults', results)
    }
  }, [results])
  
  // Atualizar o localStorage quando o modo headless mudar
  useEffect(() => {
    localStorage.setItem('headlessMode', String(headless))
  }, [headless])

  // Função para buscar os dados meteorológicos
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await weatherService.getWeather();
        if (response.data && response.status === 'success') {
          setWeather(response.data);
        }
      } catch (error) {
        console.error('Erro ao buscar dados meteorológicos:', error);
      }
    };
    
    fetchWeather();
  }, []);

  // Função para buscar as notícias
  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await newsService.getNews();
        if (response.data && response.status === 'success') {
          // Garantir que as notícias usem a imagem padrão segura
          const newsWithDefaultImage = response.data.map((item: NewsItem) => ({
            ...item,
            image: defaultNewsImage
          }));
          
          setNews(newsWithDefaultImage);
        }
      } catch (error) {
        console.error('Erro ao buscar notícias:', error);
      }
    };
    
    fetchNews();
  }, []);

  // Função para buscar os provedores disponíveis
  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const data = await providerService.getProviders();
        // Se houver provedores, selecionar o primeiro modelo disponível
        if (data && Object.keys(data).length > 0) {
          const firstProviderId = Object.keys(data)[0];
          if (data[firstProviderId].models.length > 0) {
            setModel(data[firstProviderId].models[0].id);
          }
        }
      } catch (error) {
        console.error('Erro ao buscar provedores:', error);
      }
    };
    
    fetchProviders();
  }, []);

  // Função para mudar o modo de pesquisa
  const handleModeChange = (newMode: 'search' | 'research') => {
    setMode(newMode)
    // Limpar os resultados quando mudar de modo
    setResults(null)
  }

  // Função para realizar pesquisa
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!query.trim()) return
    
    setIsLoading(true)
    
    try {
      if (mode === 'research') {
        // Modo de pesquisa profunda com o Deep Researcher
        setIsResearching(true)
        
        if (!SUPPORTED_RESEARCH_MODELS.includes(model)) {
          setNotification({
            type: 'warning',
            show: true,
            message: 'O modelo selecionado não é compatível com o modo Research. Alterando para Gemini 2.5 Pro.'
          })
          setModel('gemini-2.5-pro-preview')
          return
        }
        
        // A API usará a chave configurada no backend baseada no modelo selecionado
        // O provider será determinado automaticamente com base no modelo
        const provider = determineProviderFromModel(model);
        
        // Verificar se estamos usando o Google, que é o único provedor com API key configurada
        if (provider !== 'google' && model !== 'gemini-2.5-pro-preview' && model !== 'gemini-2.0-flash') {
          setNotification({
            show: true,
            type: 'warning',
            message: 'Apenas modelos do Google (Gemini) estão disponíveis no momento. Alterando para Gemini 2.5.'
          });
          setModel('gemini-2.5-pro-preview');
          setIsResearching(false);
          setIsLoading(false);
          return;
        }
        
        // Inicia uma pesquisa profunda com o parâmetro planner e headless
        const response = await searchService.startDeepResearch(query, model, usePlanner, headless)
        
        if (response.status === 'success') {
          // Se a pesquisa foi iniciada com sucesso, verifica o status periodicamente
          const currentResearchId = response.research_id
          setResearchId(currentResearchId)
          
          // Verificar o status a cada 5 segundos
          const intervalId = setInterval(async () => {
            try {
              const statusResponse = await searchService.getResearchStatus(currentResearchId)
              
              // A statusResponse contém o objeto da pesquisa diretamente 
              // O objeto retornado pela API possui uma propriedade "status" que indica
              // o status atual da pesquisa (running, completed, error, etc.)
              console.log("Status da pesquisa:", statusResponse) 
              
              if (statusResponse.status === 'completed') {
                // Pesquisa concluída, buscar resultados
                clearInterval(intervalId)
                
                const reportResponse = await searchService.getResearchReport(currentResearchId)
                if (reportResponse.status === 'success') {
                  // O relatório está no campo "report" da resposta
                  setResults(reportResponse.report)
                }
                
                setIsResearching(false)
                setIsLoading(false)
              } else if (statusResponse.status === 'error') {
                // Pesquisa falhou
                clearInterval(intervalId)
                console.error('A pesquisa profunda falhou:', statusResponse.error)
                setIsResearching(false)
                setIsLoading(false)
              }
              // Se estiver em andamento (status === 'running'), continua verificando
              
            } catch (error) {
              clearInterval(intervalId)
              console.error('Erro ao verificar status da pesquisa:', error)
              setIsResearching(false)
              setIsLoading(false)
            }
          }, 5000)
        }
      } else {
        // Modo de pesquisa tradicional com headless
        const response = await searchService.search(query, model, mode, headless)
        
        if (response.status === 'success') {
          setResults(response.results)
        }
        setIsLoading(false)
      }
    } catch (error: any) {
      console.error('Erro na pesquisa:', error)
      
      // Mostrar mensagem de erro específica para o usuário
      let errorMessage = 'Ocorreu um erro ao realizar a pesquisa.';
      
      if (error.response && error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setNotification({
        show: true,
        type: 'error',
        message: errorMessage
      });
      
      setIsLoading(false)
      setIsResearching(false)
    }
  }
  
  // Função para determinar o provedor com base no modelo
  const determineProviderFromModel = (modelId: string): string => {
    if (modelId.startsWith('gpt-')) return 'openai';
    if (modelId.startsWith('gemini-')) return 'google';
    if (modelId.startsWith('claude-')) return 'anthropic';
    if (modelId.startsWith('deepseek-')) return 'deepseek';
    if (modelId.startsWith('grok-')) return 'xai';
    
    // Padrão para OpenAI se não conseguir determinar
    return 'openai';
  }
  
  // Função para limpar todo o histórico e dados salvos
  const clearHistory = () => {
    localStorage.removeItem('lastQuery')
    localStorage.removeItem('lastResults')
    localStorage.removeItem('selectedModel')
    localStorage.removeItem('searchMode')
    localStorage.removeItem('usePlanner')
    localStorage.removeItem('headlessMode')
    
    setQuery('')
    setResults(null)
    setModel('gemini-2.5-pro-preview')
    setMode('search')
    setUsePlanner(true)
    setHeadless(true)
    setResearchId(null)
    
    setNotification({
      type: 'success',
      show: true,
      message: 'Histórico limpo com sucesso!'
    })
  }

  // Efeito para esconder a notificação após um tempo
  useEffect(() => {
    if (notification.show) {
      const timer = setTimeout(() => {
        setNotification({
          show: false,
          message: ''
        })
      }, 3000)
      
      return () => clearTimeout(timer)
    }
  }, [notification.show])
  
  // Função para abrir/fechar o modal de configurações
  const toggleConfigModal = () => {
    setShowConfigModal(!showConfigModal)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white flex flex-col">
      {/* Efeito de scanline futurista */}
      <div className="scanline"></div>
      
      {/* Notificação */}
      {notification.show && (
        <div className={`fixed top-5 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg shadow-lg z-50 flex items-center ${
          notification.type === 'success' ? 'bg-green-500/90 text-white' : 
          notification.type === 'warning' ? 'bg-yellow-500/90 text-white' : 
          'bg-red-500/90 text-white'
        }`}>
          <svg className="w-5 h-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            {notification.type === 'success' ? (
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            ) : notification.type === 'warning' ? (
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            ) : (
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            )}
          </svg>
          {notification.message}
        </div>
      )}
      
      {/* Efeito de partículas/grid futurista */}
      <div className="fixed inset-0 z-0 opacity-5">
        <div className="absolute inset-0 bg-grid-pattern"></div>
      </div>
      
      {/* Barra lateral */}
      <div className="fixed left-0 top-0 h-full w-14 bg-black/30 backdrop-blur-md border-r border-blue-500/20 flex flex-col items-center py-6 z-10">
        {/* Logo */}
        <button className="w-8 h-8 mb-10 relative group">
          <svg viewBox="0 0 24 24" className="w-8 h-8 text-blue-400 group-hover:text-blue-300 transition-all duration-300" fill="currentColor">
            <path d="M12 2L2 12h3v8h14v-8h3L12 2zm0 15c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z" />
          </svg>
          <div className="absolute -inset-1 bg-blue-500/20 rounded-full blur scale-0 group-hover:scale-100 transition-all duration-300"></div>
        </button>
        
        {/* Novo chat */}
        <button className="w-9 h-9 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center mb-6 hover:bg-blue-500/20 transition-all duration-300 relative group">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          <div className="absolute -inset-0.5 bg-blue-400/20 rounded-full blur scale-0 group-hover:scale-100 transition-all duration-300"></div>
        </button>
        
        {/* Menu de navegação */}
        <div className="space-y-6">
          {/* Busca */}
          <button className="w-9 h-9 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center hover:bg-blue-500/20 transition-all duration-300 relative group">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
            <div className="absolute -inset-0.5 bg-blue-400/20 rounded-full blur scale-0 group-hover:scale-100 transition-all duration-300"></div>
          </button>
          
          {/* Globo */}
          <button className="w-9 h-9 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center hover:bg-blue-500/20 transition-all duration-300 relative group">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM4.332 8.027a6.012 6.012 0 011.912-2.706C6.512 5.73 6.974 6 7.5 6A1.5 1.5 0 019 7.5V8a2 2 0 004 0 2 2 0 011.523-1.943A5.977 5.977 0 0116 10c0 .34-.028.675-.083 1H15a2 2 0 00-2 2v2.197A5.973 5.973 0 0110 16v-2a2 2 0 00-2-2 2 2 0 01-2-2 2 2 0 00-1.668-1.973z" clipRule="evenodd" />
            </svg>
            <div className="absolute -inset-0.5 bg-blue-400/20 rounded-full blur scale-0 group-hover:scale-100 transition-all duration-300"></div>
          </button>
          
          {/* Estrela */}
          <button className="w-9 h-9 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center hover:bg-blue-500/20 transition-all duration-300 relative group">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <div className="absolute -inset-0.5 bg-blue-400/20 rounded-full blur scale-0 group-hover:scale-100 transition-all duration-300"></div>
          </button>
          
          {/* Notificações */}
          <button className="w-9 h-9 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center hover:bg-blue-500/20 transition-all duration-300 relative group">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
            </svg>
            <div className="absolute -inset-0.5 bg-blue-400/20 rounded-full blur scale-0 group-hover:scale-100 transition-all duration-300"></div>
          </button>
        </div>
      </div>
      
      {/* Conteúdo principal */}
      <div className="ml-14 flex-1 flex flex-col items-center justify-center p-4 relative z-1">
        {/* Título principal */}
        <div className="text-center mb-4 mt-6">
          <h1 className="text-5xl font-light bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">O que você deseja saber?</h1>
        </div>
        
        {/* Resultados da pesquisa */}
        {(results || isLoading) && (
          <div className="w-full max-w-2xl mb-6">
            <ResultsPanel results={results} loading={isLoading} />
          </div>
        )}
        
        {/* Formulário de pesquisa - agora input chat */}
        <div className="w-full max-w-2xl mb-3">
          <form onSubmit={handleSearch} className="relative">
            <div className="absolute inset-0 bg-blue-500/10 rounded-2xl blur-md"></div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything..."
              className="input-cursor-top input-aligned-placeholder w-full px-6 py-10 bg-black/40 backdrop-blur-lg rounded-2xl border border-blue-500/30 focus:outline-none focus:border-blue-500/70 focus:ring-2 focus:ring-blue-500/30 text-gray-200 shadow-lg shadow-blue-500/10 z-10 relative transition-all duration-300 placeholder:text-blue-300/60 placeholder:absolute placeholder:top-3 placeholder:left-6 pt-3 pb-16 text-left"
              style={{ paddingTop: '12px' }}
            />
            
            {/* Botões de modo de pesquisa à esquerda */}
            <div className="absolute bottom-2.5 left-6 flex flex-col gap-2 z-10">
              <div className="flex justify-start space-x-2">
                <button 
                  type="button" 
                  onClick={() => handleModeChange('search')}
                  className={`btn-mode flex items-center px-3 py-1 rounded-full text-xs transition-all duration-300 ${mode === 'search' ? 'bg-gradient-to-r from-blue-600 to-blue-500 shadow-lg shadow-blue-500/20 active' : 'bg-black/40 backdrop-blur-lg border border-blue-500/30 hover:bg-blue-500/10'}`}
                >
                  <svg className="w-3.5 h-3.5 mr-1" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
                  </svg>
                  Busca
                </button>
                
                <button 
                  type="button" 
                  onClick={() => handleModeChange('research')}
                  className={`btn-mode flex items-center px-3 py-1 rounded-full text-xs transition-all duration-300 ${mode === 'research' ? 'bg-gradient-to-r from-purple-600 to-purple-500 shadow-lg shadow-purple-500/20 active' : 'bg-black/40 backdrop-blur-lg border border-blue-500/30 hover:bg-blue-500/10'}`}
                >
                  <svg className="w-3.5 h-3.5 mr-1" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h4l3 3 3-3h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 16h-4.83l-.59.59L12 20.17l-1.59-1.59-.58-.58H5V4h14v14z" />
                    <path d="M12 11c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm2.78 1.58A6.95 6.95 0 0012 12c-1.93 0-3.47.73-4.78 1.58C6.43 14.12 6 15.18 6 16.25V17h12v-.75c0-1.07-.43-2.13-1.22-2.67z" />
                  </svg>
                  DeepResearcher
                </button>
              </div>
            </div>
            
            {/* Botões à direita */}
            <div className="absolute bottom-2.5 right-6 flex items-center z-10">
              <ModelsDropdown 
                selectedModel={model} 
                onModelChange={(newModel) => setModel(newModel)} 
              />
              
              {/* Botão de configurações */}
              <button 
                type="button" 
                onClick={toggleConfigModal}
                className="text-blue-400 hover:text-blue-300 mx-1.5 transition-all duration-300"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              
              {/* Botão de pesquisa */}
              <button type="submit" className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-400 hover:to-blue-500 rounded-full p-1.5 text-white shadow-lg shadow-blue-500/20 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </form>
        </div>
        
        {/* Informações contextuais */}
        <div className="w-full max-w-2xl space-y-2 mt-2">
          {/* Banner do App */}
          <AppBanner />
          
          {/* Widget do tempo e notícias */}
          <div className="flex flex-col md:flex-row gap-2">
            <WeatherWidget temp={weather.temp} condition={weather.condition} location={weather.location} />
            
            {/* Cards de notícias */}
            <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-2">
              {news.map(item => (
                <NewsCard key={item.id} title={item.title} image={item.image} />
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Rodapé */}
      <footer className="mt-auto py-4 border-t border-blue-500/20 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between text-blue-300/80 text-sm">
          <div className="text-center mb-2 md:mb-0">
            <a href="#" className="hover:text-blue-300 mx-3 transition-all duration-300">Pro</a>
            <a href="#" className="hover:text-blue-300 mx-3 transition-all duration-300">Enterprise</a>
            <a href="#" className="hover:text-blue-300 mx-3 transition-all duration-300">API</a>
            <a href="#" className="hover:text-blue-300 mx-3 transition-all duration-300">Blog</a>
            <a href="#" className="hover:text-blue-300 mx-3 transition-all duration-300">Careers</a>
            <a href="#" className="hover:text-blue-300 mx-3 transition-all duration-300">Store</a>
            <a href="#" className="hover:text-blue-300 mx-3 transition-all duration-300">Finance</a>
          </div>
          
          <div className="flex items-center">
            <span className="mr-2">English</span>
            <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            
            {/* Botão de ajuda */}
            <button className="ml-4 w-8 h-8 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center hover:bg-blue-500/20 transition-all duration-300">
              <span className="text-blue-300">?</span>
            </button>
          </div>
        </div>
      </footer>
      
      {/* Modal de Configurações */}
      {showConfigModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="relative bg-gray-800 rounded-xl border border-blue-500/30 w-full max-w-md p-6 shadow-lg shadow-blue-500/10 transform transition-all">
            <div className="flex justify-between items-center mb-4 pb-2 border-b border-blue-500/20">
              <h3 className="text-xl font-medium text-blue-400">Configurações Avançadas</h3>
              <button 
                onClick={toggleConfigModal}
                className="text-gray-400 hover:text-white transition-colors duration-300"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Configurações do Navegador */}
              <div className="space-y-3">
                <h4 className="text-lg text-blue-300 font-medium">Navegador</h4>
                
                <div 
                  onClick={() => setHeadless(!headless)} 
                  className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all duration-300 ${
                    !headless ? 'bg-green-500/20 border border-green-500/30' : 'bg-gray-700/50 border border-gray-600/30 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center">
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center mr-3 ${
                      !headless ? 'bg-green-500 text-white' : 'bg-gray-600 text-gray-300'
                    }`}>
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium">Navegador Visível</div>
                      <div className="text-sm text-gray-400">
                        {!headless ? 'Ativado' : 'Desativado'} - {!headless ? 'Você verá o navegador durante a pesquisa' : 'Navegador em segundo plano'}
                      </div>
                    </div>
                  </div>
                  
                  <div className={`relative w-10 h-6 transition-colors duration-300 rounded-full ${!headless ? 'bg-green-500' : 'bg-gray-600'}`}>
                    <div className={`absolute w-4 h-4 transition-transform duration-300 transform bg-white rounded-full top-1 ${!headless ? 'translate-x-5' : 'translate-x-1'}`}></div>
                  </div>
                </div>
              </div>
              
              {/* Configurações de Pesquisa */}
              <div className="space-y-3">
                <h4 className="text-lg text-blue-300 font-medium">Pesquisa</h4>
                
                <div 
                  onClick={() => setUsePlanner(!usePlanner)} 
                  className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all duration-300 ${
                    usePlanner ? 'bg-green-500/20 border border-green-500/30' : 'bg-gray-700/50 border border-gray-600/30 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center">
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center mr-3 ${
                      usePlanner ? 'bg-green-500 text-white' : 'bg-gray-600 text-gray-300'
                    }`}>
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium">Planejador de Pesquisa</div>
                      <div className="text-sm text-gray-400">
                        {usePlanner ? 'Ativado' : 'Desativado'} - {usePlanner ? 'Pesquisa mais organizada e eficiente' : 'Pesquisa direta'}
                      </div>
                    </div>
                  </div>
                  
                  <div className={`relative w-10 h-6 transition-colors duration-300 rounded-full ${usePlanner ? 'bg-green-500' : 'bg-gray-600'}`}>
                    <div className={`absolute w-4 h-4 transition-transform duration-300 transform bg-white rounded-full top-1 ${usePlanner ? 'translate-x-5' : 'translate-x-1'}`}></div>
                  </div>
                </div>
              </div>
              
              {/* Botão para limpar histórico */}
              <div className="pt-4 border-t border-blue-500/20">
                <button 
                  onClick={clearHistory}
                  className="w-full py-2.5 px-4 rounded-lg bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30 transition-all duration-300 flex items-center justify-center"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Limpar Todo o Histórico
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App 