import gradio as gr
from .agent import PaperManager
from .config import Config

class PaperManagerUI:
    def __init__(self, config: Config):
        self.config = config
        # 在初始化时就创建PaperManager
        self.paper_manager = PaperManager(config=self.config)
    
    def clear_chat_history(self):
        """Clear chat history"""
        self.paper_manager.conversation = []
        return []

    def chat_with_manager_stream(self, message: str, history):
        """Handle streaming chat with the PaperManager"""
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

    def create_interface(self):
        """Create the simplified Gradio interface"""
        with gr.Blocks(title="Paper Manager", theme=self.config.ui_theme) as interface:
            gr.Markdown("# 📚 Paper Manager")
            gr.Markdown("Manage your research papers with AI assistance")
            
            # Display current configuration info
            gr.Markdown(f"""
            **Current Configuration:**
            - Model: `{self.config.api_model}`
            - CSV File: `{self.config.csv_file}`
            - Paper Types: `{', '.join(self.config.paper_types)}`
            """)
            
            # Main Chat Interface
            chatbot = gr.Chatbot(
                height=self.config.chatbot_height,
                label="Paper Manager Assistant"
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    label="Message",
                    placeholder="Type your message here... (e.g., 'Add this paper: https://arxiv.org/abs/2210.01117')",
                    scale=4,
                    max_lines=3
                )
                with gr.Column(scale=1):
                    send_btn = gr.Button("Send", variant="primary", size="sm")
                    clear_btn = gr.Button("Clear History", variant="secondary", size="sm")
            
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
        
        return interface

def create_paper_manager_ui(config: Config):
    """Create and return the PaperManager UI"""
    ui = PaperManagerUI(config)
    return ui.create_interface()
