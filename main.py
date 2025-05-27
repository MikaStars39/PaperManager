import argparse
from PaperManager.ui import create_paper_manager_ui
from PaperManager.config import ConfigManager

def main():
    """Main function to launch the Paper Manager UI"""
    parser = argparse.ArgumentParser(description="Paper Manager UI")
    parser.add_argument("--config", default="config/base.toml", help="Configuration file to load")
    args = parser.parse_args()
    
    print(f"🚀 Starting Paper Manager UI with config: {args.config}")
    
    # Initialize configuration manager with the specified config file
    config_manager = ConfigManager(args.config)
    
    # Create the interface with the config
    interface = create_paper_manager_ui(config_manager)
    
    # Launch the interface with minimal settings
    try:
        interface.launch(
            share=True,            # Enable share to avoid localhost issues
            debug=False,           
            show_error=True,       
            quiet=False            
        )
    except Exception as e:
        print(f"Error launching interface: {e}")
        # Fallback to basic launch
        interface.launch()

if __name__ == "__main__":
    main()
