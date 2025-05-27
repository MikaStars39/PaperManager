import requests
import json
from typing import List, Dict, Optional

def call_openrouter(
    prompt: str, 
    api_key: str, 
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 10000000,
    conversation: List[Dict[str, str]] = None
) -> Optional[str]:

    if not conversation:
        conversation = []

    conversation.append({"role": "user", "content": prompt})

    """Call LLM API to get response"""
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
        content = result['choices'][0]['message']['content'].strip()
        conversation.append({"role": "assistant", "content": content})
        return conversation, content
            
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None, None

