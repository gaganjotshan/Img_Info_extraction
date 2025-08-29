import json
import requests
from typing import Generator

def stream_response(model: str, prompt: str, images=None, **kwargs) -> Generator[str, None, None]:
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        **kwargs
    }

    if images is not None:
        payload["images"] = [images]

    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode('utf-8'))
                if 'response' in chunk:
                    yield chunk['response']
                if chunk.get('done', False):
                    break
            except json.JSONDecodeError:
                continue