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
                        height=500,
                        label="Paper Manager Assistant"
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here...",
                            scale=4
                        )
                        send_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Settings Tab
                with gr.TabItem("⚙️ Settings"):
                    gr.Markdown("## ⚙️ Configuration")
                    
                    with gr.Row():
                        with gr.Column():
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
                        
                        with gr.Column():
                            init_btn = gr.Button("Initialize", variant="primary")
                            reinit_btn = gr.Button("Re-initialize", variant="secondary")
                    
                    init_status = gr.Textbox(
                        label="Status",
                        value="Not initialized",
                        interactive=False
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
        
        return interface

def create_paper_manager_ui(config_manager=None):
    """Create and return the PaperManager UI"""
    ui = PaperManagerUI(config_manager)
    return ui.create_interface()
