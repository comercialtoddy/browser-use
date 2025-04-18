<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/browser-use-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/browser-use.png">
  <img alt="Shows a black Browser Use Logo in light color mode and a white one in dark color mode." src="./static/browser-use.png"  width="full">
</picture>

<h1 align="center">Enable AI to control your browser 🤖</h1>

[![GitHub stars](https://img.shields.io/github/stars/gregpr07/browser-use?style=social)](https://github.com/gregpr07/browser-use/stargazers)
[![Discord](https://img.shields.io/discord/1303749220842340412?color=7289DA&label=Discord&logo=discord&logoColor=white)](https://link.browser-use.com/discord)
[![Cloud](https://img.shields.io/badge/Cloud-☁️-blue)](https://cloud.browser-use.com)
[![Documentation](https://img.shields.io/badge/Documentation-📕-blue)](https://docs.browser-use.com)
[![Twitter Follow](https://img.shields.io/twitter/follow/Gregor?style=social)](https://x.com/gregpr07)
[![Twitter Follow](https://img.shields.io/twitter/follow/Magnus?style=social)](https://x.com/mamagnus00)
[![Weave Badge](https://img.shields.io/endpoint?url=https%3A%2F%2Fapp.workweave.ai%2Fapi%2Frepository%2Fbadge%2Forg_T5Pvn3UBswTHIsN1dWS3voPg%2F881458615&labelColor=#EC6341)](https://app.workweave.ai/reports/repository/org_T5Pvn3UBswTHIsN1dWS3voPg/881458615)

🌐 Browser-use is the easiest way to connect your AI agents with the browser.

💡 See what others are building and share your projects in our [Discord](https://link.browser-use.com/discord)! Want Swag? Check out our [Merch store](https://browsermerch.com).

🌤️ Skip the setup - try our <b>hosted version</b> for instant browser automation! <b>[Try the cloud ☁︎](https://cloud.browser-use.com)</b>.

# Quick start

With pip (Python>=3.11):

```bash
pip install browser-use
```

Install Playwright:
```bash
playwright install chromium
```

Spin up your agent:

```python
from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()

asyncio.run(main())
```

Add your API keys for the provider you want to use to your `.env` file.

```bash
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
AZURE_ENDPOINT=
AZURE_OPENAI_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
GROK_API_KEY=
NOVITA_API_KEY=
```

For other settings, models, and more, check out the [documentation 📕](https://docs.browser-use.com).

### Test with UI

You can test [browser-use with a UI repository](https://github.com/browser-use/web-ui)

Or simply run the gradio example:

```
uv pip install gradio
```

```bash
python examples/ui/gradio_demo.py
```

# Demos

<br/><br/>

[Task](https://github.com/browser-use/browser-use/blob/main/examples/use-cases/shopping.py): Add grocery items to cart, and checkout.

[![AI Did My Groceries](https://github.com/user-attachments/assets/d9359085-bde6-41d4-aa4e-6520d0221872)](https://www.youtube.com/watch?v=L2Ya9PYNns8)

<br/><br/>

Prompt: Add my latest LinkedIn follower to my leads in Salesforce.

![LinkedIn to Salesforce](https://github.com/user-attachments/assets/1440affc-a552-442e-b702-d0d3b277b0ae)

<br/><br/>

[Prompt](https://github.com/browser-use/browser-use/blob/main/examples/use-cases/find_and_apply_to_jobs.py): Read my CV & find ML jobs, save them to a file, and then start applying for them in new tabs, if you need help, ask me.'

https://github.com/user-attachments/assets/171fb4d6-0355-46f2-863e-edb04a828d04

<br/><br/>

[Prompt](https://github.com/browser-use/browser-use/blob/main/examples/browser/real_browser.py): Write a letter in Google Docs to my Papa, thanking him for everything, and save the document as a PDF.

![Letter to Papa](https://github.com/user-attachments/assets/242ade3e-15bc-41c2-988f-cbc5415a66aa)

<br/><br/>

[Prompt](https://github.com/browser-use/browser-use/blob/main/examples/custom-functions/save_to_file_hugging_face.py): Look up models with a license of cc-by-sa-4.0 and sort by most likes on Hugging face, save top 5 to file.

https://github.com/user-attachments/assets/de73ee39-432c-4b97-b4e8-939fd7f323b3

<br/><br/>

## More examples

For more examples see the [examples](examples) folder or join the [Discord](https://link.browser-use.com/discord) and show off your project.

# Vision

Tell your computer what to do, and it gets it done.

## Roadmap

### Agent

- [ ] Improve agent memory (summarize, compress, RAG, etc.)
- [ ] Enhance planning capabilities (load website specific context)
- [ ] Reduce token consumption (system prompt, DOM state)

### DOM Extraction

- [ ] Improve extraction for datepickers, dropdowns, special elements
- [ ] Improve state representation for UI elements

### Rerunning tasks

- [ ] LLM as fallback
- [ ] Make it easy to define workflow templates where LLM fills in the details
- [ ] Return playwright script from the agent

### Datasets

- [ ] Create datasets for complex tasks
- [ ] Benchmark various models against each other
- [ ] Fine-tuning models for specific tasks

### User Experience

- [ ] Human-in-the-loop execution
- [ ] Improve the generated GIF quality
- [ ] Create various demos for tutorial execution, job application, QA testing, social media, etc.

## Contributing

We love contributions! Feel free to open issues for bugs or feature requests. To contribute to the docs, check out the `/docs` folder.

## Local Setup

To learn more about the library, check out the [local setup 📕](https://docs.browser-use.com/development/local-setup).


`main` is the primary development branch with frequent changes. For production use, install a stable [versioned release](https://github.com/browser-use/browser-use/releases) instead.

---

## Cooperations

We are forming a commission to define best practices for UI/UX design for browser agents.
Together, we're exploring how software redesign improves the performance of AI agents and gives these companies a competitive advantage by designing their existing software to be at the forefront of the agent age.

Email [Toby](mailto:tbiddle@loop11.com?subject=I%20want%20to%20join%20the%20UI/UX%20commission%20for%20AI%20agents&body=Hi%20Toby%2C%0A%0AI%20found%20you%20in%20the%20browser-use%20GitHub%20README.%0A%0A) to apply for a seat on the committee.

## Swag

Want to show off your Browser-use swag? Check out our [Merch store](https://browsermerch.com). Good contributors will receive swag for free 👀.

## Citation

If you use Browser Use in your research or project, please cite:

```bibtex
@software{browser_use2024,
  author = {Müller, Magnus and Žunič, Gregor},
  title = {Browser Use: Enable AI to control your browser},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/browser-use/browser-use}
}
```

 <div align="center"> <img src="https://github.com/user-attachments/assets/06fa3078-8461-4560-b434-445510c1766f" width="400"/> 
 
[![Twitter Follow](https://img.shields.io/twitter/follow/Gregor?style=social)](https://x.com/gregpr07)
[![Twitter Follow](https://img.shields.io/twitter/follow/Magnus?style=social)](https://x.com/mamagnus00)
 
 </div>

<div align="center">
Made with ❤️ in Zurich and San Francisco
 </div>

# Aplicativo de Pensamentos

Um aplicativo simples para compartilhar seus pensamentos noturnos, com backend em Python/Flask e frontend em React/TypeScript.

## Estrutura do Projeto

```
browser-use/
  ├── app.py              # API REST do backend em Flask
  ├── requirements.txt    # Dependências do Python
  ├── frontend/           # Aplicativo React/TypeScript
  └── browser_use/        # Biblioteca principal Python
```

## Backend (Python/Flask)

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Dependências do Playwright (para funcionalidades de navegador)

### Instalação

1. Instale as dependências do Python:

```bash
pip install -r requirements.txt
```

2. Instale as dependências do Playwright:

```bash
python -m playwright install
```

3. Execute o servidor Flask:

```bash
python app.py
```

O servidor estará rodando em `http://localhost:5000` e acessível em sua rede local.

## Frontend (React/TypeScript)

### Pré-requisitos

- Node.js 16+
- npm ou yarn

### Instalação

1. Navegue até a pasta do frontend:

```bash
cd frontend
```

2. Instale as dependências:

```bash
npm install
# ou
yarn
```

3. Execute o servidor de desenvolvimento:

```bash
npm run dev
# ou
yarn dev
```

O frontend estará rodando em `http://localhost:5173`.

## API Endpoints

### GET /api/browser-info
Retorna informações básicas do navegador.

### GET /api/browser-stats
Retorna estatísticas de uso do navegador.

### GET /api/navigation-history
Retorna o histórico de navegação.

### GET /api/thoughts
Retorna a lista de pensamentos salvos.

### POST /api/thoughts
Salva um novo pensamento.

Corpo da requisição:
```json
{
  "thought": "Seu pensamento aqui"
}
```

## Configuração CORS

O backend está configurado para permitir requisições cross-origin de qualquer origem, o que é útil para desenvolvimento. Para produção, você deve limitar as origens permitidas.

## Licença

MIT

# Browser Use e Deep Researcher

Esta é uma aplicação que permite o uso avançado do navegador com agentes de IA, oferecendo duas funcionalidades principais:

1. **Browser Use**: Um agente de IA que navega pela web para realizar tarefas simples.
2. **Deep Researcher**: Uma versão avançada que realiza pesquisas profundas, coletando informações de múltiplas fontes.

## Modelos Suportados

A aplicação suporta os seguintes provedores e modelos de LLM:

- **Google**
  - Gemini 2.5 Pro Preview
  - Gemini 2.0 Flash
  - Gemini 1.5 Pro
  - Gemini 1.5 Flash

- **OpenAI**
  - GPT-4o (com diferentes configurações)
  - GPT-4.1
  - GPT-4 Turbo
  - GPT-4
  - GPT-3.5 Turbo

- **Anthropic**
  - Claude 3.7 Sonnet
  - Claude 3.6
  - Claude 3.5

- **DeepSeek**
  - DeepSeek Chat
  - DeepSeek R1

- **xAI**
  - Grok 2

## Instalação

1. Clone o repositório:
   ```
   git clone <repository_url>
   cd browser-use
   ```

2. Instale as dependências:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   ```
   cp .env.example .env
   # Edite o arquivo .env com suas chaves de API
   ```

4. Instale as dependências do navegador (Playwright):
   ```
   playwright install
   ```

## Uso

1. Inicie o servidor:
   ```
   cd backend
   python run.py
   ```

2. Acesse a interface web em `http://localhost:5000`

3. Selecione o provedor e modelo de sua preferência

4. Insira sua tarefa de pesquisa e inicie a execução

## APIs

A aplicação disponibiliza as seguintes APIs:

- `/api/providers` - Lista os provedores e modelos disponíveis
- `/api/research/start` - Inicia uma nova pesquisa
- `/api/research/<research_id>` - Obtém o status de uma pesquisa
- `/api/research/<research_id>/stop` - Para uma pesquisa em andamento
- `/api/research/<research_id>/report` - Obtém o relatório final de uma pesquisa

## Configurações Avançadas

### Uso de um navegador Chrome existente

Para usar um navegador Chrome existente, configure as seguintes variáveis no arquivo `.env`:

```
CHROME_CDP=ws://localhost:9222
CHROME_PATH=/caminho/para/chrome
CHROME_USER_DATA=/caminho/para/perfil
```

### Parâmetros para pesquisa profunda

- `max_query_num`: Número máximo de consultas por iteração (padrão: 3)
- `max_search_iterations`: Número máximo de iterações de pesquisa (padrão: 5)
- `max_steps`: Número máximo de passos por tarefa (padrão: 10)
- `headless`: Execução sem interface gráfica (padrão: True)
- `use_vision`: Usar visão para interpretar a página (padrão: False)

## Licença

[Incluir informações de licença]
