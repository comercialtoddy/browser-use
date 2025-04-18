"""
Script de inicialização para o BrowserUse e Deep Researcher
"""
import os
import sys
import logging
from app import app

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Verificar ambiente
    logger = logging.getLogger(__name__)
    logger.info("Iniciando BrowserUse e Deep Researcher")
    
    # Verificar presença de chaves de API
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "GROK_API_KEY": os.getenv("GROK_API_KEY")
    }
    
    keys_present = []
    for key, value in api_keys.items():
        if value:
            keys_present.append(key)
    
    if keys_present:
        logger.info(f"Chaves de API encontradas: {', '.join(keys_present)}")
    else:
        logger.warning("Nenhuma chave de API encontrada no ambiente. Configure-as para usar os modelos.")
    
    # Definir porta
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Iniciar aplicação
    app.run(debug=True, host=host, port=port) 