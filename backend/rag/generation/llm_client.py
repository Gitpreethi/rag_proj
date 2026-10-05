import json
from typing import Any

import httpx

from config.settings import get_settings
from rag.prompting.system_prompt import SYSTEM_PROMPT_V1


class ReasoningLLM:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate(self, user_payload: dict[str, Any]) -> str:
        if not self.settings.llm_api_key and not self.settings.llm_base_url:
            return self._fallback_answer(user_payload)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_V1},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)},
        ]
        url = (self.settings.llm_base_url or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {self.settings.llm_api_key}", "Content-Type": "application/json"}
        body = {"model": self.settings.llm_model, "messages": messages, "temperature": 0.2}
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, headers=headers, json=body)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as exc:
            base = self._fallback_answer(user_payload)
            return base + f"\n\n[LLM unavailable: {exc}]"

    def _fallback_answer(self, payload: dict[str, Any]) -> str:
        evidence = payload.get("evidence", [])
        if not evidence:
            return (
                "No authoritative numerical requirement was found in the retrieved knowledge base. "
                "Ingest official NIDM/NDMA/MHA/NDRF documents and sync data to enable evidence-grounded reasoning."
            )
        lines = [
            "Evidence-grounded summary (LLM not configured):",
            "",
        ]
        for i, ev in enumerate(evidence[:8], start=1):
            meta = ev.get("metadata", {})
            lines.append(
                f"{i}. [{meta.get('authority', 'unknown')}] {meta.get('section', '')} — {ev.get('text', '')[:400]}"
            )
        lines.append("")
        lines.append(
            "Numerical material totals are omitted unless an official per-capita standard is present in structured data."
        )
        return "\n".join(lines)
