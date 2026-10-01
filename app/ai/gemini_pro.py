import json
import re

from app.config import settings


def extract_json(text: str):
    if not text:
        raise ValueError("AI returned an empty response.")

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^```\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(
            "AI response does not contain a JSON array."
        )

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON returned by AI: {error}"
        )


def generate_mock_story(
    outline,
    character_name,
    tone,
):
    """
    Generate a clean five-panel story
    for testing without API keys.
    """

    dialogues = [
        f"{character_name}: What is this mysterious book?",
        f"{character_name}: Amazing! The book has taken me to a magical world!",
        f"{character_name}: The light is disappearing. We have to save this world!",
        f"{character_name}: Let's work together. Courage and friendship can help us!",
        f"{character_name}: We restored the light! Kindness and friendship made it possible!",
    ]

    narrations = [
        f"{character_name} discovers a mysterious magical book in her college library.",
        f"When she opens the book, {character_name} enters a beautiful magical world and meets new friends.",
        f"The friends discover that the magical world's light has been lost, and they decide to restore it.",
        f"Working together with courage, friendship and kindness, they overcome the challenges on their journey.",
        f"The lost light returns to the magical world, and {character_name} learns that friendship and kindness can overcome any challenge.",
    ]

    result = []

    for index, panel in enumerate(outline):

        number = index + 1

        result.append(
            {
                "panel_number": number,
                "title": panel.get(
                    "title",
                    f"Panel {number}",
                ),
                "scene_description": narrations[index],
                "image_prompt": panel.get(
                    "image_prompt",
                    narrations[index],
                ),
                "caption": (
                    f"Panel {number}: "
                    f"{panel.get('title', '')}"
                ),
                "narration": narrations[index],
                "dialogue": dialogues[index],
            }
        )

    return result


def generate_story(
    outline,
    character_name,
    tone,
):

    if settings.mock_ai:
        return generate_mock_story(
            outline,
            character_name,
            tone,
        )

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing in .env"
        )

    try:

        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=settings.gemini_api_key
        )

        outline_json = json.dumps(
            outline,
            ensure_ascii=False,
            indent=2,
        )

        prompt = f"""
Create a professional five-panel comic story.

Character:
{character_name}

Tone:
{tone}

Use this outline:
{outline_json}

IMPORTANT STORY RULES:

1. Create exactly 5 connected panels.
2. Panel 1 must introduce the character and situation.
3. Panel 2 must develop the story.
4. Panel 3 must introduce the main challenge.
5. Panel 4 must show the characters solving or overcoming the challenge.
6. Panel 5 must provide a clear and satisfying ending.
7. Every panel must have different dialogue.
8. NEVER repeat dialogue between panels.
9. Dialogue must match the scene.
10. Narration must be short and meaningful.
11. Image prompts must clearly describe what should appear in the panel.
12. Keep the same character throughout the story.
13. Keep the story consistent from beginning to end.
14. Do not add unrelated events.
15. Use the selected tone.
16. Make the story suitable for a clean educational comic.
17. Return exactly 5 objects.
18. Return ONLY valid JSON.

Each object must contain:

panel_number
title
scene_description
image_prompt
caption
narration
dialogue

Return only the JSON array.
"""

        response = client.models.generate_content(
            model=settings.gemini_story_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json",
            ),
        )

        data = extract_json(response.text)

        if not isinstance(data, list):
            raise ValueError(
                "AI story response must be a list."
            )

        if len(data) != 5:
            raise ValueError(
                f"Expected 5 panels, got {len(data)}."
            )

        required_fields = [
            "panel_number",
            "title",
            "scene_description",
            "image_prompt",
            "caption",
            "narration",
            "dialogue",
        ]

        for index, panel in enumerate(data):

            if not isinstance(panel, dict):
                raise ValueError(
                    f"Panel {index + 1} is invalid."
                )

            for field in required_fields:

                if field not in panel:
                    raise ValueError(
                        f"Panel {index + 1} is missing: {field}"
                    )

        return data

    except ImportError:
        raise RuntimeError(
            "google-genai is not installed."
        )

    except Exception as error:
        raise RuntimeError(
            f"Gemini story generation failed: {error}"
        )