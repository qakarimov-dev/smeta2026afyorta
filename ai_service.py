import logging
from typing import Dict, List, Optional
import config
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ConversationManager:
    """Foydalanuvchilar kontekst tarixini xotirada boshqarish"""

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self._history: Dict[int, List[Dict[str, str]]] = {}

    def get_history(self, chat_id: int) -> List[Dict[str, str]]:
        return self._history.get(chat_id, [])

    def add_message(self, chat_id: int, role: str, content: str):
        if chat_id not in self._history:
            self._history[chat_id] = []
        self._history[chat_id].append({"role": role, "content": content})
        # Tarix uzunligini cheklash
        if len(self._history[chat_id]) > self.max_history * 2:
            self._history[chat_id] = self._history[chat_id][-self.max_history * 2 :]

    def clear(self, chat_id: int):
        if chat_id in self._history:
            self._history[chat_id] = []


conversation_manager = ConversationManager(max_history=config.MAX_HISTORY_MESSAGES)


class AIService:
    """Gemini va OpenAI bilan ishlovchi bosh muhandis AI xizmati"""

    def __init__(self):
        self.provider = config.AI_PROVIDER
        self.model = config.AI_MODEL
        self._init_client()

    def _init_client(self):
        self.gemini_client = None
        self.openai_client = None

        if self.provider == "gemini":
            if not config.GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY topilmadi!")
                return
            try:
                # Yangi google-genai kutubxonasini tekshirish
                from google import genai

                self.gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
                self.gemini_mode = "genai_sdk"
                logger.info("Google GenAI SDK (yangi) muvaffaqiyatli ishga tushirildi.")
            except ImportError:
                try:
                    # Eski google-generativeai kutubxonasiga fallback
                    import google.generativeai as legacy_genai

                    legacy_genai.configure(api_key=config.GEMINI_API_KEY)
                    self.gemini_client = legacy_genai.GenerativeModel(
                        model_name=self.model,
                        system_instruction=SYSTEM_PROMPT,
                    )
                    self.gemini_mode = "legacy_genai"
                    logger.info("google-generativeai (eski) orqali ishga tushirildi.")
                except ImportError:
                    logger.error("Hech qanday Google Gemini kutubxonasi o'rnatilmagan.")
                    self.gemini_mode = None

        elif self.provider == "openai":
            if not config.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY topilmadi!")
                return
            try:
                from openai import AsyncOpenAI

                self.openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
                logger.info("OpenAI SDK muvaffaqiyatli ishga tushirildi.")
            except ImportError:
                logger.error("OpenAI kutubxonasi o'rnatilmagan.")

    async def get_response(self, chat_id: int, user_message: str) -> str:
        """Foydalanuvchi xabariga bosh muhandis javobini shakllantirish"""
        errors = config.validate_config()
        if errors:
            return (
                "⚠️ **Tizim sozlamalarida xatolik aniqlandi:**\n\n"
                + "\n".join(f"• {e}" for e in errors)
                + "\n\nIltimos, loyiha ildizidagi `.env` faylini to'g'ri to'ldiring."
            )

        # Tarixni olish
        history = conversation_manager.get_history(chat_id)

        try:
            if self.provider == "gemini":
                reply = await self._call_gemini(history, user_message)
            elif self.provider == "openai":
                reply = await self._call_openai(history, user_message)
            else:
                return f"⚠️ Noma'lum provayder: {self.provider}"

            # Tarixga qo'shish
            conversation_manager.add_message(chat_id, "user", user_message)
            conversation_manager.add_message(chat_id, "model", reply)
            return reply

        except Exception as e:
            logger.exception("AI xizmatida xatolik yuz berdi:")
            return (
                f"⚠️ **Muhandislik hisob-kitobida xatolik yuz berdi:**\n"
                f"`{str(e)}`\n\n"
                f"Iltimos, qaytadan urinib ko'ring yoki parametrlar to'g'riligini tekshiring."
            )

    async def _call_gemini(self, history: List[Dict[str, str]], new_message: str) -> str:
        if not self.gemini_client:
            self._init_client()
            if not self.gemini_client:
                raise RuntimeError("Gemini mijozini ishga tushirib bo'lmadi. API kalitini tekshiring.")

        if getattr(self, "gemini_mode", "") == "genai_sdk":
            from google.genai import types

            # Contents ro'yxatini shakllantirish
            contents = []
            for item in history:
                role = "user" if item["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=item["content"])],
                    )
                )
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=new_message)],
                )
            )

            # Yangi Gemini SDK orqali chaqirish
            import asyncio

            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.gemini_client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,
                    ),
                ),
            )
            return response.text

        elif getattr(self, "gemini_mode", "") == "legacy_genai":
            # Eski google.generativeai orqali
            import asyncio

            messages = []
            for item in history:
                role = "user" if item["role"] == "user" else "model"
                messages.append({"role": role, "parts": [item["content"]]})
            messages.append({"role": "user", "parts": [new_message]})

            loop = asyncio.get_running_loop()
            chat = self.gemini_client.start_chat(history=messages[:-1])
            response = await loop.run_in_executor(
                None, lambda: chat.send_message(new_message)
            )
            return response.text
        else:
            raise RuntimeError("Gemini SDK topilmadi. 'pip install google-genai' qiling.")

    async def _call_openai(self, history: List[Dict[str, str]], new_message: str) -> str:
        if not self.openai_client:
            self._init_client()
            if not self.openai_client:
                raise RuntimeError("OpenAI mijozini ishga tushirib bo'lmadi. OPENAI_API_KEY tekshiring.")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for item in history:
            role = "user" if item["role"] == "user" else "assistant"
            messages.append({"role": role, "content": item["content"]})
        messages.append({"role": "user", "content": new_message})

        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content


ai_service = AIService()


def split_message(text: str, max_chars: int = 4000) -> List[str]:
    """
    Telegramning 4096 belgilik chegarasiga moslab matnni
    xatboshilar va qatorlar bo'yicha chiroyli qismlarga bo'lish.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    lines = text.split("\n")
    current_chunk = []
    current_length = 0

    for line in lines:
        line_len = len(line) + 1
        if current_length + line_len > max_chars:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_length = line_len
            else:
                # Agar bitta qatorning o'zi 4000 belgidan oshsa
                while len(line) > max_chars:
                    chunks.append(line[:max_chars])
                    line = line[max_chars:]
                if line:
                    current_chunk = [line]
                    current_length = len(line)
        else:
            current_chunk.append(line)
            current_length += line_len

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks
