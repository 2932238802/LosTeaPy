from pathlib import Path
from app.config import get_settings
from app.llm_client import get_llm_client
from app.prompt_loader import load_system_prompt
from app.chat_service import build_extra_kwargs

s = get_settings()
print('prompt_path=', s.prompt_path)
print('prompt_exists=', Path(s.prompt_path).exists())
print('prompt_len=', len(load_system_prompt()))
print('has_deepseek_key=', bool(s.deepseek_api_key))
print('key_prefix=', s.deepseek_api_key[:8] if s.deepseek_api_key else '')
print('base_url=', s.deepseek_base_url)
print('model=', s.deepseek_model)
print('reasoning_effort=', s.reasoning_effort)
print('thinking_enabled=', s.thinking_enabled)
print('extra_kwargs=', build_extra_kwargs())

client = get_llm_client()
try:
    resp = client.chat.completions.create(
        model=s.deepseek_model,
        messages=[
            {'role': 'system', 'content': '你是一个简洁的中文助手'},
            {'role': 'user', 'content': '只回复两个字：你好'},
        ],
        temperature=0.1,
        stream=False,
        **build_extra_kwargs(),
    )
    print('reply=', resp.choices[0].message.content)
except Exception as e:
    print('error_type=', type(e).__name__)
    print('error=', repr(e))
