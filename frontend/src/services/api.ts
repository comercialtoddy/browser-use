import axios from 'axios';

// Criar uma instância de axios com configurações padrão
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interface para representar um provedor
export interface Provider {
  name: string;
  models: { id: string; name: string }[];
  requires_key: boolean;
  key_env: string;
}

// Interface para representar uma pesquisa
export interface Research {
  id: string;
  provider: string;
  model: string;
  task: string;
  status: string;
  start_time: string;
  end_time?: string;
  results?: string;
  error?: string;
  use_deep_researcher: boolean;
}

// Serviços relacionados ao clima
export const weatherService = {
  getWeather: async () => {
    const response = await api.get('/weather');
    return response.data;
  },
};

// Serviços relacionados às notícias
export const newsService = {
  getNews: async (limit = 4) => {
    const response = await api.get(`/news?limit=${limit}`);
    return response.data;
  },
};

// Função para determinar o provedor com base no modelo
function determineProviderFromModel(model: string): string {
  if (model.startsWith('gpt-') || model.includes('openai')) {
    return 'openai';
  } else if (model.startsWith('claude-') || model.includes('anthropic')) {
    return 'anthropic';
  } else if (model.includes('gemini') || model.includes('google')) {
    return 'google';
  } else if (model.includes('deepseek')) {
    return 'deepseek';
  } else if (model.includes('grok') || model.includes('xai')) {
    return 'xai';
  } else {
    // Padrão para google, já que temos uma chave de API configurada
    return 'google';
  }
}

// Serviços relacionados à pesquisa
export const searchService = {
  search: async (query: string, model: string, mode: 'search' | 'research', headless: boolean = true) => {
    const response = await api.post('/search', { query, model, mode, headless });
    return response.data;
  },
  
  // Métodos para deep research
  startDeepResearch: async (query: string, model: string, usePlanner: boolean = true, headless: boolean = true) => {
    try {
      const provider = determineProviderFromModel(model);
      console.log(`Iniciando pesquisa profunda com provedor: ${provider}, modelo: ${model}, planejador: ${usePlanner ? 'ativado' : 'desativado'}`);
      
      const response = await api.post('/research/start', { 
        query: query,
        model: model,
        provider: provider,
        deep: true,
        vision: true,
        planner: usePlanner,
        max_steps: 15,
        max_search_iterations: 3,
        max_query_num: 3,
        headless
      });
      
      return response.data;
    } catch (error) {
      console.error('Erro ao iniciar pesquisa profunda:', error);
      throw error;
    }
  },
  
  getResearchStatus: async (researchId: string) => {
    const response = await api.get(`/research/${researchId}`);
    return response.data;
  },
  
  getResearchReport: async (researchId: string) => {
    const response = await api.get(`/research/${researchId}/report`);
    return response.data;
  }
};

// Serviços relacionados aos provedores/modelos
export const providerService = {
  getProviders: async () => {
    try {
      const response = await api.get('/providers', { timeout: 5000 });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar provedores:', error);
      return {}; // Retorna um objeto vazio em caso de erro
    }
  },
};

// Serviços relacionados à pesquisa profunda
export const researchService = {
  startResearch: async (data: {
    provider: string;
    model: string;
    api_key: string;
    task: string;
    use_deep_researcher?: boolean;
    use_vision?: boolean;
    max_steps?: number;
    max_search_iterations?: number;
    max_query_num?: number;
    headless?: boolean;
  }) => {
    const response = await api.post('/research/start', data);
    return response.data;
  },
  
  getResearchStatus: async (researchId: string) => {
    const response = await api.get(`/research/${researchId}`);
    return response.data;
  },
  
  stopResearch: async (researchId: string) => {
    const response = await api.post(`/research/${researchId}/stop`);
    return response.data;
  },
  
  getResearchReport: async (researchId: string) => {
    const response = await api.get(`/research/${researchId}/report`);
    return response.data;
  },
};

// Serviço para lidar com pensamentos
export const ThoughtsService = {
  // Adicionar um novo pensamento
  postThought: async (thought: string): Promise<any> => {
    const response = await api.post('/thoughts', { thought });
    return response.data;
  },
};

export default api; 