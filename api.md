# LosTea 前后端 API 设计

本文档用于约定 LosTea 前端与后端之间的 HTTP API。当前接口统一以 `/api` 为前缀，数据格式统一使用 JSON。

## 1. 通用约定

### 1.1 Base URL

本地开发：

```txt
http://127.0.0.1:8000
```

前端环境变量：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 1.2 请求头

普通 JSON 请求：

```http
Content-Type: application/json
```

需要登录态的请求：

```http
Authorization: Bearer <access_token>
```

### 1.3 成功响应

成功响应使用业务对象本身作为返回值，例如：

```json
{
  "id": 1,
  "email": "user@example.com"
}
```

### 1.4 错误响应

后端建议统一使用 FastAPI 默认错误结构：

```json
{
  "detail": "错误说明"
}
```

常用状态码：

| 状态码 | 含义 |
|---|---|
| 200 | 请求成功 |
| 400 | 请求参数错误或业务校验失败 |
| 401 | 未登录、登录过期、账号密码错误 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突，例如邮箱已注册 |
| 422 | FastAPI/Pydantic 参数校验失败 |
| 500 | 服务端异常 |

---

## 2. 认证模块 Auth

### 2.1 发送注册邮箱验证码

```http
POST /api/auth/send-code
Content-Type: application/json
```

#### 请求体

```json
{
  "email": "user@example.com"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| email | string | 是 | 用户邮箱 |

#### 成功响应

```json
{
  "message": "验证码已发送"
}
```

#### 可能错误

```json
{
  "detail": "邮箱格式不正确"
}
```

```json
{
  "detail": "该邮箱已注册"
}
```

```json
{
  "detail": "验证码发送过于频繁，请稍后再试"
}
```

---

### 2.2 注册

```http
POST /api/auth/register
Content-Type: application/json
```

#### 请求体

```json
{
  "email": "user@example.com",
  "password": "123456",
  "code": "123456"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| email | string | 是 | 用户邮箱 |
| password | string | 是 | 用户密码，建议至少 6 位 |
| code | string | 是 | 邮箱验证码 |

#### 成功响应

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxx",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user@example.com"
  }
}
```

#### 可能错误

```json
{
  "detail": "验证码错误或已过期"
}
```

```json
{
  "detail": "该邮箱已注册"
}
```

---

### 2.3 登录

```http
POST /api/auth/login
Content-Type: application/json
```

#### 请求体

```json
{
  "email": "user@example.com",
  "password": "123456"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| email | string | 是 | 用户邮箱 |
| password | string | 是 | 用户密码 |

#### 成功响应

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxx",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user@example.com"
  }
}
```

#### 可能错误

```json
{
  "detail": "邮箱或密码错误"
}
```

---

### 2.4 获取当前登录用户

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### 成功响应

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user@example.com"
}
```

#### 可能错误

```json
{
  "detail": "登录已失效，请重新登录"
}
```

---

## 3. AI Chat 模块

### 3.1 AI 问答

```http
POST /api/chat
Content-Type: application/json
```

#### 请求体

```json
{
  "message": "安顶山云雾茶有什么特色？",
  "history": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "你好，我是茶小泽。"
    }
  ]
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| message | string | 是 | 用户本轮问题 |
| history | array | 否 | 最近聊天上下文 |
| history[].role | string | 是 | `user` 或 `assistant` |
| history[].content | string | 是 | 消息内容 |

#### 成功响应

```json
{
  "reply": "安顶山云雾茶具有高山云雾环境孕育的清香口感……",
  "error": null
}
```

#### 降级响应

当大模型不可用但后端有兜底话术时，仍然返回 200：

```json
{
  "reply": "抱歉，茶小泽暂时连接大模型失败了……",
  "error": "AuthenticationError: ..."
}
```

---

## 4. 健康检查

### 4.1 根路径健康检查

```http
GET /
```

#### 成功响应

```json
{
  "status": "ok",
  "service": "LosTeaApi"
}
```

---

### 4.2 API 健康检查

```http
GET /api/health
```

#### 成功响应

```json
{
  "status": "ok",
  "service": "LosTeaApi"
}
```

---

## 5. 前端当前对接点

前端当前会调用以下接口：

| 页面/功能 | 方法 | 接口 |
|---|---|---|
| 注册页获取验证码 | POST | `/api/auth/send-code` |
| 注册页提交注册 | POST | `/api/auth/register` |
| 登录页提交登录 | POST | `/api/auth/login` |
| 获取当前用户 | GET | `/api/auth/me` |
| AI 客服 | POST | `/api/chat` |
| 健康检查 | GET | `/api/health` |

---

## 6. 前端 Token 存储约定

前端登录成功后会保存：

```txt
localStorage.losteapy_token
localStorage.losteapy_user
```

其中：

- `losteapy_token` 保存 JWT access token
- `losteapy_user` 保存用户基本信息 JSON

前端请求需要登录的接口时，会使用：

```http
Authorization: Bearer <localStorage.losteapy_token>
```
