import gradio as gr
import os
from .agent import PaperManager
from .config import ConfigManager

class PaperManagerUI:
    def __init__(self, config_manager=None):
        self.paper_manager = None
        self.chat_history = []
        self.config_manager = config_manager or ConfigManager()
    
    def initialize_manager(self, csv_path: str, api_key: str) -> str:
        """Initialize the PaperManager with given CSV path and API key"""
        try:
            if not csv_path.strip():
                csv_path = self.config_manager.csv_file
            
            if not api_key.strip():
                api_key = self.config_manager.api_key
                if not api_key:
                    return "❌ Please provide an API key"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(csv_path) if os.path.dirname(csv_path) else '.', exist_ok=True)
            
            # Initialize PaperManager with only the parameters it accepts
            self.paper_manager = PaperManager(
                csv_file=csv_path,
                api_key=api_key
            )
            
            return f"✅ Paper Manager initialized successfully!\n📁 CSV file: {csv_path}\n🤖 Model: {self.config_manager.api_model}"
            
        except Exception as e:
            return f"❌ Error initializing Paper Manager: {str(e)}"
    
    def clear_chat_history(self):
        """Clear chat history"""
        if self.paper_manager:
            self.paper_manager.conversation = []
        return []
    
    def update_config_and_reinit(self, model, temperature, max_tokens, api_key, csv_path):
        """Update configuration and reinitialize manager"""
        try:
            # Update config
            self.config_manager.update_config("api", "model", model)
            self.config_manager.update_config("api", "temperature", temperature)
            self.config_manager.update_config("api", "max_tokens", max_tokens)
            self.config_manager.update_config("api", "api_key", api_key)
            self.config_manager.update_config("paper", "csv_file", csv_path)
            
            # Reinitialize manager if it exists
            if self.paper_manager:
                self.paper_manager = PaperManager(
                    config_manager=self.config_manager,
                    csv_file=csv_path,
                    api_key=api_key
                )
                return "✅ Configuration updated and manager reinitialized!"
            else:
                return "✅ Configuration updated! Please initialize the manager."
        except Exception as e:
            return f"❌ Error updating configuration: {str(e)}"
    
    def save_config_as(self, config_name):
        """Save current configuration with a new name"""
        try:
            if not config_name.strip():
                return "❌ Please provide a configuration name"
            
            if not config_name.endswith('.toml'):
                config_name += '.toml'
            
            # Create config directory if it doesn't exist
            config_dir = "config"
            os.makedirs(config_dir, exist_ok=True)
            
            # Save config with new name
            old_config_file = self.config_manager.config_file
            self.config_manager.config_file = os.path.join(config_dir, config_name)
            
            if self.config_manager.save_config():
                return f"✅ Configuration saved as {config_name}"
            else:
                self.config_manager.config_file = old_config_file
                return f"❌ Failed to save configuration as {config_name}"
        except Exception as e:
            return f"❌ Error saving configuration: {str(e)}"
    
    def load_config_file(self, config_file):
        """Load a specific configuration file"""
        try:
            if not config_file:
                return "❌ Please select a configuration file", "", 0.3, 1000000, "", "papers.csv"
            
            self.config_manager.load_config_file(config_file)
            
            return (
                f"✅ Loaded configuration: {config_file}",
                self.config_manager.api_model,
                self.config_manager.api_temperature,
                self.config_manager.api_max_tokens,
                self.config_manager.api_key,
                self.config_manager.csv_file
            )
        except Exception as e:
            return f"❌ Error loading configuration: {str(e)}", "", 0.3, 1000000, "", "papers.csv"
    
    def get_available_configs(self):
        """Get list of available configuration files"""
        return self.config_manager.get_config_files()

    def chat_with_manager_stream(self, message: str, history):
        """Handle streaming chat with the PaperManager"""
        if not self.paper_manager:
            history.append([message, "❌ Please initialize the Paper Manager first in the Settings tab."])
            yield "", history
            return
        
        if not message.strip():
            yield "", history
            return
        
        try:
            # Add user message to history immediately
            history.append([message, ""])
            yield "", history
            
            # Stream the response
            response = ""
            for chunk in self.paper_manager.chat_stream(message):
                response += chunk
                # Update the last message in history with the accumulated response
                history[-1][1] = response
                yield "", history
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            if history and history[-1][0] == message:
                history[-1][1] = error_msg
            else:
                history.append([message, error_msg])
            yield "", history

    def chat_with_manager(self, message: str, history):
        """Handle chat with the PaperManager (non-streaming fallback)"""
        if not self.paper_manager:
            history.append([message, "❌ Please initialize the Paper Manager first in the Settings tab."])
            return "", history
        
        if not message.strip():
            return "", history
        
        try:
            # Get response from PaperManager using the chat method
            response = self.paper_manager.chat(message)
            
            # Add to history
            history.append([message, response])
            
            return "", history
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            history.append([message, error_msg])
            return "", history
    
    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(title="Paper Manager") as interface:
            gr.Markdown("# 📚 Paper Manager")
            gr.Markdown("Manage your research papers with AI assistance")
            
            with gr.Tabs():
                # Main Chat Tab
                with gr.TabItem("💬 Chat"):
                    gr.Markdown("## 💬 Chat with AI Assistant")              
                    chatbot = gr.Chatbot(
                        height=self.config_manager.chatbot_height,
                        label="Paper Manager Assistant"
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here...",
                            scale=4,
                            max_lines=3  # Limit input height
                        )
                        with gr.Column(scale=1):
                            send_btn = gr.Button("Send", variant="primary", size="sm")
                            clear_btn = gr.Button("Clear History", variant="secondary", size="sm")
                
                # Settings Tab
                with gr.TabItem("⚙️ Settings"):
                    gr.Markdown("## ⚙️ Configuration")
                    
                    with gr.Row():
                        # Left Column - Basic Settings
                        with gr.Column():
                            gr.Markdown("### Basic Settings")
                            csv_path_input = gr.Textbox(
                                label="CSV File Path",
                                value=self.config_manager.csv_file,
                                placeholder="papers.csv"
                            )
                            api_key_input = gr.Textbox(
                                label="API Key",
                                value=self.config_manager.api_key,
                                placeholder="Enter your API key",
                                type="password"
                            )
                            
                            with gr.Row():
                                init_btn = gr.Button("Initialize", variant="primary")
                                reinit_btn = gr.Button("Re-initialize", variant="secondary")
                        
                        # Right Column - Advanced Settings
                        with gr.Column():
                            gr.Markdown("### Advanced Settings")
                            model_input = gr.Textbox(
                                label="Model",
                                value=self.config_manager.api_model,
                                placeholder="google/gemini-2.0-flash-001"
                            )
                            temperature_input = gr.Slider(
                                label="Temperature",
                                minimum=0.0,
                                maximum=2.0,
                                step=0.1,
                                value=self.config_manager.api_temperature
                            )
                            max_tokens_input = gr.Number(
                                label="Max Tokens",
                                value=self.config_manager.api_max_tokens,
                                minimum=1,
                                maximum=10000000
                            )
                            
                            update_btn = gr.Button("Update & Apply", variant="primary")
                    
                    # Configuration Management Section
                    gr.Markdown("### Configuration Management")
                    with gr.Row():
                        with gr.Column():
                            config_dropdown = gr.Dropdown(
                                label="Available Configurations",
                                choices=self.get_available_configs(),
                                value=None
                            )
                            load_config_btn = gr.Button("Load Configuration", variant="secondary")
                        
                        with gr.Column():
                            new_config_name = gr.Textbox(
                                label="New Configuration Name",
                                placeholder="my_config.toml"
                            )
                            save_config_btn = gr.Button("Save As New Config", variant="secondary")
                    
                    # Status Display
                    init_status = gr.Textbox(
                        label="Status",
                        value="Not initialized",
                        interactive=False,
                        lines=3
                    )
            
            # Event handlers
            send_btn.click(
                fn=self.chat_with_manager_stream,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot]
            )
            
            msg_input.submit(
                fn=self.chat_with_manager_stream,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot]
            )
            
            clear_btn.click(
                fn=self.clear_chat_history,
                outputs=chatbot
            )
            
            init_btn.click(
                fn=self.initialize_manager,
                inputs=[csv_path_input, api_key_input],
                outputs=init_status
            )
            
            reinit_btn.click(
                fn=self.initialize_manager,
                inputs=[csv_path_input, api_key_input],
                outputs=init_status
            )
            
            update_btn.click(
                fn=self.update_config_and_reinit,
                inputs=[model_input, temperature_input, max_tokens_input, api_key_input, csv_path_input],
                outputs=init_status
            )
            
            save_config_btn.click(
                fn=self.save_config_as,
                inputs=new_config_name,
                outputs=init_status
            )
            
            load_config_btn.click(
                fn=self.load_config_file,
                inputs=config_dropdown,
                outputs=[init_status, model_input, temperature_input, max_tokens_input, api_key_input, csv_path_input]
            )
            
            # Refresh config dropdown when tab is opened
            def refresh_configs():
                return gr.Dropdown(choices=self.get_available_configs())
            
            # Update dropdown choices when interface loads
            interface.load(
                fn=lambda: self.get_available_configs(),
                outputs=config_dropdown
            )
        
        return interface

def create_paper_manager_ui(config_manager=None):
    """Create and return the PaperManager UI"""
    ui = PaperManagerUI(config_manager)
    return ui.create_interface()
