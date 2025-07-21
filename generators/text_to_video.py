from prompt.text_to_video_prompt import (
    generate_prompt
)

def generate_text_to_video(_: str = "") -> str:
    prompt = generate_prompt()

    return prompt