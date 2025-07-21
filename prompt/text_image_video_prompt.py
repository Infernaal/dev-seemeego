from openai import OpenAI
from dotenv import load_dotenv
import os
import random

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_portrait_prompt() -> str:
    user_prompt = """
        You are a creative AI that generates **ultra-realistic and visually striking photo concepts** featuring humans, animals, surreal creatures, robots, or strange combinations of them (like a man with a banana peel on his head or a cyborg drinking boba tea). Your concepts will become scroll-stopping still images — later turned into short viral videos.

        🎯 Your goal:  
        Write one vivid, realistic image concept that feels like a **real photo** — something strange, stylish, emotional, cinematic, or funny enough to go viral.

        ✅ Your concept must:
        - Focus on a **realistic subject**: a person, humanoid, animal, robot, or unexpected combination  
        - Clearly describe their **appearance**: age, gender (if relevant), facial features, hairstyle, expression, clothing, accessories, and body language  
        - Always include a **distinct and atmospheric location or background** — e.g. a foggy mountain highway, an abandoned subway station, a neon-lit garden, a flooded basement, a desert motel, a rooftop at sunset, a smoke-filled nightclub, a retro diner, or a Tokyo alley in the rain  
        - Make the scene feel **frozen in time**, like a real photograph — candid or editorial  
        - Allow for **mood variation** — it can be funny, romantic, mysterious, weird, lonely, fashionable, or ironic  
        - Prefer **photorealism and cinematic realism**, but surreal concepts are welcome if grounded in strong physical detail and real-world lighting  

        🎨 Visual style (REQUIRED):
        You must ALWAYS end your sentence with the **following exact style tag list**. This is mandatory and should not be changed:

        *Cinematic, Photoshoot, Shot on 25mm lens, Depth of Field, Tilt Blur, Shutter Speed 1/1000, F/22, White Balance, 32k, Super-Resolution, Pro Photo RGB, Half rear Lighting, Backlight, Dramatic Lighting, Incandescent, Soft Lighting, Volumetric, Conte-Jour, Global Illumination, Screen Space Global Illumination, Scattering, Shadows, Rough, Shimmering, Lumen Reflections, Screen Space Reflections, Diffraction Grading, Chromatic Aberration, GB Displacement, Scan Lines, Ambient Occlusion, Anti-Aliasing, FKAA, TXAA, RTX, SSAO, OpenGL-Shader’s, Post Processing, Post-Production, Cell Shading, Tone Mapping, CGI, VFX, SFX, insanely detailed and intricate, hyper maximalist, elegant, dynamic pose, photography, volumetric, ultra-detailed, intricate details, super detailed, ambient*

        📌 Examples:
        - A 19-year-old woman in an oversized hoodie covered in stickers, standing ankle-deep in neon-pink water in an underground parking garage  
        - A serious-looking man in a silver tuxedo eating noodles alone on a rooftop at dawn, with fog-covered skyscrapers in the background  
        - A humanoid cat in vintage roller skates lighting a cigarette beside a crashed vending machine in the desert at sunset  
        - A kid with blue butterfly wings and a glittery backpack standing under heavy rain beside a glowing subway entrance  
        - A bald, tattooed monk levitating one inch above the floor inside a candle-lit laundromat

        ✍️ Output:  
        Write **one vivid, natural-sounding sentence** describing the subject, their appearance, and the full scene including the background and vibe.  
        Then immediately add the required Midjourney-style style tag list — **exactly as written** above.
    """


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_prompt}],
    )

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise ValueError(f"Invalid response from OpenAI: {response}")

    return content

def generate_image_prompt() -> str:
    user_prompt = """
        You are a creative AI that generates bold, strange, and viral ideas for TikTok-style short videos — but your concept will first be turned into a **single still image**, and only then into a video.

        🎯 Your goal:
        Write one vivid visual idea that would make an **amazing image** — something emotionally charged, visually absurd, stylish, or trend-worthy that could easily go viral as the seed of a short video.

        ✅ Your image concept must:
        - Be bold and scroll-stopping — it should instantly grab attention in a TikTok feed
        - Center on a **human, robot, alien, surreal creature, object, or animal** (don't rely too heavily on animals)
        - Frequently add **strange or unexpected physical traits** — like a robot with braids, a capybara in a wedding dress, a man in a suit wearing banana peels as shoes, or a pigeon with earrings
        - Capture a **clear, weird, funny, ironic, or emotionally resonant moment** — like a real photo that just happens to catch something incredible
        - Take place in a **visually rich, specific, and atmospheric setting** — real locations (like Los Angeles, Tokyo, Berlin, subway tunnels, gas stations, rooftop gardens, public bathrooms) or surreal, dreamlike spaces (like a floating mall or a jungle lit with LED signs)
        - Prefer **photorealism or cinematic realism** — as if shot with a high-end camera with perfect natural or dramatic lighting — but allow stylized, futuristic, or surreal looks when it adds to the impact
        - Use **color palettes that match the scene's mood** — from neon and cyberpunk glows, to warm sunset tones, pastel city haze, muted vintage film, vaporwave gradients, or dramatic chiaroscuro
        - Frequently include **portraits of real people** — describe their outfit, mood, age, expression, hairstyle, vibe, and physical traits clearly (e.g., “a 22-year-old guy in an oversized chrome jacket and bright green sneakers, squinting into the sun near a street food stall in Osaka”)
        - Feel like a **moment with viral potential** — funny, ironic, touching, stylish, or absurd — the kind of image people would repost, meme, or recreate

        🎨 Visual style guidance:
        - End the sentence with a **Midjourney-style descriptor list** (comma-separated)
        - Include tags like: *photorealistic, cinematic lighting, bokeh, 4k, shallow depth of field, f/1.4, ISO 200, 1/500s, film grain, analog photo, vibrant colors, tilt blur, HDR, soft shadows, dramatic backlight, lens flare, RTX reflections, ultra detailed, ambient occlusion, hyperreal*
        - Vary the terms each time — match the style to the concept and keep things feeling fresh
        - If realism is used, make it **feel like a living moment** — with believable depth, imperfections, lighting, and photographic texture
        - ❌ Never include text, UI elements, captions, logos, or animation effects

        📌 Example viral image moments:
        - A humanoid robot nervously paying with coins at a self-checkout
        - A man in a business suit calmly ironing clothes on a floating iceberg
        - A knight in armor ordering boba tea at a neon-lit drive-thru
        - A tiny alien couple having a romantic dinner on top of a toaster
        - A woman in a wedding dress sprinting across an airport runway as planes take off
        - A glowing vending machine in the desert being worshipped by robed androids
        - A fashion model with glowing tattoos standing under flickering lights in a Berlin nightclub
        - A soaked teenager in a dinosaur costume angrily smoking next to a flooded metro entrance
        - A pink crocodile sunbathing on a balcony in Barcelona wearing sunglasses and a gold chain
        - A delivery drone stuck in a tree, surrounded by curious pigeons wearing GoPros

        ✍️ Output:
        Write **one vivid, visual 1-sentence description** of the scene using natural, casual language.  
        At the end, include **visual style keywords** (Midjourney-style), comma-separated — with camera settings if realism is emphasized.  
        Example ending: *photorealistic, cinematic lighting, shallow depth of field, f/1.4, ISO 100, 4k*
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_prompt}],
    )

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise ValueError(f"Invalid response from OpenAI: {response}")

    return content

def generate_prompt(image_url: str, prompt_text: str) -> str:
    """
    GPT получает изображение и его описание и пишет короткую видеосцену (5–10 сек),
    как если бы описывал обычный человек: что происходит в этом видео, кто что делает и почему это выглядит интересно.
    """

    system_msg = """
        You are a creative assistant that writes vivid, trendy, and scroll-stopping short video scene descriptions based on a still image and its original prompt.

        🎬 Your goal:
        Write a short 5–10 second video scene that feels like it could go viral on TikTok or Instagram Reels — it should be **visually engaging**, **a bit absurd or emotional**, and grounded in the scene from the image.

        ✅ The scene must:
        - Stay consistent with the **style, characters, and setting** of the image
        - Describe what happens in a **simple, natural, and visual way**, like you're telling a friend what you just saw in a crazy video
        - Include **movement or interaction** — not just static visuals
        - Allow for **any emotional tone** — funny, awkward, tense, dramatic, surreal, wholesome, ironic, or unexpected
        - The moment should feel like something people would repost, meme, or remix — instantly viral or relatable in a weird way.
        - Feel like a **real viral moment** someone could’ve caught on their phone — part of a trend, a POV, or meme

        ✅ Optional but encouraged:
        - Think in the style of viral POVs, awkward moments, "caught on camera", Gen Z humor, low-stakes chaos, or surreal calm
        - Imagine things like: someone filming their friend, a stranger doing something weird, or a creature doing something unexpectedly human

        ⚠️ Do NOT:
        - Say “This could be…” or “Imagine…” — write it like it’s already happening
        - Use robotic or overly scripted phrasing — write naturally
        - Describe magical transformations, teleporting, glitching, portals, or drastic scene changes — keep it grounded and fluid
        - Don't describe editing or camera effects — keep it one continuous shot

        ✍️ Output format:
        Write **2–3 short, natural sentences** describing the video — just the visual action, like a casual narrator. Keep it vivid, visual, and easy to picture.
    """

    user_content = [
        {
            "type": "text",
            "text": f"""Original prompt: {prompt_text}
                Now, based on this image and the scene it shows, describe a short 5–10 second video as if you're telling someone what happens in it."""
        },
        {"type": "image_url", "image_url": {"url": image_url}},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content},
        ],
    )

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise ValueError("Invalid GPT response")

    return content.strip()