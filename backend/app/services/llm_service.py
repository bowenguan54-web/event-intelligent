"""
LLM 服务层 —— 封装 DeepSeek / OpenAI 兼容 API 调用
使用 httpx 直接调用 /v1/chat/completions，支持同步 & 流式输出
"""
import httpx
import json
import logging
from typing import List, Dict, Optional, AsyncGenerator

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 基础请求参数
# ---------------------------------------------------------------------------

def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
    }


def _api_url() -> str:
    base = settings.LLM_API_BASE_URL.rstrip("/")
    return f"{base}/v1/chat/completions"


# ---------------------------------------------------------------------------
# 非流式调用
# ---------------------------------------------------------------------------

async def chat_completion(
    messages: List[Dict[str, str]],
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    调用 LLM 获取完整回答（非流式）

    参数:
        messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
        model: 模型名称，默认使用 settings.LLM_MODEL_NAME
        temperature: 采样温度
        max_tokens: 最大生成 token 数

    返回:
        LLM 生成的文本内容
    """
    if not settings.LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY 未配置，请在 .env 中设置")

    payload = {
        "model": model or settings.LLM_MODEL_NAME,
        "messages": messages,
        "temperature": temperature if temperature is not None else settings.LLM_TEMPERATURE,
        "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120.0, verify=False, trust_env=False) as client:
        try:
            resp = await client.post(_api_url(), headers=_headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            logger.info(f"LLM 调用成功 | model={payload['model']} | tokens={data.get('usage', {})}")
            return content
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API 错误: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"LLM API 调用失败: {e.response.status_code}")
        except Exception as e:
            logger.error(f"LLM 调用异常: {type(e).__name__}: {e}")
            raise RuntimeError(f"LLM 调用异常: {type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# 流式调用（SSE）
# ---------------------------------------------------------------------------

async def chat_completion_stream(
    messages: List[Dict[str, str]],
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    """
    流式调用 LLM，逐 token 返回内容

    用法:
        async for chunk in chat_completion_stream(messages):
            print(chunk, end="")
    """
    if not settings.LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY 未配置，请在 .env 中设置")

    payload = {
        "model": model or settings.LLM_MODEL_NAME,
        "messages": messages,
        "temperature": temperature if temperature is not None else settings.LLM_TEMPERATURE,
        "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120.0, verify=False, trust_env=False) as client:
        try:
            async with client.stream(
                "POST", _api_url(), headers=_headers(), json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM 流式 API 错误: {e.response.status_code}")
            raise RuntimeError(f"LLM API 调用失败: {e.response.status_code}")
        except Exception as e:
            logger.error(f"LLM 流式调用异常: {type(e).__name__}: {e}")
            raise RuntimeError(f"LLM 流式调用异常: {type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# 便捷方法：单轮对话
# ---------------------------------------------------------------------------

async def generate_text(
    prompt: str,
    *,
    system_prompt: str = "你是一个专业的会议助手AI。",
    **kwargs,
) -> str:
    """单轮对话快捷方法"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    return await chat_completion(messages, **kwargs)


async def generate_text_stream(
    prompt: str,
    *,
    system_prompt: str = "你是一个专业的会议助手AI。",
    **kwargs,
) -> AsyncGenerator[str, None]:
    """单轮流式对话快捷方法"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    async for chunk in chat_completion_stream(messages, **kwargs):
        yield chunk
