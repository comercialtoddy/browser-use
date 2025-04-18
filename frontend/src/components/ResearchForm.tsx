import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Provider {
  name: string;
  models: { id: string; name: string }[];
  requires_key: boolean;
  key_env: string;
}

interface Providers {
  [key: string]: Provider;
}

interface ResearchFormProps {
  onResearchStarted: (researchId: string) => void;
}

const ResearchForm: React.FC<ResearchFormProps> = ({ onResearchStarted }) => {
  const [providers, setProviders] = useState<Providers>({});
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [apiKey, setApiKey] = useState<string>('');
  const [task, setTask] = useState<string>('');
  const [useDeepResearcher, setUseDeepResearcher] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Carregar provedores disponíveis
    const fetchProviders = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/providers');
        setProviders(response.data);
        
        // Selecionar o primeiro provedor e modelo por padrão
        const firstProvider = Object.keys(response.data)[0];
        if (firstProvider) {
          setSelectedProvider(firstProvider);
          
          const firstModel = response.data[firstProvider].models[0]?.id;
          if (firstModel) {
            setSelectedModel(firstModel);
          }
        }
      } catch (error) {
        console.error('Erro ao carregar provedores:', error);
        setError('Não foi possível carregar os provedores disponíveis. Verifique se o backend está em execução.');
      }
    };

    fetchProviders();
  }, []);

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provider = e.target.value;
    setSelectedProvider(provider);
    
    // Selecionar o primeiro modelo deste provedor
    if (providers[provider]?.models.length > 0) {
      setSelectedModel(providers[provider].models[0].id);
    } else {
      setSelectedModel('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedProvider || !selectedModel || !apiKey || !task) {
      setError('Por favor, preencha todos os campos obrigatórios.');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://localhost:5000/api/research/start', {
        provider: selectedProvider,
        model: selectedModel,
        api_key: apiKey,
        task,
        use_deep_researcher: useDeepResearcher
      });
      
      if (response.data.research_id) {
        onResearchStarted(response.data.research_id);
      }
    } catch (error: any) {
      console.error('Erro ao iniciar pesquisa:', error);
      setError(error.response?.data?.message || 'Erro ao iniciar a pesquisa. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-orange-500 mb-6">Nova Pesquisa</h2>
      
      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-100 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-300 mb-2">Provedor</label>
          <select
            className="w-full bg-gray-700 border border-gray-600 rounded py-2 px-3 text-gray-100"
            value={selectedProvider}
            onChange={handleProviderChange}
            disabled={isLoading}
          >
            {Object.entries(providers).map(([id, provider]) => (
              <option key={id} value={id}>
                {provider.name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-300 mb-2">Modelo</label>
          <select
            className="w-full bg-gray-700 border border-gray-600 rounded py-2 px-3 text-gray-100"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={isLoading || !selectedProvider}
          >
            {selectedProvider &&
              providers[selectedProvider]?.models.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name}
                </option>
              ))}
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-300 mb-2">API Key</label>
          <input
            type="password"
            className="w-full bg-gray-700 border border-gray-600 rounded py-2 px-3 text-gray-100"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Insira sua chave API"
            disabled={isLoading}
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-300 mb-2">Tarefa de Pesquisa</label>
          <textarea
            className="w-full bg-gray-700 border border-gray-600 rounded py-2 px-3 text-gray-100 h-32"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Descreva o que você deseja pesquisar..."
            disabled={isLoading}
          />
        </div>
        
        <div className="mb-6">
          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              className="mr-2 h-5 w-5 text-orange-500 rounded focus:ring-orange-500"
              checked={useDeepResearcher}
              onChange={(e) => setUseDeepResearcher(e.target.checked)}
              disabled={isLoading}
            />
            Usar Deep Researcher (pesquisa mais completa)
          </label>
        </div>
        
        <button
          type="submit"
          className={`w-full py-2 px-4 rounded font-bold ${
            isLoading
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-orange-600 hover:bg-orange-700 text-white'
          }`}
          disabled={isLoading}
        >
          {isLoading ? 'Iniciando pesquisa...' : 'Iniciar Pesquisa'}
        </button>
      </form>
    </div>
  );
};

export default ResearchForm; 