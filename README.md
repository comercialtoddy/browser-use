# Browser Use

Uma plataforma avançada que permite o uso de navegadores web controlados por agentes de IA para realizar pesquisas e tarefas automatizadas.

![Imagem da Interface do Browser Use](./frontend/public/screenshot.png)

## Sobre o Projeto

Browser Use é uma aplicação web que conecta diferentes LLMs (Large Language Models) a um navegador web, permitindo que estes modelos interajam com a internet de forma autônoma para realizar tarefas complexas. O projeto contém dois modos principais:

1. **Modo Simples**: Um agente de IA navega pela web para realizar tarefas específicas
2. **Modo Profundo (Deep Researcher)**: Um sistema avançado que realiza pesquisas profundas, coletando informações de múltiplas fontes e gerando relatórios detalhados

## Provedores e Modelos Suportados

A aplicação suporta uma ampla variedade de LLMs:

- **Google Gemini** (2.5, 2.0, 1.5)
- **OpenAI GPT** (4o, 4.1, 4, 3.5)
- **Anthropic Claude** (3.7, 3.6, 3.5)
- **DeepSeek** (Chat, R1)
- **xAI Grok** (2)

## Estrutura do Projeto

O projeto está dividido em duas partes principais:

- **Backend**: Desenvolvido em Python utilizando Flask, gerencia a comunicação com os LLMs e controla o navegador
- **Frontend**: Desenvolvido em React com TypeScript, fornece uma interface amigável para o usuário

## Instalação e Uso

### Pré-requisitos

- Python 3.9+
- Node.js 18+
- NPM ou Yarn

### Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Para mais detalhes, consulte os READMEs específicos em cada diretório.

## Contribuições

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes. 