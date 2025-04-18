import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

interface ResearchResultsProps {
  researchId: string | null;
}

interface Research {
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

const ResearchResults: React.FC<ResearchResultsProps> = ({ researchId }) => {
  const [research, setResearch] = useState<Research | null>(null);
  const [report, setReport] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // Função para formatar a data
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  };

  // Função para buscar o status da pesquisa
  const fetchResearchStatus = async () => {
    if (!researchId) return;

    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5000/api/research/${researchId}`);
      setResearch(response.data);

      // Se a pesquisa estiver concluída e for do tipo Deep Researcher, buscar o relatório
      if (response.data.status === 'completed' && response.data.use_deep_researcher) {
        try {
          const reportResponse = await axios.get(`http://localhost:5000/api/research/${researchId}/report`);
          setReport(reportResponse.data.report);
        } catch (reportError) {
          console.error('Erro ao buscar relatório:', reportError);
        }
      }

      // Se a pesquisa estiver concluída ou com erro, parar de polling
      if (response.data.status === 'completed' || response.data.status === 'error') {
        if (pollingInterval) {
          clearInterval(pollingInterval);
          setPollingInterval(null);
        }
      }

      setError(null);
    } catch (error) {
      console.error('Erro ao buscar status da pesquisa:', error);
      setError('Não foi possível buscar o status da pesquisa.');
    } finally {
      setLoading(false);
    }
  };

  // Configurar polling para atualizar o status da pesquisa
  useEffect(() => {
    if (researchId) {
      // Buscar o status inicial
      fetchResearchStatus();

      // Configurar polling a cada 5 segundos
      const interval = setInterval(fetchResearchStatus, 5000);
      setPollingInterval(interval);

      // Limpar o intervalo quando o componente for desmontado ou o ID da pesquisa mudar
      return () => {
        clearInterval(interval);
        setPollingInterval(null);
      };
    }
  }, [researchId]);

  // Se não houver ID de pesquisa ou pesquisa, exibir mensagem
  if (!researchId || !research) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
        <p className="text-gray-400">
          {loading ? 'Carregando...' : 'Nenhuma pesquisa selecionada. Inicie uma nova pesquisa para ver os resultados.'}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-orange-500 mb-4">Resultados da Pesquisa</h2>

      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-100 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-200 mb-2">Detalhes</h3>
        <div className="bg-gray-700 rounded p-4">
          <p className="text-gray-300 mb-2">
            <span className="font-semibold">ID:</span> {research.id}
          </p>
          <p className="text-gray-300 mb-2">
            <span className="font-semibold">Tarefa:</span> {research.task}
          </p>
          <p className="text-gray-300 mb-2">
            <span className="font-semibold">Modelo:</span> {research.provider} / {research.model}
          </p>
          <p className="text-gray-300 mb-2">
            <span className="font-semibold">Tipo:</span>{' '}
            {research.use_deep_researcher ? 'Deep Researcher' : 'Pesquisa Simples'}
          </p>
          <p className="text-gray-300 mb-2">
            <span className="font-semibold">Iniciado em:</span> {formatDate(research.start_time)}
          </p>
          {research.end_time && (
            <p className="text-gray-300 mb-2">
              <span className="font-semibold">Concluído em:</span> {formatDate(research.end_time)}
            </p>
          )}
          <p className="text-gray-300 mb-2">
            <span className="font-semibold">Status:</span>{' '}
            <span
              className={`font-semibold ${
                research.status === 'completed'
                  ? 'text-green-500'
                  : research.status === 'error'
                  ? 'text-red-500'
                  : 'text-yellow-500'
              }`}
            >
              {research.status === 'completed'
                ? 'Concluído'
                : research.status === 'error'
                ? 'Erro'
                : 'Em andamento'}
            </span>
          </p>
          {research.error && (
            <p className="text-red-400 mt-2">
              <span className="font-semibold">Erro:</span> {research.error}
            </p>
          )}
        </div>
      </div>

      {research.status === 'running' && (
        <div className="flex justify-center my-8">
          <div className="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12 mb-4 border-t-orange-500 animate-spin"></div>
        </div>
      )}

      {research.status === 'completed' && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-200 mb-2">Resultado</h3>
          <div className="bg-gray-700 rounded p-4 overflow-auto max-h-[60vh]">
            {research.use_deep_researcher ? (
              report ? (
                <ReactMarkdown className="markdown prose prose-invert max-w-none">
                  {report}
                </ReactMarkdown>
              ) : (
                <p className="text-gray-400">Carregando relatório...</p>
              )
            ) : (
              <ReactMarkdown className="markdown prose prose-invert max-w-none">
                {research.results || 'Nenhum resultado disponível.'}
              </ReactMarkdown>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchResults; 