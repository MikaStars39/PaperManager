import toml
import os
from typing import Dict, Any, List

class ConfigManager:
    def __init__(self, config_file: str = "config/base.toml"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return toml.load(f)
            else:
                # Return default configuration if file doesn't exist
                return self.get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "api": {
                "model": "google/gemini-2.0-flash-001",
                "temperature": 0.3,
                "max_tokens": 1000000,
                "api_key": ""
            },
            "paper": {
                "types": ["Agent/RL", "Interpretability", "Efficiency"],
                "csv_file": "papers.csv"
            },
            "ui": {
                "theme": "soft",
                "chatbot_height": 500,
                "debug": True
            }
        }
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                toml.dump(self.config, f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def update_config(self, section: str, key: str, value: Any):
        """Update a specific configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def get_config_files(self) -> List[str]:
        """Get list of available config files"""
        config_dir = "config"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
            return []
        
        files = [f for f in os.listdir(config_dir) if f.endswith('.toml')]
        return sorted(files) if files else []
    
    def load_config_file(self, filename: str):
        """Load a specific config file"""
        if filename:
            self.config_file = os.path.join("config", filename)
            self.config = self.load_config()
    
    def create_config_from_template(self, name: str, template_config: Dict[str, Any] = None):
        """Create a new config file from template or current config"""
        try:
            if not name.endswith('.toml'):
                name += '.toml'
            
            config_path = os.path.join("config", name)
            config_to_save = template_config or self.config
            
            os.makedirs("config", exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                toml.dump(config_to_save, f)
            
            return True
        except Exception as e:
            print(f"Error creating config file: {e}")
            return False
    
    # Convenience methods for accessing config values
    @property
    def api_model(self) -> str:
        return self.config.get("api", {}).get("model", "google/gemini-2.0-flash-001")
    
    @property
    def api_temperature(self) -> float:
        return self.config.get("api", {}).get("temperature", 0.3)
    
    @property
    def api_max_tokens(self) -> int:
        return self.config.get("api", {}).get("max_tokens", 1000000)
    
    @property
    def api_key(self) -> str:
        return self.config.get("api", {}).get("api_key", "")
    
    @property
    def paper_types(self) -> List[str]:
        return self.config.get("paper", {}).get("types", ["Agent/RL", "Interpretability", "Efficiency"])
    
    @property
    def csv_file(self) -> str:
        return self.config.get("paper", {}).get("csv_file", "papers.csv")
    
    @property
    def ui_theme(self) -> str:
        return self.config.get("ui", {}).get("theme", "soft")
    
    @property
    def chatbot_height(self) -> int:
        return self.config.get("ui", {}).get("chatbot_height", 500)
    
    @property
    def debug(self) -> bool:
        return self.config.get("ui", {}).get("debug", True) 