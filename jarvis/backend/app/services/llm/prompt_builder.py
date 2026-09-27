from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.models.memory_entry import MemoryEntry
from app.models.message import Message

BASE_SYSTEM_PROMPT = """You are Jarvis, a highly capable, articulate, and thoughtful local AI assistant running entirely on the user's local machine.
You have no external cloud dependencies and operate with full local privacy.

System Context:
- Current UTC Time: {current_time}
- Persona: Helpful, precise, conversational, and direct.

Behavioral Guidelines:
1. Provide accurate, clear, and direct answers.
2. If code is requested, provide clean, idiomatic, and modern code with syntax highlighting.
3. Keep responses conversational when spoken or voice mode is enabled, while remaining substantive.
4. Utilize retrieved user memory facts to personalize responses seamlessly.
{memory_context}
"""

class PromptBuilder:
    @staticmethod
    def build_system_prompt(memory_entries: Optional[List[MemoryEntry]] = None) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        memory_str = ""
        if memory_entries:
            memory_lines = [f"- {m.key}: {m.value}" for m in memory_entries if m.key and m.value]
            if memory_lines:
                memory_str = "\nLong-Term User Memory:\n" + "\n".join(memory_lines)

        return BASE_SYSTEM_PROMPT.format(
            current_time=now_str,
            memory_context=memory_str,
        ).strip()

    @staticmethod
    def build_messages(
        conversation_history: List[Message],
        user_message: str,
        system_prompt: str,
        max_history_tokens: int = 4000,
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

        trimmed_history = PromptBuilder.truncate_history(conversation_history, max_history_tokens)
        for msg in trimmed_history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": user_message})
        return messages

    @staticmethod
    def truncate_history(history: List[Message], max_tokens: int = 4000) -> List[Message]:
        estimated_chars = max_tokens * 4
        total_chars = sum(len(m.content) for m in history)

        if total_chars <= estimated_chars:
            return history

        retained: List[Message] = []
        running_chars = 0
        for msg in reversed(history):
            msg_chars = len(msg.content)
            if running_chars + msg_chars > estimated_chars:
                break
            retained.insert(0, msg)
            running_chars += msg_chars

        return retained
