import requests
import json
from typing import List, Dict, Optional, Generator

def call_openrouter_stream(
    prompt: str, 
    api_key: str, 
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 10000000,
    conversation: List[Dict[str, str]] = None
) -> Generator[str, None, None]:
    """Call LLM API to get streaming response"""
    if not conversation:
        conversation = []

    conversation.append({"role": "user", "content": prompt})

    if not api_key:
        yield "Warning: No API key provided. Using fallback method."
        return
        
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": conversation,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            },
            stream=True
        )
        
        buffer = ""
        full_content = ""
        
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                buffer += chunk
                while True:
                    try:
                        # Find the next complete SSE line
                        line_end = buffer.find('\n')
                        if line_end == -1:
                            break

                        line = buffer[:line_end].strip()
                        buffer = buffer[line_end + 1:]

                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                # Add the complete response to conversation
                                conversation.append({"role": "assistant", "content": full_content})
                                return

                            try:
                                data_obj = json.loads(data)
                                content = data_obj["choices"][0]["delta"].get("content")
                                if content:
                                    full_content += content
                                    yield content
                            except json.JSONDecodeError:
                                pass
                    except Exception:
                        break
            
    except Exception as e:
        yield f"Error calling API: {str(e)}"

# Keep the original function for backward compatibility
def call_openrouter(
    prompt: str, 
    api_key: str, 
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 10000000,
    conversation: List[Dict[str, str]] = None
) -> Optional[str]:
    """Call LLM API to get response (non-streaming version)"""
    if not conversation:
        conversation = []

    conversation.append({"role": "user", "content": prompt})

    if not api_key:
        print("Warning: No API key provided. Using fallback method.")
        return None, None
        
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": model,
                "messages": conversation,
                "temperature": temperature,
                "max_tokens": max_tokens
            })
        )
        
        result = response.json()
        print("The result is", result)
        content = result['choices'][0]['message']['content'].strip()
        conversation.append({"role": "assistant", "content": content})
        return conversation, content
            
    except Exception as e:
        print(f"Error calling API: {str(e)}")
        return None, None

