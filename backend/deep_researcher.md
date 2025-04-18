# Documentação: Deep Researcher

## Visão Geral

O arquivo `deep_researcher.py` implementa um sistema avançado de pesquisa na web, permitindo a execução de pesquisas profundas e automatizadas utilizando modelos de linguagem e automação de navegador. O sistema é capaz de extrair e processar conteúdos de páginas web, gerar relatórios estruturados, e navegar de forma autônoma pela internet para coletar informações relevantes sobre um tópico.

## Estrutura Principal

### Verificação de Versão
- **verify_browser_use_version()**: Função que verifica a versão do pacote browser-use.

### Extração de Conteúdo
- **MainContentExtractor**: Classe responsável por extrair o conteúdo principal de páginas HTML.
  - `extract(html, output_format)`: Método principal que processa o HTML e extrai o conteúdo relevante.
  - `_convert_to_markdown(element)`: Converte elementos HTML para formato markdown.

### Processamento de JSON
- **repair_json(json_str)**: Função utilitária que tenta reparar strings JSON malformadas.

### Navegador Personalizado
- **CustomBrowser**: Estende a classe `Browser` com funcionalidades específicas para o Deep Researcher.
  - `__init__(config)`: Inicializa o navegador com configurações específicas.
  - `new_context(config)`: Cria um novo contexto de navegador com scripts para remoção de popups/cookies.
  - `extract_page_content(context, url, use_jina)`: Extrai o conteúdo de uma página web em formato markdown.
  - `save_screenshot(context, path)`: Captura uma screenshot da página atual.

### Controlador Personalizado
- **CustomController**: Estende a classe `Controller` para adicionar ações personalizadas.
  - `setup_actions()`: Configura ações como extração de conteúdo, captura de screenshot e processamento de PDFs.
    - `extract_content(browser)`: Extrai o conteúdo da página atual para markdown.
    - `take_screenshot(browser)`: Captura uma imagem da página atual.
    - `extract_pdf_content(browser)`: Extrai o conteúdo de arquivos PDF.

### Prompts Personalizados
- **CustomSystemPrompt**: Define o prompt de sistema personalizado para o agente.
- **CustomAgentMessagePrompt**: Personaliza o formato de mensagens do agente.

### Agente Personalizado
- **CustomAgent**: Estende a classe `Agent` com funcionalidades específicas para o Deep Researcher.
  - `__init__(task, llm, browser, ...)`: Inicializa o agente com as configurações necessárias.

### Estado do Agente
- **AgentState**: Classe para controlar o estado do agente, permitindo interrupção da pesquisa.
  - `request_stop()`: Solicita a interrupção do processo.
  - `is_stop_requested()`: Verifica se foi solicitada a interrupção.

### Pesquisador Profundo
- **EnhancedDeepResearcher**: Implementação principal do pesquisador profundo.
  - `__init__(llm, max_query_num, max_search_iterations, max_steps, headless, use_vision)`: Inicializa o pesquisador com os parâmetros configuráveis.
  - `search(task, save_dir, agent_state, **kwargs)`: Executa a pesquisa e retorna os resultados.

### Funções de Pesquisa
- **enhanced_deep_research(task, llm, agent_state, **kwargs)**: Implementa o fluxo de pesquisa profunda.
- **generate_final_report(task, history_infos, save_dir, llm, error_msg, research_plan)**: Gera um relatório final baseado nos resultados da pesquisa.

### Classe Legada
- **DeepResearcher**: Estende `EnhancedDeepResearcher` mantendo compatibilidade com versões anteriores.
  - Adiciona o parâmetro `use_planner` que não é utilizado na implementação atual.

## Fluxo de Funcionamento

1. **Inicialização**: O sistema é inicializado com parâmetros como modelo de linguagem, número máximo de consultas e iterações.

2. **Preparação**: 
   - Um `CustomBrowser` é criado com as configurações especificadas (headless ou não).
   - Um `CustomAgent` é configurado com o navegador e o modelo de linguagem.

3. **Execução da Pesquisa**:
   - O sistema gera um plano de pesquisa com consultas específicas.
   - Para cada consulta, o sistema navega na web, extrai conteúdo relevante.
   - Informações são coletadas e processadas em cada iteração.

4. **Geração de Relatório**:
   - As informações coletadas são sintetizadas em um relatório final estruturado.
   - O relatório é salvo no diretório especificado.

## Parâmetros Configuráveis

- **max_query_num**: Número máximo de consultas de pesquisa a serem executadas.
- **max_search_iterations**: Número máximo de iterações de pesquisa.
- **max_steps**: Número máximo de passos de navegação permitidos ao agente.
- **headless**: Controla se o navegador será executado em modo invisível (true) ou visível (false).
- **use_vision**: Habilita o uso de recursos de visão no modelo de linguagem para interpretar conteúdo visual.
- **use_planner**: (Legado) Controla o uso do planejador de pesquisa.

## Exemplo de Uso

```python
llm = configure_llm("gemini-2.5-pro-preview")  # Configurar o modelo de linguagem
researcher = DeepResearcher(
    llm=llm,
    max_query_num=3,
    max_search_iterations=5,
    max_steps=25,
    headless=False,  # Navegador visível
    use_vision=True
)
resultado, caminho_relatorio = await researcher.search(
    task="Quais são os últimos avanços em energia renovável no Brasil?",
    save_dir="./resultados"
)
```

## Considerações Técnicas

1. O sistema utiliza um navegador automatizado para interagir com a web, podendo operar tanto em modo visível quanto invisível.

2. A extração de conteúdo pode ser realizada diretamente ou através do serviço jina.ai, que pode melhorar a qualidade da extração.

3. O sistema inclui tratamento para lidar com popups de cookies e notificações que poderiam atrapalhar a navegação.

4. A execução pode ser interrompida a qualquer momento usando o objeto `AgentState`.

5. O relatório final gerado contém informações estruturadas sobre o tópico pesquisado, com referências às fontes. 