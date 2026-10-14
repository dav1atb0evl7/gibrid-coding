from app.config.settings import get_settings


class AIAssistant:
    """Future Gemini integration boundary; pricing is never represented as a quote."""

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def answer(self, question: str, language: str = "en") -> str:
        del question
        messages = {
            "en": "Our team can help with that. Send a project request and a specialist will follow up. Pricing is confirmed by our team after reviewing the requirements.",
            "ru": "Наша команда поможет вам. Отправьте заявку, и специалист свяжется с вами. Стоимость подтверждается после изучения требований.",
            "uz": "Jamoamiz sizga yordam beradi. So'rov yuboring, mutaxassisimiz siz bilan bog'lanadi. Narx talablar ko'rib chiqilgandan so'ng tasdiqlanadi.",
        }
        return messages.get(language, messages["en"])
