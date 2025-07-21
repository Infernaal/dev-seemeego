from openai import OpenAI
from dotenv import load_dotenv
import os
import random

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_prompt() -> str:
    user_prompt = """
    You are a creative AI that generates short, weird, and hyper-viral video ideas for TikTok-style AI tools like Veo, Seeme, Kling, Runway, or Pika.

    🎯 Your goal:  
    Describe one 8–10 second video scene that feels like an iconic TikTok clip — something so weird, funny, or visually crazy that people instantly want to remix, react, or repost it.

    ✅ Your scene must:
    - Start with something absurd, shocking, or hilarious **in the first second**
    - Be based on **one bold, scroll-stopping idea**
    - Feature a real or stylized human, animal, object, or creature doing something strange, surreal, ironic, or challenge-worthy
    - Vary the type of main character. Don’t always use humans — include animals, creatures, and weird objects as central characters too.
    - Feel like it could be part of a trend, POV format, filter effect, or "WTF just happened" moment
    - Be emotionally loud: chaotic, cringe, cool, aesthetic, or ridiculous
    - Be extremely simple, visual, and remixable — like real TikTok trends are
    - 🔴 Keep it simple: **Don’t stack more than one surreal transformation** (e.g. no A → B → C → glitch). Use **one clear, bold twist** per scene.
    - Avoid overly cute or safe content (no kiddie pool puppies unless they rap in autotune)
    - 🔴 Do **not** mix radically different visual styles — e.g. **don’t put cartoon characters in photorealistic settings**, and **don’t add animated effects to realistic food, people, or animals**. Stick to a consistent visual world.

    📌 Examples of viral energy:
    - A guy in a suit eats spaghetti with VR goggles on — screams as if he's on a rollercoaster  
    - A grandma raps the lyrics to a trap song while making dumplings  
    - A guy opens a microwave and there's a tiny disco rave happening inside  
    - A cat jumps, freeze-frames mid-air, and turns into a Minecraft skin  
    - A fashion model gets smacked by a baguette in perfect slo-mo, then poses like nothing happened  
    - A girl does a thirst-trap transition, but it cuts to a lizard doing the same move

    ✍️ Output:  
    Write one vivid 8–10 sec scene description in continuous, natural language. No inner commentary, just the visual idea.  
    End with: **Visual style: [your chosen style]**

    Now generate one weird, wild, TikTok-style video scene that could go viral.
    """


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": user_prompt}
        ],
    )

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise ValueError(f"Invalid response from OpenAI: {response}")

    return content