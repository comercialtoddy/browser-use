"""
Este arquivo exporta classes necessárias de views.py para manter compatibilidade.
"""

from browser_use.agent.views import ActionResult, AgentState, AgentOutput

# Re-export as AgentResult para manter compatibilidade
AgentResult = AgentOutput 