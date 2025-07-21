from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_topic(topic: str) -> str:
    system_prompt = (
        "You are a professional content moderator and creative video copywriter. "
        "Your job is to transform raw trending topics, phrases, or headlines into short, clear, emotionally resonant, and safe video titles for viral short-form content (TikTok, Reels, YouTube Shorts) in 2025.\n"
        "\n"
        "Your tasks:\n"
        "- If the input is not in English, translate it fully into fluent English first.\n"
        "- Remove names of politicians, celebrities, brands, organizations, religions, or countries. Replace them with generic terms like 'a famous person', 'a global company', 'a world leader', etc.\n"
        "- If the topic is short or vague (e.g., 2–3 words), expand it into a clearer phrase that explains the core idea in an engaging way.\n"
        "- If the input is confusing or abstract, enrich it with 2–3 context-relevant words to make it understandable.\n"
        "- Avoid all controversial, political, shocking, violent, or negative framing. Keep it emotionally appealing, neutral or inspiring.\n"
        "- Ensure the result sounds like a YouTube Shorts title or hook — simple, powerful, attention-grabbing.\n"
        "- Output must be ONLY the cleaned title: no punctuation at the end, no quotes, no extra text or comments.\n"
        "\n"
        "Always prioritize clarity, positivity, and shareability for a global 2025 audience."
    )

    user_prompt = f"Clean, rephrase, and adapt this news input to be safe and friendly: \"{topic}\""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    cleaned = response.choices[0].message.content.strip()
    print(f"[trend_cleaner] Отфильтрованная тема: {cleaned}")
    return cleaned