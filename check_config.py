from app.config import get_settings
s = get_settings()
print('has_deepseek_key=', bool(s.deepseek_api_key))
print('base_url=', s.deepseek_base_url)
print('model=', s.deepseek_model)
print('origins=', s.cors_origins)
