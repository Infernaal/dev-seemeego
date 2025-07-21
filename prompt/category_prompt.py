import random
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CATEGORIES = [
    "Lifehacks and how-to tricks",
    "Motivation and mental hacks",
    "Fascinating facts and curious trivia",
    "Books that change how you think",
    "Money traps and financial habits",
    "Inventions and how things were created",
    "Psychology explained simply",
    "Time-saving productivity tips",
    "Cultural habits and global surprises",
    "Common myths and surprising truths",
    "Visual explainers (ELI5 style)",
    "Simple science for everyone",
    "AI trends and tech breakthroughs",
    "Fantasy logic and impossible ideas",
    "Tiny stories from real people",
    "Before vs After transformations",
    "What if… (short imagined scenarios)",
    "Odd but satisfying visuals",
    "Unusual jobs and hidden skills",
    "Mini experiments or physics in motion"
]

def get_custom_topic_from_category() -> str:
    category = random.choice(CATEGORIES)

    system_prompt = (
        "You are a creative strategist working for a viral video platform that uses AI to generate 10-second visual stories. "
        "Your job is to generate short, globally interesting, specific video **topic ideas** based on a given category.\n"
        "\n"
        "Each topic must:\n"
        "- Be engaging and understandable to people from any country or culture.\n"
        "- Be clearly worded in one short sentence (max 20 words).\n"
        "- Contain no names, brands, or country-specific references.\n"
        "- Be safe, friendly, and policy-compliant (no violence, politics, or sensitive content).\n"
        "- Avoid emojis, asterisks, special symbols, or formatting. Just clean natural English.\n"
        "- Be **specific and concrete**, not abstract. Avoid vague ideas or general slogans.\n"
        "- Be suitable for AI video generation — easy to imagine as a 10-second visual.\n"
        "\n"
        "Output ONLY the topic line, without any extra text, comments, or formatting."
    )

    user_prompt = (
        f"Suggest one short, globally appealing, clear video topic based on this category: '{category}'. "
        f"The topic must work visually in 10 seconds, interest people from any country, and be concrete, clean, and realistic."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise ValueError(f"Некорректный ответ от OpenAI: {response}")
    return content