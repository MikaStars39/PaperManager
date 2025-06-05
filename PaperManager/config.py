import toml
import os
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    # API settings
    api_model: str = "google/gemini-2.0-flash-001"
    api_temperature: float = 0.3
    api_max_tokens: int = 1000000
    api_key: str = ""
    
    # Paper settings
    paper_types: List[str] = None
    csv_file: str = "papers.csv"

    # HF settings
    hf_folder: str = "data"
    hf_repo_id: str = "MikaStars39/MikaDailyPaper"
    hf_token: str = ""
    
    # UI settings
    ui_theme: str = "soft"
    chatbot_height: int = 500
    debug: bool = True
    
    def __post_init__(self):
        if self.paper_types is None:
            self.paper_types = ["agent_rl", "interpretability", "efficiency"]
    
    @classmethod
    def load_from_file(cls, config_file: str = "config/base.toml") -> 'Config':
        """Load configuration from TOML file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = toml.load(f)
                
                # Flatten nested structure
                config_data = {}
                if 'api' in data:
                    config_data.update({f'api_{k}': v for k, v in data['api'].items()})
                if 'paper' in data:
                    config_data.update({f'paper_{k}' if k != 'types' else 'paper_types': v for k, v in data['paper'].items()})
                if 'hf' in data:
                    config_data.update({f'hf_{k}': v for k, v in data['hf'].items()})
                if 'ui' in data:
                    config_data.update({f'ui_{k}': v for k, v in data['ui'].items()})
                
                # Only include fields that exist in the dataclass
                valid_fields = {field.name for field in cls.__dataclass_fields__.values()}
                filtered_data = {k: v for k, v in config_data.items() if k in valid_fields}

                print(filtered_data)
                
                return cls(**filtered_data)
            else:
                return cls()
        except Exception as e:
            print(f"Error loading config: {e}")
            return cls()
    
    def save_to_file(self, config_file: str = "config/base.toml") -> bool:
        """Save configuration to TOML file"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # Convert to nested structure for TOML
            data = {
                "api": {
                    "model": self.api_model,
                    "temperature": self.api_temperature,
                    "max_tokens": self.api_max_tokens,
                    "api_key": self.api_key
                },
                "paper": {
                    "types": self.paper_types,
                    "csv_file": self.csv_file
                },
                "hf": {
                    "folder": self.hf_folder,
                    "repo_id": self.hf_repo_id,
                    "token": self.hf_token
                },
                "ui": {
                    "theme": self.ui_theme,
                    "chatbot_height": self.chatbot_height,
                    "debug": self.debug
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                toml.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def update_config(self, section: str, key: str, value):
        """Update a configuration value"""
        field_name = f"{section}_{key}" if section != "paper" or key != "types" else "paper_types"
        if hasattr(self, field_name):
            setattr(self, field_name, value)
    
    def get_config_files(self) -> List[str]:
        """Get list of available configuration files"""
        config_dir = "config"
        if not os.path.exists(config_dir):
            return []
        
        config_files = []
        for file in os.listdir(config_dir):
            if file.endswith('.toml'):
                config_files.append(os.path.join(config_dir, file))
        return config_files
    
    def load_config_file(self, config_file: str):
        """Load a specific configuration file and update current config"""
        loaded_config = self.load_from_file(config_file)
        
        # Update current instance with loaded values
        for field in self.__dataclass_fields__:
            setattr(self, field, getattr(loaded_config, field))
    
    def save_config(self) -> bool:
        """Save current configuration"""
        return self.save_to_file() 