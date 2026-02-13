"""
NEXUS-7 Registry Loader
═══════════════════════════════════════════════════════════════════════════════
Carga y gestiona el registro central (registry.yaml).
"""

import yaml
from pathlib import Path
from typing import Dict, Optional


class AgentRegistry:
    """Registro de agentes basado en registry.yaml"""
    
    def __init__(self, registry_path: str = ".ai/memory/core/registry.yaml"):
        self.registry_path = Path(registry_path)
        self._config: Optional[dict] = None
        self._load_registry()
    
    def _load_registry(self):
        """Carga y valida el registro"""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
    
    def reload(self):
        """Recarga el registro"""
        self._load_registry()
    
    def get_agent_config(self, agent_id: str) -> Optional[dict]:
        """Obtiene configuración de un agente"""
        return self._config.get("agents", {}).get(agent_id)
    
    def get_all_agents(self) -> Dict[str, dict]:
        """Obtiene todos los agentes"""
        return self._config.get("agents", {})
    
    def get_skill_config(self, skill_id: str) -> Optional[dict]:
        """Obtiene configuración de un skill"""
        return self._config.get("skills", {}).get(skill_id)
    
    def get_system_config(self) -> dict:
        """Obtiene configuración del sistema"""
        return self._config.get("system", {})
    
    def validate_agent_exists(self, agent_id: str) -> bool:
        """Valida que un agente exista en el registro"""
        return agent_id in self._config.get("agents", {})
