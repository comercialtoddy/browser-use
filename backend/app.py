from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import asyncio
import threading
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.views import BrowserState, TabInfo
from uuid import uuid4
from datetime import datetime
from browser_use import Agent, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from deep_researcher import EnhancedDeepResearcher, AgentState
import time
import atexit

app = Flask(__name__)
# Configuração simplificada do CORS
CORS(app)

# Adicionar cabeçalhos CORS manualmente para garantir que funcionem
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do loop de eventos assíncrono global
# Variável global para armazenar o loop de eventos
app_loop = None
loop_thread = None

def start_background_loop():
    """Inicia um loop de eventos assíncrono em background"""
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    global app_loop
    app_loop = loop
    logger.info("Loop de eventos assíncrono iniciado")
    loop.run_forever()

# Iniciar o loop de eventos em uma thread separada
def initialize_async_loop():
    global loop_thread, app_loop
    if loop_thread is None or not loop_thread.is_alive():
        loop_thread = threading.Thread(target=start_background_loop, daemon=True)
        loop_thread.start()
        # Pequena pausa para garantir que o loop esteja pronto
        time.sleep(0.5)
        logger.info("Loop de eventos assíncrono iniciado em thread separada")

# Inicializar o loop de eventos    
initialize_async_loop()

# Função para executar código assíncrono no Flask
def run_async(func):
    def wrapper(*args, **kwargs):
        global app_loop
        if app_loop is None or app_loop.is_closed():
            logger.warning("Loop de eventos não disponível na função run_async, recriando...")
            initialize_async_loop()
            time.sleep(0.5)  # Pequena pausa para o loop iniciar
            
        # Criar um objeto Future para obter o resultado da coroutine
        future = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), app_loop)
        # Esperar pelo resultado com timeout
        return future.result(timeout=60)  # Timeout de 60 segundos
    return wrapper

# Lista de provedores e modelos suportados
PROVIDERS = {
    "google": {
        "name": "Google",
        "models": [
            {"id": "gemini-2.5-pro-preview", "name": "Gemini 2.5 Pro Preview"},
            {"id": "gemini-2.5-flash-preview-04-17", "name": "Gemini 2.5 Flash"},
        ],
        "requires_key": True,
        "key_env": "GEMINI_API_KEY"
    },
    "openai": {
        "name": "OpenAI",
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-no-vision", "name": "GPT-4o (sem visão)"},
            {"id": "gpt-4o-viewport-0", "name": "GPT-4o (viewport 0)"},
            {"id": "gpt-4o-no-boundingbox", "name": "GPT-4o (sem boundingbox)"},
            {"id": "gpt-4.1", "name": "GPT-4.1"},
        ],
        "requires_key": True,
        "key_env": "OPENAI_API_KEY"
    },
    "anthropic": {
        "name": "Anthropic",
        "models": [
            {"id": "claude-3.7-sonnet", "name": "Claude 3.7 Sonnet"},
            {"id": "claude-3.6", "name": "Claude 3.6"},
            {"id": "claude-3.5", "name": "Claude 3.5"}
        ],
        "requires_key": True,
        "key_env": "ANTHROPIC_API_KEY"
    },
    "deepseek": {
        "name": "DeepSeek",
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek Chat"},
            {"id": "deepseek-r1", "name": "DeepSeek R1"}
        ],
        "requires_key": True,
        "key_env": "DEEPSEEK_API_KEY"
    },
    "xai": {
        "name": "xAI",
        "models": [
            {"id": "grok-2-1212", "name": "Grok 2"}
        ],
        "requires_key": True,
        "key_env": "GROK_API_KEY"
    }
}

# Armazenamento de pesquisas em andamento
ACTIVE_RESEARCHES = {}
# Armazenamento de estados de agentes para controle de parada
AGENT_STATES = {}

# Dados simulados para meteorologia e notícias
SAMPLE_WEATHER = {
    "temp": "18°C",
    "condition": "Clear",
    "location": "Estalo",
    "high": "26°C",
    "low": "15°C"
}

SAMPLE_NEWS = [
    {
        "id": 1,
        "title": "Trump blocks Musk from Pentagon briefing",
        "image": "https://via.placeholder.com/50",
        "url": "https://example.com/news/1"
    },
    {
        "id": 2,
        "title": "Elon Musk seeks more children via social media",
        "image": "https://via.placeholder.com/50",
        "url": "https://example.com/news/2"
    },
    {
        "id": 3,
        "title": "AI agents becoming more proficient at web automation",
        "image": "https://via.placeholder.com/50",
        "url": "https://example.com/news/3"
    },
    {
        "id": 4,
        "title": "New research shows improvements in LLM reasoning capabilities",
        "image": "https://via.placeholder.com/50",
        "url": "https://example.com/news/4"
    }
]

@app.route('/api/browser-info', methods=['GET'])
@run_async
async def get_browser_info():
    """Obtém informações básicas do navegador"""
    try:
        # Inicializa o navegador com configurações padrão
        browser_config = BrowserConfig(headless=True)
        browser = Browser(config=browser_config)
        
        # Cria um contexto de navegador
        context = await browser.new_context()
        
        # Cria uma nova aba e navega para uma URL
        await context.create_new_tab()
        session = await context.get_session()
        page = await context._get_current_page(session)
        await page.goto('https://example.com')
        
        # Obtém informações da página
        title = await page.title()
        url = page.url
        
        # Obtém informações das abas
        tabs = [
            TabInfo(
                page_id=1,
                url=url,
                title=title
            ).model_dump()
        ]
        
        # Fecha o navegador
        await browser.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "title": title,
                "url": url,
                "tabs": tabs
            }
        })
    except Exception as e:
        logger.error(f"Erro ao obter informações do navegador: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/browser-stats', methods=['GET'])
def get_stats():
    """Obtém estatísticas de uso do navegador"""
    try:
        # Aqui você implementaria a lógica para obter estatísticas reais
        # Este é apenas um exemplo
        stats = {
            "total_pages_visited": 125,
            "most_visited_domains": [
                {"domain": "google.com", "count": 45},
                {"domain": "github.com", "count": 32},
                {"domain": "stackoverflow.com", "count": 28}
            ],
            "average_time_per_page": "2m 15s",
            "browser_usage_time": "5h 30m"
        }
        
        return jsonify({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/navigation-history', methods=['GET'])
def get_navigation_history():
    """Obtém o histórico de navegação"""
    try:
        # Exemplo de histórico de navegação
        history = [
            {"url": "https://example.com", "title": "Example Domain", "timestamp": "2023-05-15T10:30:00Z"},
            {"url": "https://google.com", "title": "Google", "timestamp": "2023-05-15T10:35:00Z"},
            {"url": "https://github.com", "title": "GitHub", "timestamp": "2023-05-15T11:15:00Z"}
        ]
        
        return jsonify({
            "status": "success",
            "data": history
        })
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Retorna a lista de provedores e modelos disponíveis"""
    return jsonify(PROVIDERS)

@app.route('/api/thoughts', methods=['POST'])
def add_thought():
    """Adiciona um novo pensamento"""
    data = request.json
    if not data or 'thought' not in data:
        return jsonify({
            "status": "error",
            "message": "O campo 'thought' é obrigatório"
        }), 400
        
    thought = data['thought']
    
    # Aqui você salvaria o pensamento em um banco de dados
    # Este é apenas um exemplo de resposta
    return jsonify({
        "status": "success",
        "message": "Pensamento adicionado",
        "data": {"thought": thought}
    })

@app.route('/api/research/start', methods=['POST'])
def start_research():
    """Inicia uma nova pesquisa"""
    logger.info("--- Nova requisição recebida em /api/research/start ---") # Log de início
    try:
        data = request.json
        logger.info(f"Dados recebidos no corpo da requisição: {data}") # Log dos dados recebidos

        if not data:
            logger.error("Dados da requisição vazios ou inválidos")
            return jsonify({
                "status": "error",
                "message": "Requisição inválida - dados ausentes"
            }), 400

        query = data.get('query')
        model = data.get('model', 'gemini-2.5-pro-preview')
        provider = data.get('provider', 'google')

        logger.info(f"Extraídos: query='{query}', model={model}, provider={provider}") # Log dos valores extraídos

        api_key = None
        if provider == 'google':
            api_key = os.getenv("GEMINI_API_KEY")
            logger.info(f"Provedor Google detectado, buscando GEMINI_API_KEY. Valor obtido: {'***' if api_key else 'Nenhum'}") # Log da chave (sem expor o valor)
        else:
            api_key_env_var = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(api_key_env_var)
            logger.info(f"Buscando chave API na variável de ambiente: {api_key_env_var}. Valor obtido: {'***' if api_key else 'Nenhum'}") # Log da chave

        use_deep = data.get('deep', True)
        use_vision = data.get('vision', False)
        use_planner = data.get('planner', True)
        headless = data.get('headless', True)
        max_steps = data.get('max_steps', 10)
        max_query_num = data.get('max_query_num', 3)
        max_search_iterations = data.get('max_search_iterations', 5)

        logger.info(f"Parâmetros da pesquisa: deep={use_deep}, vision={use_vision}, planner={use_planner}, etc.")

        # Verificar se a chave API foi passada no corpo da requisição (opcional, para override)
        if not api_key and 'api_key' in data:
            api_key = data.get('api_key')
            logger.info(f"Chave API fornecida no corpo da requisição será usada. Valor obtido: {'***' if api_key else 'Nenhum'}")

        # --- VALIDAÇÕES ---
        if not query:
            logger.error("Validação falhou: Campo 'query' está vazio.")
            return jsonify({
                "status": "error",
                "message": "O campo 'query' é obrigatório"
            }), 400

        if not api_key:
            error_message = f"Validação falhou: Chave API não encontrada para o provedor {provider}. Verifique a variável de ambiente correspondente (ex: GEMINI_API_KEY para Google)."
            logger.error(error_message)
            return jsonify({
                "status": "error",
                "message": error_message
            }), 400
        # --- FIM VALIDAÇÕES ---

        logger.info("Validações de query e API key passaram.")

        # Gerar ID único para a pesquisa
        research_id = str(uuid4())
        logger.info(f"Gerado research_id: {research_id}")

        # Criar um estado do agente para controle
        agent_state = AgentState()
        AGENT_STATES[research_id] = agent_state
        logger.info(f"Estado do agente criado para {research_id}")

        # Registrar a pesquisa
        ACTIVE_RESEARCHES[research_id] = {
            "id": research_id,
            "query": query,
            "model": model,
            "provider": provider,
            "status": "running",
            "deep": use_deep,
            "vision": use_vision,
            "planner": use_planner,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "results": None,
            "error": None
        }
        logger.info(f"Pesquisa {research_id} registrada em ACTIVE_RESEARCHES")

        # Iniciar a pesquisa em background
        kwargs = {
            "research_id": research_id,
            "provider": provider,
            "model": model,
            "api_key": api_key, # Passando a chave obtida
            "task": query,
            "use_deep": use_deep,
            "use_vision": use_vision,
            "use_planner": use_planner,
            "headless": headless,
            "max_steps": max_steps,
            "max_query_num": max_query_num,
            "max_search_iterations": max_search_iterations
        }
        logger.info(f"Preparando para iniciar run_research em background com kwargs: { {k: v for k, v in kwargs.items() if k != 'api_key'} }") # Log sem a chave

        # Iniciar a pesquisa em background de forma segura
        try:
            asyncio.run_coroutine_threadsafe(run_research(**kwargs), app_loop)
            logger.info(f"Pesquisa {research_id} agendada com sucesso em background")
        except Exception as e:
            logger.error(f"Erro ao agendar pesquisa em background: {e}")
            ACTIVE_RESEARCHES[research_id]["status"] = "error"
            ACTIVE_RESEARCHES[research_id]["error"] = str(e)
            return jsonify({
                "status": "error",
                "message": f"Erro ao iniciar pesquisa em background: {str(e)}"
            }), 500

        logger.info(f"Retornando sucesso para a requisição {research_id}")
        return jsonify({
            "status": "success",
            "message": "Pesquisa iniciada com sucesso",
            "research_id": research_id
        })
    except Exception as e:
        logger.error(f"Erro geral ao processar requisição /api/research/start: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Erro interno ao processar requisição: {str(e)}"
        }), 500

@app.route('/api/research/<research_id>', methods=['GET'])
def get_research_status(research_id):
    """Obtém o status de uma pesquisa"""
    if research_id not in ACTIVE_RESEARCHES:
        return jsonify({"status": "error", "message": "Pesquisa não encontrada"}), 404
    
    return jsonify(ACTIVE_RESEARCHES[research_id])

@app.route('/api/research/<research_id>/stop', methods=['POST'])
def stop_research(research_id):
    """Para uma pesquisa em andamento"""
    if research_id not in ACTIVE_RESEARCHES:
        return jsonify({"status": "error", "message": "Pesquisa não encontrada"}), 404
    
    if research_id in AGENT_STATES:
        # Solicitar parada do agente
        AGENT_STATES[research_id].request_stop()
        
        # Atualizar status
        ACTIVE_RESEARCHES[research_id]["status"] = "stopping"
        
        return jsonify({
            "status": "success",
            "message": "Solicitação de parada enviada. A pesquisa será interrompida em breve."
        })
    
    return jsonify({
        "status": "error",
        "message": "Não foi possível parar a pesquisa. Estado do agente não encontrado."
    }), 400

@app.route('/api/research', methods=['GET'])
def get_all_researches():
    """Obtém a lista de todas as pesquisas"""
    return jsonify(list(ACTIVE_RESEARCHES.values()))

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Obtém informações meteorológicas atuais"""
    # Em uma implementação real, você iria buscar dados de uma API de clima
    # Aqui estamos apenas retornando dados simulados
    return jsonify({
        "status": "success",
        "data": SAMPLE_WEATHER
    })

@app.route('/api/news', methods=['GET'])
def get_news():
    """Obtém as principais notícias"""
    # Em uma implementação real, você iria buscar notícias de uma API de notícias
    # Aqui estamos apenas retornando dados simulados
    limit = request.args.get('limit', default=4, type=int)
    news = SAMPLE_NEWS[:limit]
    
    return jsonify({
        "status": "success",
        "data": news
    })

@app.route('/api/search', methods=['POST'])
def perform_search():
    """Realiza uma pesquisa simples"""
    data = request.json
    query = data.get('query')
    model = data.get('model')
    mode = data.get('mode', 'search')  # 'search' ou 'research'
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "O campo 'query' é obrigatório"
        }), 400
    
    # Em uma implementação real, você enviaria a consulta para o LLM
    # e retornaria os resultados
    
    # Para demonstração, retornamos uma resposta simulada
    time.sleep(1)  # Simular processamento
    
    return jsonify({
        "status": "success",
        "query": query,
        "mode": mode,
        "model": model,
        "results": f"Resultados da pesquisa para: {query}"
    })

@app.route('/api/research/<research_id>/report', methods=['GET'])
def get_research_report(research_id):
    """Obtém o relatório de uma pesquisa"""
    if research_id not in ACTIVE_RESEARCHES:
        return jsonify({"status": "error", "message": "Pesquisa não encontrada"}), 404
    
    research = ACTIVE_RESEARCHES[research_id]
    
    if research['status'] != 'completed':
        return jsonify({"status": "error", "message": "Pesquisa ainda não concluída"}), 400
    
    # Verificar se existe um arquivo de relatório
    save_dir = os.path.join(f"./tmp/deep_research/{research_id}")
    report_path = os.path.join(save_dir, "final_report.md")
    
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        return jsonify({
            "status": "success",
            "report": report_content
        })
    
    return jsonify({
        "status": "success",
        "report": research['results']
    })

@app.route('/api/cors-test', methods=['GET'])
def test_cors():
    """Endpoint para testar se o CORS está funcionando corretamente"""
    return jsonify({
        "status": "success",
        "message": "CORS configurado corretamente!",
        "time": datetime.now().isoformat()
    })

async def run_research(research_id, provider, model, api_key, task, **kwargs):
    """Executa a pesquisa em background"""
    try:
        # Registrar os parâmetros recebidos para diagnóstico (exceto a chave API)
        logger.info(f"Iniciando pesquisa {research_id} com parâmetros: provider={provider}, model={model}, task='{task}', kwargs={kwargs}")
        
        # Verificar se a chave API está presente
        if not api_key:
            error_msg = f"Chave API não fornecida para o provedor {provider}"
            logger.error(error_msg)
            if research_id in ACTIVE_RESEARCHES:
                ACTIVE_RESEARCHES[research_id]["status"] = "error"
                ACTIVE_RESEARCHES[research_id]["error"] = error_msg
            return
        
        # Pegar agente state
        agent_state = AGENT_STATES.get(research_id)
        if not agent_state:
            logger.warning(f"Estado do agente não encontrado para {research_id}, criando novo estado")
            agent_state = AgentState()
            AGENT_STATES[research_id] = agent_state
        
        # Configurar o LLM baseado no provedor
        try:
            if provider == "google":
                from langchain_google_genai import ChatGoogleGenerativeAI
                from pydantic import SecretStr
                llm = ChatGoogleGenerativeAI(model=model, api_key=SecretStr(api_key))
                logger.info(f"LLM do Google inicializado com sucesso: {model}")
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model=model, api_key=api_key)
                logger.info(f"LLM da OpenAI inicializado com sucesso: {model}")
            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                llm = ChatAnthropic(model_name=model, api_key=api_key)
                logger.info(f"LLM da Anthropic inicializado com sucesso: {model}")
            elif provider == "deepseek":
                from langchain_openai import ChatOpenAI
                from pydantic import SecretStr
                llm = ChatOpenAI(
                    base_url='https://api.deepseek.com/v1',
                    model=model,
                    api_key=SecretStr(api_key)
                )
                logger.info(f"LLM da DeepSeek inicializado com sucesso: {model}")
            elif provider == "xai":
                from langchain_openai import ChatOpenAI
                from pydantic import SecretStr
                llm = ChatOpenAI(
                    base_url='https://api.x.ai/v1',
                    model=model,
                    api_key=SecretStr(api_key)
                )
                logger.info(f"LLM da xAI inicializado com sucesso: {model}")
            else:
                raise ValueError(f"Provedor {provider} não implementado")
        except Exception as llm_error:
            error_msg = f"Erro ao inicializar o LLM: {str(llm_error)}"
            logger.error(error_msg)
            if research_id in ACTIVE_RESEARCHES:
                ACTIVE_RESEARCHES[research_id]["status"] = "error"
                ACTIVE_RESEARCHES[research_id]["error"] = error_msg
            return
        
        # Configurar diretório de resultados
        save_dir = os.path.join(f"./tmp/deep_research/{research_id}")
        try:
            os.makedirs(save_dir, exist_ok=True)
            logger.info(f"Diretório criado: {save_dir}")
        except Exception as dir_error:
            error_msg = f"Erro ao criar diretório: {str(dir_error)}"
            logger.error(error_msg)
            if research_id in ACTIVE_RESEARCHES:
                ACTIVE_RESEARCHES[research_id]["status"] = "error"
                ACTIVE_RESEARCHES[research_id]["error"] = error_msg
            return
        
        use_deep = kwargs.get("use_deep", False)
        
        # Verificar configurações específicas do modelo
        use_vision = kwargs.get("use_vision", False)
        
        # Verificar se o modelo é uma variante que não suporta visão
        if model in ["gpt-4o-no-vision", "deepseek-chat", "deepseek-r1", "grok-2-1212"]:
            use_vision = False
            logger.info(f"Visão desabilitada para o modelo {model}")
        
        # Configurações específicas para viewport
        browser_config = BrowserConfig(
            headless=kwargs.get("headless", True),
            disable_security=True
        )
        
        # Configurações especiais para viewport-0
        if model == "gpt-4o-viewport-0":
            browser_config = BrowserConfig(
                headless=kwargs.get("headless", True),
                disable_security=True,
                new_context_config=BrowserContextConfig(
                    viewport_expansion=0
                )
            )
            logger.info("Configuração especial de viewport-0 aplicada")
        
        if use_deep:
            # Usar o DeepResearcher completo
            logger.info(f"Iniciando pesquisa profunda para {research_id} usando {provider}/{model}")
            
            # Criar uma cópia de kwargs sem os parâmetros que serão passados explicitamente
            researcher_kwargs = kwargs.copy()
            
            # Remover todos os parâmetros que já são passados explicitamente
            params_to_remove = ['use_vision', 'max_steps', 'max_query_num', 
                              'max_search_iterations', 'headless']
            
            removed_params = []
            for param in params_to_remove:
                if param in researcher_kwargs:
                    del researcher_kwargs[param]
                    removed_params.append(param)
            
            if removed_params:
                logger.info(f"Parâmetros removidos para evitar duplicação: {', '.join(removed_params)}")
            
            try:
                researcher = EnhancedDeepResearcher(
                    llm=llm,
                    max_query_num=kwargs.get("max_query_num", 3),
                    max_search_iterations=kwargs.get("max_search_iterations", 5),
                    max_steps=kwargs.get("max_steps", 10),
                    headless=kwargs.get("headless", True),
                    use_vision=use_vision
                )
                logger.info("EnhancedDeepResearcher inicializado com sucesso")
                
                report_content, report_path = await researcher.search(
                    task=task, 
                    save_dir=save_dir,
                    agent_state=agent_state,
                    **researcher_kwargs  # Usar a versão sem parâmetros duplicados
                )
                logger.info(f"Pesquisa concluída. Relatório salvo em: {report_path}")
                
                # Atualizar status da pesquisa
                if research_id in ACTIVE_RESEARCHES:
                    if agent_state and agent_state.is_stop_requested():
                        ACTIVE_RESEARCHES[research_id]["status"] = "stopped"
                        ACTIVE_RESEARCHES[research_id]["message"] = "A pesquisa foi interrompida pelo usuário."
                    else:
                        ACTIVE_RESEARCHES[research_id]["status"] = "completed"
                    
                    ACTIVE_RESEARCHES[research_id]["end_time"] = datetime.now().isoformat()
                    ACTIVE_RESEARCHES[research_id]["results"] = "Relatório gerado com sucesso. Use a rota /api/research/{research_id}/report para visualizar."
                    ACTIVE_RESEARCHES[research_id]["report_path"] = report_path
                
                logger.info(f"Pesquisa profunda {research_id} concluída com sucesso ou interrompida")
            except Exception as research_error:
                error_msg = f"Erro durante a execução da pesquisa: {str(research_error)}"
                logger.error(error_msg)
                if research_id in ACTIVE_RESEARCHES:
                    ACTIVE_RESEARCHES[research_id]["status"] = "error"
                    ACTIVE_RESEARCHES[research_id]["error"] = error_msg
        else:
            # Usar o agente padrão
            logger.info(f"Iniciando pesquisa simples para {research_id} usando {provider}/{model}")
            browser = Browser(config=browser_config)
            
            agent = Agent(
                task=task,
                llm=llm,
                max_actions_per_step=kwargs.get("max_actions_per_step", 4),
                browser=browser,
                use_vision=use_vision
            )
            
            result = await agent.run(max_steps=kwargs.get("max_steps", 25))
            final_result = result.final_result()
            
            # Salvar o resultado em arquivo
            result_path = os.path.join(save_dir, "result.md")
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(final_result)
            
            # Atualizar status da pesquisa
            if research_id in ACTIVE_RESEARCHES:
                ACTIVE_RESEARCHES[research_id]["status"] = "completed"
                ACTIVE_RESEARCHES[research_id]["end_time"] = datetime.now().isoformat()
                ACTIVE_RESEARCHES[research_id]["results"] = final_result
            
            logger.info(f"Pesquisa simples {research_id} concluída com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao executar pesquisa {research_id}: {str(e)}")
        if research_id in ACTIVE_RESEARCHES:
            ACTIVE_RESEARCHES[research_id]["status"] = "error"
            ACTIVE_RESEARCHES[research_id]["error"] = str(e)
    finally:
        # Limpar o estado do agente
        if research_id in AGENT_STATES:
            del AGENT_STATES[research_id]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 