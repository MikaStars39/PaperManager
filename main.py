import argparse
from PaperManager.ui import create_paper_manager_ui
from PaperManager.config import Config

def main():
    """Main function to launch the Paper Manager UI"""
    parser = argparse.ArgumentParser(description="Paper Manager UI")
    parser.add_argument("--config", default="config/base.toml", help="Configuration file to load")
    args = parser.parse_args()
    
    print(f"🚀 Starting Paper Manager UI with config: {args.config}")
    
    # Initialize configuration with the specified config file
    config = Config.load_from_file(args.config)
    
    # Validate critical settings
    if not config.api_key:
        print("⚠️  Warning: No API key found in config. Please add your API key to the config file.")
    
    print(f"📊 Model: {config.api_model}")
    print(f"📁 CSV File: {config.csv_file}")
    print(f"🔑 API Key: {'✅ Set' if config.api_key else '❌ Missing'}")
    
    # Create the interface with the config
    interface = create_paper_manager_ui(config)
    
    # Enable queue for streaming support
    interface.queue()
    
    # Launch the interface with minimal settings
    try:
        interface.launch(debug=config.debug, show_error=True, quiet=False)
    except Exception as e:
        print(f"Error launching interface: {e}")
        # Fallback to basic launch
        interface.queue()  # Make sure queue is enabled in fallback too
        interface.launch()

if __name__ == "__main__":
    main()
