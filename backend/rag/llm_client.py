# rag/llm_client.py
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

from openai import OpenAI


@dataclass
class OpenAIConfig:
    """
    OpenAI LLM 호출 설정.

    Notes:
    - 기본은 Responses API 사용 (OpenAI 권장)
    - 필요 시 use_chat_completions=True로 Chat Completions 사용 가능
    """
    model: str = "gpt-4o-mini"          # 필요시 "gpt-5" 등으로 교체
    api_key: Optional[str] = None       # None이면 OPENAI_API_KEY 사용
    base_url: Optional[str] = None      # 프록시/게이트웨이 사용 시
    timeout: float = 60.0
    max_retries: int = 3
    retry_backoff_sec: float = 1.5      # 지수 backoff 기본 계수

    # API 선택
    use_chat_completions: bool = False  # False: Responses API, True: Chat Completions API

    # 생성 파라미터
    temperature: float = 0.2
    max_output_tokens: int = 1200

    # JSON 강제(가능한 경우)
    # - Chat Completions: response_format={"type":"json_object"}로 강제 가능
    # - Responses: 모델/SDK 동작에 따라 완전 강제는 어려워서 프롬프트로 강제 + 후처리 파싱 권장
    force_json: bool = True


class OpenAIClient:
    """
    OpenAI 기반 LLM 클라이언트.

    generate(system, user) -> str:
      - system: 시스템 프롬프트(규칙/역할)
      - user: 유저 프롬프트(입력 JSON + RAG 문서 snippets 등)
      - 반환: 모델이 생성한 텍스트(우리 파이프라인에선 JSON 문자열을 기대)
    """

    def __init__(self, config: OpenAIConfig):
        self.config = config
        api_key = config.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다. 환경변수 또는 config.api_key로 제공하세요.")

        kwargs: Dict[str, Any] = {"api_key": api_key}
        if config.base_url:
            kwargs["base_url"] = config.base_url

        # openai-python 클라이언트 생성
        self.client = OpenAI(**kwargs)

    def generate(self, system: str, user: str) -> str:
        """
        LLM 호출 (Responses API 기본).
        실패 시 재시도(backoff) 포함.
        """
        last_err: Optional[Exception] = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                if self.config.use_chat_completions:
                    return self._generate_chat_completions(system, user)
                return self._generate_responses(system, user)
            except Exception as e:
                last_err = e
                if attempt >= self.config.max_retries:
                    break
                sleep_s = self.config.retry_backoff_sec ** attempt
                time.sleep(sleep_s)

        raise RuntimeError(f"OpenAI 호출 실패 (retries={self.config.max_retries}). 마지막 에러: {last_err}") from last_err

    def _generate_responses(self, system: str, user: str) -> str:
        """
        Responses API (권장)
        - instructions에 system을 넣고
        - input에 user를 넣는 기본 패턴
        """
        resp = self.client.responses.create(
            model=self.config.model,
            instructions=system,
            input=user,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
            # Responses API에서 JSON을 '강제'하는 옵션은 상황에 따라 다를 수 있어
            # 우리는 프롬프트로 JSON-only를 강제하고 pipeline에서 JSON 파싱으로 검증함
            # (force_json은 여기서는 프롬프트 강제에 의존)
        )

        # openai-python은 편의로 output_text를 제공
        text = getattr(resp, "output_text", None)
        if not text:
            # 혹시 SDK 버전에 따라 output_text가 없을 때 대비
            # resp.output을 순회해 message content를 찾아본다.
            text = self._extract_text_from_responses(resp)

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Responses API 응답에서 텍스트를 추출하지 못했습니다.")

        return text

    def _generate_chat_completions(self, system: str, user: str) -> str:
        """
        Chat Completions API
        - response_format을 활용해 JSON 객체 출력 강제 가능
        """
        kwargs: Dict[str, Any] = dict(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
        )

        if self.config.force_json:
            # JSON mode/response_format 지원 시 JSON object 형태 강제
            kwargs["response_format"] = {"type": "json_object"}

        comp = self.client.chat.completions.create(**kwargs)

        content = comp.choices[0].message.content if comp.choices else None
        if not content or not content.strip():
            raise ValueError("Chat Completions 응답이 비어 있습니다.")
        return content

    @staticmethod
    def _extract_text_from_responses(resp: Any) -> str:
        """
        Responses API 응답 구조에서 텍스트 추출(보수적).
        SDK/모델에 따라 구조가 다를 수 있어 최대한 안전하게 처리.
        """
        # resp.output: list of items
        out = []
        output = getattr(resp, "output", None)
        if not output:
            return ""

        for item in output:
            if getattr(item, "type", None) == "message":
                content = getattr(item, "content", None) or []
                for c in content:
                    # content item에 text가 들어있는 케이스
                    text = getattr(c, "text", None)
                    if isinstance(text, str):
                        out.append(text)
                    # 일부 SDK는 c가 dict일 수 있음
                    if isinstance(c, dict):
                        t = c.get("text")
                        if isinstance(t, str):
                            out.append(t)

        return "\n".join(out).strip()