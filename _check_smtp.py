import smtplib
import os
import sys
from pathlib import Path

# 手动加载 .env
env_path = Path(__file__).resolve().parent / '.env'
if env_path.exists():
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())

host = os.environ.get('SMTP_HOST', 'smtp.163.com')
port = int(os.environ.get('SMTP_PORT', '465'))
user = os.environ.get('SMTP_USER', '')
password = os.environ.get('SMTP_PASSWORD', '')

print(f'SMTP_HOST = {host}')
print(f'SMTP_PORT = {port}')
print(f'SMTP_USER = {user}')
print(f'SMTP_PASSWORD = {"***" + password[-4:] if password else "(空)"}')
print(f'SMTP_PASSWORD 长度 = {len(password)}')

if not password:
    print('SMTP_PASSWORD 为空，请先去 163 邮箱开启 SMTP 服务并生成授权码')
    sys.exit(1)

try:
    if port == 465:
        print('尝试 SMTP_SSL 连接…')
        smtp = smtplib.SMTP_SSL(host, port, timeout=15)
    else:
        print('尝试 SMTP STARTTLS 连接…')
        smtp = smtplib.SMTP(host, port, timeout=15)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
    smtp.set_debuglevel(1)

    print('尝试登录…')
    smtp.login(user, password)
    print('登录成功')
    smtp.quit()
except smtplib.SMTPAuthenticationError as e:
    print('认证失败:', e.smtp_code, e.smtp_error)
except Exception as e:
    print('异常:', type(e).__name__, e)
