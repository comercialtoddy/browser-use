# Frontend do Aplicativo de Pensamentos

Interface de usuário construída em React/TypeScript com Tailwind CSS para o Aplicativo de Pensamentos.

## Pré-requisitos

- Node.js 16+
- npm ou yarn

## Instalação

1. Instale as dependências:

```bash
npm install
# ou
yarn
```

2. Execute o servidor de desenvolvimento:

```bash
npm run dev
# ou
yarn dev
```

O aplicativo estará disponível em `http://localhost:5173` e acessível na rede local.

## Estrutura do Projeto

```
frontend/
  ├── public/            # Arquivos públicos e favicon
  ├── src/               # Código fonte
  │   ├── services/      # Serviços de API
  │   ├── App.tsx        # Componente principal
  │   └── main.tsx       # Ponto de entrada
  ├── .gitignore         # Arquivos ignorados pelo Git
  ├── index.html         # HTML principal
  ├── package.json       # Dependências e scripts
  ├── postcss.config.js  # Configuração do PostCSS
  ├── tailwind.config.js # Configuração do Tailwind CSS
  ├── tsconfig.json      # Configuração do TypeScript
  └── vite.config.ts     # Configuração do Vite
```

## Scripts Disponíveis

- `npm run dev` - Inicia o servidor de desenvolvimento
- `npm run build` - Constrói o aplicativo para produção
- `npm run preview` - Visualiza a versão de produção localmente

## Conectando com o Backend

O frontend se conecta ao backend através de requisições para `/api/*`. O proxy está configurado no arquivo `vite.config.ts` para redirecionar as requisições para o backend em `http://localhost:5000`. 