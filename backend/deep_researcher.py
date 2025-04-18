import asyncio
import os
import json
import logging
import re
from uuid import uuid4
from typing import Dict, List, Any, Optional, Tuple
import importlib.metadata

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importações do browser_use
from browser_use import Agent, BrowserConfig
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContextConfig, BrowserContext
from browser_use.agent.agent import AgentResult, ActionResult
from browser_use.agent.controller import Controller
from browser_use.agent.prompt import SystemPrompt, AgentMessagePrompt

from langchain_core.messages import SystemMessage, HumanMessage

def verify_browser_use_version():
    """Verifica e registra a versão do browser_use para diagnóstico"""
    try:
        version = importlib.metadata.version('browser_use')
        logger.info(f"Browser Use versão: {version}")
        return version
    except importlib.metadata.PackageNotFoundError:
        logger.warning("Não foi possível determinar a versão do browser_use")
        return "desconhecida"

# Verificar versão do browser_use ao inicializar
BROWSER_USE_VERSION = verify_browser_use_version()

class MainContentExtractor:
    """Extrai o conteúdo principal de uma página HTML com suporte a preservação de estrutura"""
    
    @staticmethod
    def extract(html: str, output_format: str = 'markdown') -> str:
        """
        Extrai o conteúdo principal de uma página HTML.
        
        Args:
            html: O conteúdo HTML da página
            output_format: O formato de saída ('markdown' ou 'text')
            
        Returns:
            O conteúdo principal da página no formato especificado
        """
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remover elementos que geralmente não contêm conteúdo principal
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'form']):
            tag.decompose()
        
        # Remover classes/IDs comuns de anúncios ou elementos de navegação
        ad_patterns = ['ad', 'banner', 'promo', 'sidebar', 'comment', 'cookie', 'popup', 'social']
        for pattern in ad_patterns:
            for element in soup.find_all(class_=re.compile(pattern, re.IGNORECASE)):
                element.decompose()
            for element in soup.find_all(id=re.compile(pattern, re.IGNORECASE)):
                element.decompose()
        
        # Identificar o elemento principal
        main_content = None
        
        # Tentar encontrar elementos que comumente contêm o conteúdo principal
        candidates = []
        for tag_name in ['article', 'main', 'div[role="main"]', '.post-content', '.article-body', '.content-body']:
            if '[' in tag_name:
                tag, attr = tag_name.replace(']', '').split('[role=')
                elements = soup.find_all(tag, {'role': attr.strip('"\'')})
            elif '.' in tag_name:
                class_name = tag_name[1:]
                elements = soup.find_all(class_=class_name)
            else:
                elements = soup.find_all(tag_name)
            
            candidates.extend(elements)
        
        # Selecionar o candidato com mais texto
        if candidates:
            main_content = max(candidates, key=lambda elem: len(elem.get_text()))
        else:
            # Se não encontrar elementos específicos, usar o body inteiro
            main_content = soup.body
        
        # Se estiver formatando como markdown
        if output_format == 'markdown':
            return MainContentExtractor._convert_to_markdown(main_content)
        else:
            # Para formato de texto simples
            text = main_content.get_text(separator='\n')
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            return text.strip()
    
    @staticmethod
    def _convert_to_markdown(element) -> str:
        """Converte um elemento BeautifulSoup para markdown preservando estrutura"""
        import re
        from bs4 import NavigableString
        
        if isinstance(element, NavigableString):
            return str(element)
        
        # Inicializa o markdown resultante
        result = ""
        
        # Elementos de bloco
        tag_name = element.name if element.name else ""
        
        # Processar cabeçalhos
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            prefix = '#' * level
            content = ''.join(MainContentExtractor._convert_to_markdown(child) for child in element.children)
            result += f"{prefix} {content.strip()}\n\n"
        
        # Processar parágrafos
        elif tag_name == 'p':
            content = ''.join(MainContentExtractor._convert_to_markdown(child) for child in element.children)
            if content.strip():
                result += f"{content.strip()}\n\n"
        
        # Processar listas
        elif tag_name == 'ul':
            for li in element.find_all('li', recursive=False):
                content = ''.join(MainContentExtractor._convert_to_markdown(child) for child in li.children)
                if content.strip():
                    result += f"* {content.strip()}\n"
            result += "\n"
        elif tag_name == 'ol':
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                content = ''.join(MainContentExtractor._convert_to_markdown(child) for child in li.children)
                if content.strip():
                    result += f"{i}. {content.strip()}\n"
            result += "\n"
        
        # Processar links
        elif tag_name == 'a' and element.get('href'):
            content = ''.join(MainContentExtractor._convert_to_markdown(child) for child in element.children)
            href = element.get('href')
            if href.startswith('/'):
                # Link relativo - tentar recuperar o domínio base
                base_url = element.find_parent('html').find('base', href=True)
                if base_url:
                    href = base_url['href'].rstrip('/') + href
            if content.strip():
                result += f"[{content.strip()}]({href})"
            else:
                result += href
        
        # Processar imagens
        elif tag_name == 'img' and element.get('src'):
            alt_text = element.get('alt', 'image')
            src = element.get('src')
            if src.startswith('/'):
                # Imagem relativa - tentar recuperar o domínio base
                base_url = element.find_parent('html').find('base', href=True)
                if base_url:
                    src = base_url['href'].rstrip('/') + src
            result += f"![{alt_text}]({src})\n\n"
        
        # Processar tabelas
        elif tag_name == 'table':
            # Cabeçalhos da tabela
            headers = []
            header_row = element.find('thead')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    headers.append(th.get_text().strip())
            
            if not headers and element.find('tr'):
                # Se não encontrou cabeçalhos mas tem linhas, usa a primeira linha
                first_row = element.find('tr')
                for cell in first_row.find_all(['th', 'td']):
                    headers.append(cell.get_text().strip())
            
            # Se tem cabeçalhos, adiciona a linha de cabeçalho
            if headers:
                result += "| " + " | ".join(headers) + " |\n"
                result += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            
            # Linhas da tabela
            tbody = element.find('tbody') or element
            for row in tbody.find_all('tr'):
                if row == first_row and not header_row:
                    continue  # Pula a primeira linha se já usamos como cabeçalho
                
                cells = []
                for cell in row.find_all(['td', 'th']):
                    cells.append(cell.get_text().strip())
                
                if cells:
                    result += "| " + " | ".join(cells) + " |\n"
            
            result += "\n"
        
        # Processar blocos de código
        elif tag_name in ['pre', 'code']:
            code_content = element.get_text()
            result += f"```\n{code_content}\n```\n\n"
        
        # Processar formatação inline
        elif tag_name == 'strong' or tag_name == 'b':
            content = ''.join(MainContentExtractor._convert_to_markdown(child) for child in element.children)
            result += f"**{content}**"
        elif tag_name == 'em' or tag_name == 'i':
            content = ''.join(MainContentExtractor._convert_to_markdown(child) for child in element.children)
            result += f"*{content}*"
        elif tag_name == 'blockquote':
            lines = []
            content = ''.join(MainContentExtractor._convert_to_markdown(child) for child in element.children)
            for line in content.strip().split('\n'):
                lines.append(f"> {line}")
            result += '\n'.join(lines) + "\n\n"
        
        # Para outros elementos, processar seus filhos
        else:
            for child in element.children:
                result += MainContentExtractor._convert_to_markdown(child)
        
        # Limpar espaços em branco extras e quebras de linha
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result

def repair_json(json_str: str) -> str:
    """
    Tenta reparar uma string JSON mal formada.
    
    Args:
        json_str: A string JSON potencialmente mal formada
        
    Returns:
        Uma string JSON válida, se possível
    """
    # Remover comentários
    json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # Remover vírgulas extras antes de fechamento de colchetes/chaves
    json_str = re.sub(r',\s*\]', ']', json_str)
    json_str = re.sub(r',\s*\}', '}', json_str)
    
    # Remover quebras de linha e espaços extras
    json_str = json_str.strip()
    
    # Verificar se o JSON é válido
    try:
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError as e:
        logger.warning(f"Erro ao decodificar JSON: {e}")
        
        # Tentativa de reparar problemas comuns
        if "Expecting ',' delimiter" in str(e):
            pos = int(re.search(r'char (\d+)', str(e)).group(1))
            json_str = json_str[:pos] + ',' + json_str[pos:]
        elif "Expecting property name enclosed in double quotes" in str(e):
            pos = int(re.search(r'char (\d+)', str(e)).group(1))
            json_str = json_str[:pos] + '"key":' + json_str[pos:]
        
        # Tentativa final - envolver em { } se não estiver envolvido
        if not json_str.startswith('{'):
            json_str = '{' + json_str
        if not json_str.endswith('}'):
            json_str = json_str + '}'
        
        # Verificar novamente
        try:
            json.loads(json_str)
            return json_str
        except:
            # Se falhar, retornar original
            logger.error("Não foi possível reparar o JSON")
            return json_str

class CustomBrowser(Browser):
    """Versão personalizada do Browser com suporte adicional para pesquisa e extração"""
    
    def __init__(self, config: BrowserConfig):
        super().__init__(config=config)
        
    async def new_context(self, config: Optional[BrowserContextConfig] = None) -> BrowserContext:
        """Cria um novo contexto com configurações melhoradas para pesquisa"""
        # Criar o contexto base
        if config is None:
            config = BrowserContextConfig()
        
        # Configurar User-Agent para desktop
        config.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        # Criar o contexto com as configurações atualizadas
        context = await super().new_context(config)
        
        # Adicionar script para desativar overlay de cookies/notificações comuns
        cookie_remover_script = """
        (function() {
            // Remove elements common in cookie/GDPR notices
            const selectors = [
                '[id*="cookie"], [class*="cookie"]',
                '[id*="consent"], [class*="consent"]',
                '[id*="popup"], [class*="popup"]',
                '[id*="gdpr"], [class*="gdpr"]',
                '[id*="overlay"], [class*="overlay"]',
                '[id*="newsletter"], [class*="newsletter"]'
            ];
            
            const removeElements = () => {
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const element of elements) {
                        // Check if it looks like a floating element or notification
                        const style = window.getComputedStyle(element);
                        if (
                            style.position === 'fixed' || 
                            style.position === 'absolute' || 
                            style.zIndex >= 1000 ||
                            element.id.includes('banner') ||
                            element.className.includes('banner')
                        ) {
                            element.remove();
                        }
                    }
                }
                
                // Também remover overflow hidden no body
                document.body.style.overflow = 'auto';
            };
            
            // Execute on load
            removeElements();
            
            // Set up observer to handle dynamically added elements
            const observer = new MutationObserver(removeElements);
            observer.observe(document.body, { childList: true, subtree: true });
            
            // Return cleanup function
            return () => observer.disconnect();
        })();
        """
        
        # Aplicamos o script quando a primeira página for aberta
        # Primeiro, criamos uma nova aba no contexto
        await context.create_new_tab()
        
        try:
            # Obter a página atual
            page = await context.get_current_page()
            
            # Configurar timeout mais longo
            await page.set_default_navigation_timeout(30000)
            
            # Adicionar script para remover cookies e popups
            await page.add_script_tag(content=cookie_remover_script)
            
            logger.info("Página configurada com sucesso: remoção de popups e timeout estendido")
        except Exception as e:
            logger.error(f"Erro ao configurar página: {e}")
        
        return context
        
    async def extract_page_content(self, context: BrowserContext, url: str, use_jina: bool = True) -> str:
        """
        Extrai o conteúdo de uma página web, usando jina.ai ou extração direta
        
        Args:
            context: O contexto do navegador
            url: URL da página a ser extraída
            use_jina: Se True, usa o serviço jina.ai para extração, caso contrário usa extração direta
            
        Returns:
            O conteúdo extraído em formato markdown
        """
        # Obter a página atual
        try:
            page = await context.get_current_page()
        except Exception as e:
            logger.warning(f"Não foi possível obter a página atual: {e}. Criando nova página.")
            await context.create_new_tab()
            page = await context.get_current_page()
        
        # Gravar URL atual para poder voltar depois
        current_url = page.url
        
        # Script para remover elementos de cookies e popups
        cookie_remover_script = """
        (function() {
            // Remove elements common in cookie/GDPR notices
            const selectors = [
                '[id*="cookie"], [class*="cookie"]',
                '[id*="consent"], [class*="consent"]',
                '[id*="popup"], [class*="popup"]',
                '[id*="gdpr"], [class*="gdpr"]',
                '[id*="overlay"], [class*="overlay"]',
                '[id*="newsletter"], [class*="newsletter"]'
            ];
            
            const removeElements = () => {
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const element of elements) {
                        // Check if it looks like a floating element or notification
                        const style = window.getComputedStyle(element);
                        if (
                            style.position === 'fixed' || 
                            style.position === 'absolute' || 
                            style.zIndex >= 1000 ||
                            element.id.includes('banner') ||
                            element.className.includes('banner')
                        ) {
                            element.remove();
                        }
                    }
                }
                
                // Também remover overflow hidden no body
                document.body.style.overflow = 'auto';
            };
            
            // Execute on load
            removeElements();
        })();
        """
        
        try:
            if use_jina:
                # Usar URL jina.ai para extração de conteúdo
                jina_url = f"https://r.jina.ai/{url}"
                logger.info(f"Navegando para URL Jina.ai: {jina_url}")
                await page.goto(jina_url)
            else:
                # Ir diretamente para a URL
                logger.info(f"Navegando para URL: {url}")
                await page.goto(url)
            
            # Aplicar script para remover popups
            await page.add_script_tag(content=cookie_remover_script)
            
            # Esperar um pouco para a página carregar completamente
            await asyncio.sleep(2)
            
            # Obter o conteúdo da página
            html_content = await page.content()
            
            # Extrair o conteúdo principal
            content = MainContentExtractor.extract(
                html=html_content,
                output_format='markdown',
            )
            
            # Incluir URL e título na saída
            title = await page.title()
            
            # Formatar a saída
            formatted_content = f"# {title}\n\nURL: {url}\n\n{content}"
            
            # Voltar para a URL original se necessário
            if current_url and current_url != url and current_url != jina_url:
                try:
                    await page.goto(current_url)
                except Exception as nav_error:
                    logger.warning(f"Não foi possível voltar para a URL original: {nav_error}")
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo da página {url}: {e}")
            return f"Erro ao extrair conteúdo da página {url}: {str(e)}"
            
    async def save_screenshot(self, context: BrowserContext, path: str) -> str:
        """
        Captura uma screenshot da página atual
        
        Args:
            context: O contexto do navegador
            path: Caminho onde a screenshot será salva
            
        Returns:
            Caminho para a screenshot salva
        """
        try:
            # Obter a página atual
            try:
                page = await context.get_current_page()
            except Exception as e:
                logger.warning(f"Não foi possível obter a página atual: {e}. Criando nova página.")
                await context.create_new_tab()
                page = await context.get_current_page()
            
            # Verificar se o diretório existe
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Remover popups antes de capturar a screenshot
            cookie_remover_script = """
            (function() {
                // Remove elements common in cookie/GDPR notices
                const selectors = [
                    '[id*="cookie"], [class*="cookie"]',
                    '[id*="consent"], [class*="consent"]',
                    '[id*="popup"], [class*="popup"]',
                    '[id*="gdpr"], [class*="gdpr"]',
                    '[id*="overlay"], [class*="overlay"]',
                    '[id*="newsletter"], [class*="newsletter"]'
                ];
                
                const removeElements = () => {
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            // Check if it looks like a floating element or notification
                            const style = window.getComputedStyle(element);
                            if (
                                style.position === 'fixed' || 
                                style.position === 'absolute' || 
                                style.zIndex >= 1000 ||
                                element.id.includes('banner') ||
                                element.className.includes('banner')
                            ) {
                                element.remove();
                            }
                        }
                    }
                    
                    // Também remover overflow hidden no body
                    document.body.style.overflow = 'auto';
                };
                
                // Execute on load
                removeElements();
            })();
            """
            
            # Aplicar script para remover popups
            await page.add_script_tag(content=cookie_remover_script)
            
            # Esperar um pouco para a página carregar completamente e os popups serem removidos
            await asyncio.sleep(1)
            
            # Capturar a screenshot
            await page.screenshot(path=path, full_page=True)
            logger.info(f"Screenshot salva em {path}")
            return path
        except Exception as e:
            logger.error(f"Erro ao capturar screenshot: {e}")
            return None

class CustomController(Controller):
    """Controlador personalizado para o agente Deep Researcher"""
    
    def __init__(self):
        super().__init__()
        self.setup_actions()
        
    def setup_actions(self):
        """Configura as ações personalizadas para o Deep Researcher"""
        
        @self.registry.action('Extract page content to get the pure markdown.')
        async def extract_content(browser: BrowserContext):
            """Extrai conteúdo de uma página em formato markdown"""
            page = await browser.get_current_page()
            url = page.url
            
            # Script para remover popups e avisos de cookies
            cookie_remover_script = """
            (function() {
                // Remove elements common in cookie/GDPR notices
                const selectors = [
                    '[id*="cookie"], [class*="cookie"]',
                    '[id*="consent"], [class*="consent"]',
                    '[id*="popup"], [class*="popup"]',
                    '[id*="gdpr"], [class*="gdpr"]',
                    '[id*="overlay"], [class*="overlay"]',
                    '[id*="newsletter"], [class*="newsletter"]'
                ];
                
                const removeElements = () => {
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            // Check if it looks like a floating element or notification
                            const style = window.getComputedStyle(element);
                            if (
                                style.position === 'fixed' || 
                                style.position === 'absolute' || 
                                style.zIndex >= 1000 ||
                                element.id.includes('banner') ||
                                element.className.includes('banner')
                            ) {
                                element.remove();
                            }
                        }
                    }
                    
                    // Também remover overflow hidden no body
                    document.body.style.overflow = 'auto';
                };
                
                // Execute on load
                removeElements();
            })();
            """
            
            # Verificar se o navegador é CustomBrowser para usar métodos avançados
            browser_instance = browser.browser
            
            try:
                if isinstance(browser_instance, CustomBrowser):
                    # Usar método avançado do CustomBrowser
                    logger.info(f"Extraindo conteúdo usando CustomBrowser para URL: {url}")
                    
                    # Aplicar script de remoção de cookies
                    await page.add_script_tag(content=cookie_remover_script)
                    
                    content = await browser_instance.extract_page_content(browser, url, use_jina=True)
                    logger.info(f"Conteúdo extraído com CustomBrowser ({len(content)} caracteres)")
                else:
                    # Fallback para o método tradicional
                    logger.info(f"Usando método tradicional de extração para URL: {url}")
                    
                    # Aplicar script de remoção de cookies
                    await page.add_script_tag(content=cookie_remover_script)
                    
                    # Usar URL jina.ai para extração de conteúdo
                    jina_url = f"https://r.jina.ai/{url}"
                    await page.goto(jina_url)
                    
                    # Obter o conteúdo da página
                    html_content = await page.content()
                    
                    # Extrair o conteúdo principal
                    content = MainContentExtractor.extract(
                        html=html_content,
                        output_format='markdown',
                    )
                    
                    # Voltar para a URL original
                    await page.go_back()
                    
                    logger.info(f"Conteúdo extraído com método tradicional ({len(content)} caracteres)")
                
                # Adicionar informações sobre a fonte
                if not content.startswith("# "):
                    title = await page.title()
                    content = f"# {title}\n\nURL: {url}\n\n{content}"
                
                msg = f'Extracted page content:\n{content}\n'
                
                return ActionResult(extracted_content=msg)
            except Exception as e:
                logger.error(f"Erro ao extrair conteúdo: {str(e)}")
                return ActionResult(error=f"Erro ao extrair conteúdo: {str(e)}")
            
        @self.registry.action('Take a screenshot of the current page.')
        async def take_screenshot(browser: BrowserContext):
            """Captura uma screenshot da página atual"""
            page = await browser.get_current_page()
            url = page.url
            
            # Gerar um nome de arquivo baseado na URL
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            screenshot_dir = os.path.join("./tmp/screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{url_hash}.png")
            
            # Verificar se o navegador é CustomBrowser para usar métodos avançados
            browser_instance = browser.browser
            if isinstance(browser_instance, CustomBrowser):
                # Usar método avançado do CustomBrowser
                path = await browser_instance.save_screenshot(browser, screenshot_path)
            else:
                # Fallback para o método tradicional
                try:
                    await page.screenshot(path=screenshot_path, full_page=True)
                    path = screenshot_path
                    logger.info(f"Screenshot salva em {path}")
                except Exception as e:
                    logger.error(f"Erro ao capturar screenshot: {e}")
                    path = None
            
            if path:
                return ActionResult(screenshot=f"Screenshot salva em {path}")
            else:
                return ActionResult(error=f"Falha ao capturar screenshot da página {url}")
                
        @self.registry.action('Extract content from a PDF file.')
        async def extract_pdf_content(browser: BrowserContext):
            """Extrai conteúdo de um arquivo PDF"""
            page = await browser.get_current_page()
            url = page.url
            
            # Verificar se é um PDF
            if not url.lower().endswith('.pdf'):
                return ActionResult(error="A URL atual não parece ser um arquivo PDF.")
            
            try:
                # Tentar baixar o PDF
                import tempfile
                import PyPDF2
                import requests
                
                # Criar um arquivo temporário
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    pdf_path = temp_file.name
                
                # Baixar o PDF
                response = requests.get(url, stream=True)
                with open(pdf_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extrair texto do PDF
                text = ""
                with open(pdf_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    num_pages = len(pdf_reader.pages)
                    
                    # Limite máximo de páginas para extrair (evitar PDFs muito grandes)
                    max_pages = min(num_pages, 50)
                    
                    # Extrair texto de cada página
                    for page_num in range(max_pages):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\n\n"
                
                # Limpar o arquivo temporário
                os.unlink(pdf_path)
                
                # Formatar como markdown
                pdf_name = url.split('/')[-1]
                content = f"# {pdf_name}\n\nURL: {url}\n\n## Conteúdo do PDF\n\n{text}"
                
                return ActionResult(extracted_content=f"Extracted PDF content:\n{content}\n")
            
            except Exception as e:
                logger.error(f"Erro ao extrair conteúdo do PDF {url}: {e}")
                return ActionResult(error=f"Falha ao extrair conteúdo do PDF: {str(e)}")

class CustomSystemPrompt(SystemPrompt):
    """Prompt de sistema personalizado para o Deep Researcher"""
    
    def get_content(self) -> str:
        base_content = super().get_content()
        
        # Adicionar instruções específicas para o Deep Researcher
        additional_content = """
        Como assistente de pesquisa avançado, você tem acesso a ferramentas especializadas para buscar, explorar e coletar informações detalhadas.

        ## INSTRUÇÕES DE PESQUISA:

        1. **ESTRATÉGIA DE BUSCA EFICIENTE**
           - Priorize fontes confiáveis e relevantes para o tópico
           - Aprofunde-se em links relevantes em vez de permanecer apenas em páginas de resultados de busca
           - Busque informações complementares e verifique detalhes em múltiplas fontes quando apropriado

        2. **EXTRAÇÃO DE CONTEÚDO**
           - Use a ação `Extract page content to get the pure markdown` ao encontrar páginas com informações detalhadas
           - Use `Take a screenshot of the current page` para capturar visualmente páginas importantes ou complexas
           - Para arquivos PDF, utilize `Extract content from a PDF file` para obter o texto completo

        3. **ANÁLISE DE DADOS**
           - Extraia dados estruturados como tabelas, estatísticas, e comparações importantes
           - Quando encontrar números, datas ou detalhes técnicos, capture-os com precisão
           - Preste atenção especial a informações atualizadas sobre o tópico
           
        4. **NAVEGAÇÃO INTELIGENTE**
           - Evite páginas de anúncios ou não relevantes
           - Quando encontrar paredes de pagamento (paywalls), tente métodos alternativos para acessar informações
           - Identifique e utilize seções específicas de sites que contenham informações mais relevantes (ex: seções "About", "FAQ", "Research", etc.)

        LEMBRE-SE: Seu objetivo é coletar informações completas, precisas e bem estruturadas que respondam à consulta de pesquisa de forma abrangente.
        """
        
        return f"{base_content}\n\n{additional_content}"

class CustomAgentMessagePrompt(AgentMessagePrompt):
    """Prompt de mensagem personalizado para o Deep Researcher"""
    
    def __init__(self, add_infos: str = ""):
        super().__init__()
        self.add_infos = add_infos
    
    def get_content(self, **kwargs) -> str:
        base_content = super().get_content(**kwargs)
        
        if self.add_infos:
            return f"{base_content}\n\nAdditional Information: {self.add_infos}"
        return base_content

class CustomAgent(Agent):
    """Agente personalizado para o Deep Researcher"""
    
    def __init__(
        self,
        task: str,
        llm: Any,
        browser: Optional[Browser] = None,
        browser_context: Optional[BrowserContext] = None,
        controller: Optional[Controller] = None,
        use_vision: bool = False,
        add_infos: str = "",
        max_actions_per_step: int = 5
    ):
        # Se não houver navegador, criar um CustomBrowser em vez do Browser padrão
        if not browser and not browser_context:
            browser = CustomBrowser(
                config=BrowserConfig(
                    headless=True,
                    disable_security=True,
                )
            )
        
        # Se não houver controlador, usar o padrão
        if not controller:
            controller = CustomController()
        
        # Configurar prompts personalizados
        self.add_infos = add_infos
        
        super().__init__(
            task=task,
            llm=llm,
            browser=browser,
            browser_context=browser_context,
            controller=controller,
            use_vision=use_vision,
            max_actions_per_step=max_actions_per_step
        )

class AgentState:
    """Estado do agente Deep Researcher"""
    
    def __init__(self):
        self.stop_requested = False
    
    def request_stop(self):
        """Solicita parada da execução"""
        self.stop_requested = True
    
    def is_stop_requested(self) -> bool:
        """Verifica se a parada foi solicitada"""
        return self.stop_requested

class EnhancedDeepResearcher:
    """Implementação aprimorada do agente Deep Researcher usando planejador e múltiplos agentes especializados"""
    
    def __init__(self, 
                 llm: Any,
                 max_query_num: int = 3,
                 max_search_iterations: int = 5,
                 max_steps: int = 10,
                 headless: bool = True,
                 use_vision: bool = False):
        """
        Inicializa um pesquisador profundo aprimorado com planejador e múltiplos agentes.
        
        Args:
            llm: Modelo de linguagem para usar na pesquisa (será usado para todos os agentes)
            max_query_num: Número máximo de consultas por iteração
            max_search_iterations: Número máximo de iterações de pesquisa
            max_steps: Número máximo de passos por agente
            headless: Se True, executa o navegador em modo headless (sem interface gráfica)
            use_vision: Se True, usa capacidades de visão do LLM para análise de páginas
        """
        self.llm = llm
        self.max_query_num = max_query_num
        self.max_search_iterations = max_search_iterations
        self.max_steps = max_steps
        self.headless = headless
        self.use_vision = use_vision
        logger.info(f"EnhancedDeepResearcher inicializado com: max_query_num={max_query_num}, " +
                   f"max_search_iterations={max_search_iterations}, max_steps={max_steps}, " +
                   f"headless={headless}, use_vision={use_vision}, browser_use_version={BROWSER_USE_VERSION}")
        
    async def search(self, task: str, save_dir: Optional[str] = None, agent_state: Optional[AgentState] = None, **kwargs) -> Tuple[str, Optional[str]]:
        """
        Executa a pesquisa profunda aprimorada usando o planejador e múltiplos agentes especializados.
        
        Args:
            task: A tarefa de pesquisa a ser executada
            save_dir: Diretório para salvar os resultados (se None, usa diretório padrão)
            agent_state: Estado do agente para controle de parada
            **kwargs: Parâmetros adicionais para a pesquisa
            
        Returns:
            Tupla com (relatório_final, caminho_do_arquivo)
        """
        # Criar um novo dicionário que não inclui parâmetros que já são passados explicitamente
        enhanced_research_kwargs = kwargs.copy()
        
        # Remover todos os parâmetros que já são passados explicitamente
        params_to_remove = ['use_vision', 'max_steps', 'max_query_num', 
                           'max_search_iterations', 'headless']
        
        removed_params = []
        for param in params_to_remove:
            if param in enhanced_research_kwargs:
                del enhanced_research_kwargs[param]
                removed_params.append(param)
        
        if removed_params:
            logger.info(f"EnhancedDeepResearcher.search: Parâmetros removidos para evitar duplicação: {', '.join(removed_params)}")
        
        logger.info(f"Iniciando pesquisa profunda aprimorada para: '{task}'")
        
        return await enhanced_deep_research(
            task=task,
            llm=self.llm,
            agent_state=agent_state or AgentState(),
            save_dir=save_dir,
            max_query_num=self.max_query_num,
            max_search_iterations=self.max_search_iterations,
            max_steps=self.max_steps,
            headless=self.headless,
            use_vision=self.use_vision,
            **enhanced_research_kwargs
        )

async def enhanced_deep_research(task, llm, agent_state=None, **kwargs):
    """
    Executa pesquisa profunda aprimorada com planejador e agentes especializados.
    
    Esta função implementa uma abordagem coordenada utilizando um agente planejador
    e múltiplos agentes especializados para obter resultados mais abrangentes.
    
    Args:
        task: A tarefa de pesquisa a ser executada
        llm: Modelo de linguagem a ser usado (o mesmo para todos os agentes)
        agent_state: Estado do agente para controle de parada
        **kwargs: Parâmetros adicionais
        
    Returns:
        Tuple[str, Optional[str]]: Relatório final e caminho do arquivo
    """
    # Criar um novo ID para a pesquisa
    task_id = str(uuid4())
    save_dir = kwargs.get("save_dir", os.path.join(f"./tmp/deep_research/{task_id}"))
    logger.info(f"Save Enhanced Deep Research at: {save_dir}")
    os.makedirs(save_dir, exist_ok=True)

    # Configurar parâmetros de pesquisa
    max_query_num = kwargs.get("max_query_num", 3)
    max_steps = kwargs.get("max_steps", 10)
    max_search_iterations = kwargs.get("max_search_iterations", 5)
    use_vision = kwargs.get("use_vision", False)
    headless = kwargs.get("headless", True)
    browser = None
    main_context = None
    browser_contexts = []  # Lista para rastrear todos os contextos criados
    
    # Armazenar o loop atual para restaurá-lo posteriormente
    original_loop = None
    new_loop = None
    
    try:
        # Capturar o loop atual se existir
        try:
            original_loop = asyncio.get_event_loop()
            if original_loop.is_closed():
                original_loop = None
        except RuntimeError:
            # Não há loop de eventos no thread atual
            original_loop = None
        
        # Criar um novo loop de eventos dedicado
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        logger.info("Criado novo loop de eventos para enhanced_deep_research")
        
        # Inicializar o navegador compartilhado
        browser = CustomBrowser(
            config=BrowserConfig(
                headless=headless,
                disable_security=kwargs.get("disable_security", True),
            )
        )
        
        # Criar o contexto principal do navegador que será compartilhado
        main_context = await browser.new_context()
        browser_contexts.append(main_context)
        logger.info("Contexto principal do navegador criado com sucesso")
        
        # Criar o controlador personalizado
        controller = CustomController()
        
        # Estrutura para armazenar resultados
        all_search_results = []
        history_infos = []
        
        # === FASE 1: PLANEJAMENTO ===
        logger.info("=== FASE 1: PLANEJAMENTO DA PESQUISA ===")
        
        # Configurar prompt do sistema para o planejador
        planner_system_prompt = f"""
        Você é um **Planejador de Pesquisa Estratégica**, especializado em desenvolver planos detalhados para 
        pesquisas complexas. Sua tarefa é analisar a consulta do usuário e criar um plano abrangente que:
        
        1. Identifique os principais aspectos que precisam ser investigados
        2. Defina objetivos específicos para cada aspecto
        3. Priorize as áreas de pesquisa em ordem de importância
        4. Determine os tipos de fontes mais relevantes para cada aspecto
        5. Sugira abordagens específicas para extrair informações dessas fontes
        
        Forneça um plano detalhado estruturado no seguinte formato JSON:
        
        ```json
        {{
          "objetivo_principal": "Descreva o objetivo principal da pesquisa",
          "aspectos_chave": [
            {{
              "titulo": "Nome do aspecto",
              "descrição": "Descrição detalhada do que buscar",
              "prioridade": "alta|média|baixa",
              "fontes_recomendadas": ["Tipo de fonte 1", "Tipo de fonte 2"],
              "consultas_sugeridas": [
                "consulta 1",
                "consulta 2",
                "consulta 3"
              ]
            }}
          ],
          "estrategia_consolidacao": "Como consolidar as informações encontradas"
        }}
        ```
        
        Você pode incluir até {max_search_iterations} aspectos_chave, cada um com até {max_query_num} consultas_sugeridas.
        """
        
        # Criar o agente planejador
        try:
            logger.info("Criando e executando o agente planejador...")
            
            planner_agent = CustomAgent(
                task=f"Analise esta solicitação de pesquisa e crie um plano estratégico detalhado: {task}",
                llm=llm,
                add_infos=planner_system_prompt,
                browser=browser,
                browser_context=main_context,
                controller=controller,
                use_vision=use_vision,
                max_actions_per_step=2
            )
            
            # Executar o planejador para obter o plano
            planner_result = await planner_agent.run(max_steps=3)  # Limitar passos para o planejador
            plan_content = planner_result.final_result()
            
            # Tentar extrair o plano JSON
            try:
                # Limpar o conteúdo para extrair apenas o JSON
                plan_content = re.sub(r'```json|```', '', plan_content)
                plan_content = repair_json(plan_content)
                research_plan = json.loads(plan_content)
                
                # Salvar o plano
                plan_path = os.path.join(save_dir, "research_plan.json")
                with open(plan_path, "w", encoding="utf-8") as f:
                    json.dump(research_plan, f, indent=2)
                logger.info(f"Plano de pesquisa salvo em: {plan_path}")
                
            except json.JSONDecodeError:
                logger.warning("Não foi possível extrair o plano JSON. Usando plano padrão.")
                # Plano padrão se não conseguir extrair
                research_plan = {
                    "objetivo_principal": task,
                    "aspectos_chave": [
                        {
                            "titulo": "Pesquisa Principal",
                            "descrição": "Informações gerais sobre o tópico",
                            "prioridade": "alta",
                            "fontes_recomendadas": ["Sites confiáveis", "Artigos acadêmicos"],
                            "consultas_sugeridas": [task]
                        }
                    ]
                }
            
            logger.info(f"Plano criado: {research_plan['objetivo_principal']}")
            logger.info(f"Aspectos a pesquisar: {len(research_plan['aspectos_chave'])}")
            
        except Exception as e:
            logger.error(f"Erro ao executar o planejador: {e}")
            # Plano padrão se o planejador falhar
            research_plan = {
                "objetivo_principal": task,
                "aspectos_chave": [
                    {
                        "titulo": "Pesquisa Principal",
                        "descrição": "Informações gerais sobre o tópico",
                        "prioridade": "alta",
                        "fontes_recomendadas": ["Sites confiáveis", "Artigos acadêmicos"],
                        "consultas_sugeridas": [task]
                    }
                ]
            }
        
        # === FASE 2: EXECUÇÃO DOS AGENTES ESPECIALIZADOS ===
        logger.info("=== FASE 2: EXECUÇÃO DOS AGENTES ESPECIALIZADOS ===")
        
        # Ordenar aspectos por prioridade
        aspectos = sorted(
            research_plan["aspectos_chave"],
            key=lambda x: {"alta": 0, "média": 1, "baixa": 2}.get(x.get("prioridade", "média"), 1)
        )
        
        # Informações adicionais para o agente
        add_infos = """
        1. Por favor, clique no link mais relevante para obter informações mais profundas, em vez de ficar apenas na página de resultados da pesquisa.
        2. Ao abrir um arquivo PDF, lembre-se de extrair o conteúdo usando extract_content em vez de apenas abri-lo para visualização.
        3. Use a ação Take a screenshot of the current page para capturar páginas com visualizações ou gráficos importantes.
        4. Quando encontrar tabelas ou dados estruturados, tente capturá-los com precisão.
        5. Analise criticamente as informações encontradas e verifique a credibilidade das fontes.
        """
        
        # Executar um agente para cada aspecto do plano
        for i, aspecto in enumerate(aspectos):
            if agent_state and agent_state.is_stop_requested():
                logger.info("Parada solicitada. Interrompendo execução de agentes.")
                break
                
            logger.info(f"Executando agente para o aspecto: {aspecto['titulo']} (Prioridade: {aspecto['prioridade']})")
            
            # Pegar as consultas sugeridas (limitar ao máximo configurado)
            consultas = aspecto.get("consultas_sugeridas", [])[:max_query_num]
            if not consultas:
                consultas = [f"Pesquisar sobre {aspecto['titulo']}"]
            
            # Criar novo contexto para este aspecto
            aspecto_context = await browser.new_context()
            browser_contexts.append(aspecto_context)
            
            # Estrutura para armazenar resultados deste aspecto
            aspecto_results = []
            
            # Executar um agente para cada consulta deste aspecto
            for j, consulta in enumerate(consultas):
                if agent_state and agent_state.is_stop_requested():
                    logger.info("Parada solicitada. Interrompendo execução de consultas.")
                    break
                
                logger.info(f"Executando consulta {j+1}/{len(consultas)}: {consulta}")
                
                try:
                    # Contexto específico para cada consulta
                    query_context = await browser.new_context()
                    browser_contexts.append(query_context)
                    
                    # Instruções específicas para esta consulta
                    query_instructions = f"""
                    {add_infos}
                    
                    INFORMAÇÕES SOBRE ESTA CONSULTA:
                    Aspecto: {aspecto['titulo']}
                    Descrição: {aspecto['descrição']}
                    Fontes recomendadas: {', '.join(aspecto.get('fontes_recomendadas', ['Sites confiáveis']))}
                    
                    Seu objetivo é encontrar informações precisas, factuais e relevantes sobre esta consulta específica.
                    """
                    
                    # Criar o agente para esta consulta
                    query_agent = CustomAgent(
                        task=consulta,
                        llm=llm,
                        add_infos=query_instructions,
                        browser=browser,
                        browser_context=query_context,
                        controller=controller,
                        use_vision=use_vision,
                        max_actions_per_step=5
                    )
                    
                    # Executar o agente
                    agent_result = await query_agent.run(max_steps=max_steps)
                    
                    # Processar resultado
                    result_content = agent_result.final_result()
                    if result_content:
                        # Salvar o resultado
                        result_path = os.path.join(save_dir, f"aspecto_{i+1}_consulta_{j+1}.md")
                        with open(result_path, "w", encoding="utf-8") as f:
                            f.write(f"# Consulta: {consulta}\n\n{result_content}")
                        
                        # Adicionar aos resultados deste aspecto
                        aspecto_results.append({
                            "consulta": consulta,
                            "conteudo": result_content,
                            "caminho": result_path
                        })
                        
                        # Processar para extrair informações estruturadas
                        try:
                            # Dividir resultado por conteúdo extraído 
                            query_results_split = result_content.split("Extracted page content:")
                            for qi, query_result_ in enumerate(query_results_split):
                                if not query_result_:
                                    continue
                                
                                # Preparar para registrar informações usando o LLM
                                record_system_prompt = """
                                Você é um especialista em extração de informações. Analise o conteúdo fornecido e 
                                extraia informações úteis e relevantes no formato JSON especificado abaixo:
                                
                                ```json
                                [
                                  {
                                    "url": "URL da fonte",
                                    "title": "Título da fonte",
                                    "summary_content": "Resumo conciso do conteúdo, preservando dados e figuras importantes",
                                    "thinking": "Como esta informação contribui para a pesquisa"
                                  }
                                ]
                                ```
                                
                                Evite redundância e procure extrair apenas informações novas e relevantes.
                                """
                                
                                record_prompt = f"Consulta: {consulta}\nAspecto: {aspecto['titulo']}\n\nConteúdo para análise:\n{query_result_}"
                                
                                # Obter informações do LLM
                                from langchain_core.messages import SystemMessage, HumanMessage
                                record_messages = [
                                    SystemMessage(content=record_system_prompt),
                                    HumanMessage(content=record_prompt)
                                ]
                                
                                # Extrair informações
                                try:
                                    ai_record_msg = llm.invoke(record_messages)
                                    record_content = ai_record_msg.content
                                    record_content = repair_json(record_content)
                                    new_record_infos = json.loads(record_content)
                                    history_infos.extend(new_record_infos)
                                    logger.info(f"Registradas {len(new_record_infos)} novas informações")
                                except Exception as e:
                                    logger.error(f"Erro ao extrair informações: {e}")
                        except Exception as e:
                            logger.error(f"Erro ao processar conteúdo extraído: {e}")
                    
                except Exception as e:
                    logger.error(f"Erro ao executar consulta {consulta}: {e}")
                
                # Fechar contexto da consulta
                try:
                    await query_context.close()
                except Exception as e:
                    logger.warning(f"Erro ao fechar contexto da consulta: {e}")
            
            # Adicionar resultados deste aspecto ao total
            all_search_results.append({
                "aspecto": aspecto['titulo'],
                "prioridade": aspecto['prioridade'],
                "resultados": aspecto_results
            })
            
            # Fechar contexto do aspecto
            try:
                await aspecto_context.close()
            except Exception as e:
                logger.warning(f"Erro ao fechar contexto do aspecto: {e}")
        
        # === FASE 3: CONSOLIDAÇÃO E RELATÓRIO FINAL ===
        logger.info("=== FASE 3: CONSOLIDAÇÃO E RELATÓRIO FINAL ===")
        
        # Salvar todas as informações extraídas
        record_json_path = os.path.join(save_dir, "record_infos.json")
        with open(record_json_path, "w", encoding="utf-8") as fw:
            json.dump(history_infos, fw, indent=4)
        logger.info(f"Informações extraídas salvas em {record_json_path}")
        
        # Salvar resultados da pesquisa
        results_json_path = os.path.join(save_dir, "search_results.json")
        with open(results_json_path, "w", encoding="utf-8") as fw:
            json.dump(all_search_results, fw, indent=4)
        logger.info(f"Resultados da pesquisa salvos em {results_json_path}")
        
        # Gerar relatório final
        return await generate_final_report(task, history_infos, save_dir, llm, 
                                          error_msg=None, 
                                          research_plan=research_plan)
        
    except Exception as e:
        logger.error(f"Erro na pesquisa profunda aprimorada: {e}")
        return await generate_final_report(task, history_infos or [], save_dir, llm, str(e))
        
    finally:
        # Fechar contextos e navegador
        try:
            # Fechar todos os contextos de navegador
            for ctx in browser_contexts:
                try:
                    await ctx.close()
                except Exception as e:
                    logger.warning(f"Erro ao fechar contexto de navegador: {e}")
            
            # Fechar o navegador principal se existir
            if browser:
                try:
                    await browser.close()
                    logger.info("Navegador fechado com sucesso.")
                except Exception as e:
                    logger.warning(f"Erro ao fechar navegador principal: {e}")
            
            # Restaurar o loop de eventos original
            if original_loop and not original_loop.is_closed():
                asyncio.set_event_loop(original_loop)
                logger.info("Loop de eventos original restaurado.")
            
            logger.info("Limpeza de recursos concluída.")
            
        except Exception as cleanup_error:
            logger.error(f"Erro durante limpeza de recursos: {cleanup_error}")

# Modificar a função generate_final_report para aceitar o plano de pesquisa
async def generate_final_report(task, history_infos, save_dir, llm, error_msg=None, research_plan=None):
    """Generate report from collected information with error handling and research plan integration"""
    try:
        # Verificar se temos um loop de eventos válido
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                logger.info("Criado novo loop de eventos para geração do relatório")
        except Exception as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info(f"Novo loop de eventos criado para relatório após erro: {e}")
            
        logger.info("\nGerando relatório final a partir dos dados coletados...")

        # Sistema de prompt aprimorado para incluir o plano de pesquisa
        writer_system_prompt = """
        Você é um **Pesquisador Especializado** responsável por criar relatórios detalhados, precisos e bem estruturados 
        que atendam completamente às necessidades do usuário. Use o formato Markdown para criar um relatório 
        informativo e visualmente atraente.

        **Instruções específicas:**

        * **Estrutura de Impacto:** O relatório deve ter uma estrutura clara, lógica e impactante. Comece com uma introdução envolvente, 
          desenvolva parágrafos que fluam de maneira lógica, e conclua com uma conclusão concisa e memorável.
          
        * **Linguagem Envolvente:** Empregue linguagem precisa, vívida e descritiva para tornar o relatório cativante.
          
        * **Precisão e Citações:** Garanta que todas as informações apresentadas sejam meticulosamente precisas e apoiadas pelos dados disponíveis.
          Cite fontes usando números sequenciais entre colchetes no texto (ex: [1], [2]). Estes números devem corresponder 
          a uma lista de referências no final do relatório.
          
        * **Formatação Markdown:** Utilize a formatação Markdown para excelente legibilidade e aparência profissional.
          
        * **Tabelas para Comparações:** Quando apropriado, apresente comparações de dados em tabelas bem estruturadas.
          
        * **Lista de Referências:** Formate as referências da seguinte forma:
          `[1] Título (URL, se disponível)`
          Cada referência deve ser separada por uma linha em branco.
        
        **Entrada:**
        1. **Instrução do Usuário:** A instrução original dada pelo usuário.
        2. **Informações da Pesquisa:** Informações coletadas das consultas de pesquisa.
        3. **Plano de Pesquisa:** O plano estratégico usado para conduzir a pesquisa.
        
        **RESTRIÇÃO FINAL ABSOLUTA:** Sua saída deve conter APENAS o relatório pronto para publicação em Markdown.
        O relatório deve começar diretamente com o título e parágrafo introdutório, e terminar após a conclusão e 
        a lista de referências (se aplicável).
        """

        history_infos_ = json.dumps(history_infos, indent=4)
        
        # Incluir informações do plano de pesquisa, se disponível
        plan_info = ""
        if research_plan:
            plan_info = f"""
            ## Plano de Pesquisa Utilizado:
            
            **Objetivo Principal:** {research_plan.get('objetivo_principal', task)}
            
            **Aspectos Pesquisados:**
            """
            
            for i, aspecto in enumerate(research_plan.get('aspectos_chave', [])):
                plan_info += f"""
                {i+1}. **{aspecto.get('titulo', 'Aspecto ' + str(i+1))}** (Prioridade: {aspecto.get('prioridade', 'não especificada')})
                   - Descrição: {aspecto.get('descrição', 'Não fornecida')}
                   - Fontes recomendadas: {', '.join(aspecto.get('fontes_recomendadas', ['Não especificadas']))}
                   - Consultas realizadas: {', '.join([f'"{q}"' for q in aspecto.get('consultas_sugeridas', ['Não especificadas'])])}
                """
            
            plan_info += f"\n**Estratégia de Consolidação:** {research_plan.get('estrategia_consolidacao', 'Não especificada')}\n"
        
        report_prompt = f"Instrução do Usuário: {task}\n\nInformações da Pesquisa:\n{history_infos_}\n\nPlano de Pesquisa:\n{plan_info}"
        report_messages = [SystemMessage(content=writer_system_prompt),
                           HumanMessage(content=report_prompt)]
        
        # Usar try-except para garantir que erros na invocação do LLM sejam capturados
        try:
            ai_report_msg = llm.invoke(report_messages)
            report_content = ai_report_msg.content
        except Exception as llm_error:
            logger.error(f"Erro ao gerar relatório com LLM: {llm_error}")
            report_content = f"# Erro na Geração do Relatório\n\nOcorreu um erro ao gerar o relatório final: {str(llm_error)}\n\n## Dados Coletados\n\nOs seguintes dados foram coletados durante a pesquisa:\n\n```json\n{history_infos_}\n```"
            
        report_content = re.sub(r"^```\s*markdown\s*|^\s*```|```\s*$", "", report_content, flags=re.MULTILINE)
        report_content = report_content.strip()

        # Add error notification to the report
        if error_msg:
            report_content = f"## ⚠️ Pesquisa Incompleta - Resultados Parciais\n" \
                             f"**O processo de pesquisa foi interrompido por um erro:** {error_msg}\n\n" \
                             f"{report_content}"

        report_file_path = os.path.join(save_dir, "final_report.md")
        with open(report_file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"Relatório salvo em: {report_file_path}")
        
        # Restaurar o loop de eventos original se necessário
        try:
            asyncio.set_event_loop(asyncio.get_event_loop_policy().get_event_loop())
        except Exception as e:
            logger.warning(f"Erro ao restaurar loop de eventos após geração do relatório: {e}")
            
        return report_content, report_file_path

    except Exception as report_error:
        logger.error(f"Falha ao gerar relatório parcial: {report_error}")
        return f"Erro ao gerar relatório: {str(report_error)}", None 

class DeepResearcher(EnhancedDeepResearcher):
    """Classe de compatibilidade que estende EnhancedDeepResearcher"""
    
    def __init__(self, 
                 llm: Any,
                 max_query_num: int = 3,
                 max_search_iterations: int = 5,
                 max_steps: int = 10,
                 headless: bool = True,
                 use_vision: bool = False,
                 use_planner: bool = True):  # Parâmetro adicional ignorado
        """
        Inicializador compatível com a versão antiga da classe.
        
        Args:
            llm: Modelo de linguagem para usar na pesquisa
            max_query_num: Número máximo de consultas por iteração
            max_search_iterations: Número máximo de iterações de pesquisa
            max_steps: Número máximo de passos por agente
            headless: Se True, executa o navegador em modo headless
            use_vision: Se True, usa capacidades de visão do LLM
            use_planner: Parâmetro ignorado, mantido para compatibilidade
        """
        super().__init__(
            llm=llm,
            max_query_num=max_query_num,
            max_search_iterations=max_search_iterations,
            max_steps=max_steps,
            headless=headless,
            use_vision=use_vision
        )
        # Logging para informar que estamos usando a versão melhorada
        logger.info("Usando DeepResearcher aprimorado com planejador e múltiplos agentes") 