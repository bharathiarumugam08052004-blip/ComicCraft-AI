import json
import re

from app.config import settings


def extract_json(text: str):

    if not text:
        raise ValueError(
            "AI returned an empty response."
        )

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

    json_text = text[start:end + 1]

    return json.loads(json_text)


def generate_mock_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style,
):

    return [
        {
            "panel_number": 1,
            "title": "The Beginning",
            "scene_description": (
                f"{character_name} begins an adventure "
                f"in the {setting}."
            ),
            "image_prompt": (
                f"{character_name} entering a beautiful "
                f"{setting}, {art_style} style, "
                f"colorful comic illustration."
            ),
        },
        {
            "panel_number": 2,
            "title": "The Discovery",
            "scene_description": (
                f"{character_name} discovers something "
                f"mysterious in the {setting}."
            ),
            "image_prompt": (
                f"{character_name} discovering a mysterious "
                f"object in the {setting}, {art_style} style."
            ),
        },
        {
            "panel_number": 3,
            "title": "The Challenge",
            "scene_description": (
                f"{character_name} faces an unexpected "
                f"challenge."
            ),
            "image_prompt": (
                f"{character_name} facing an exciting "
                f"challenge in the {setting}, "
                f"{art_style} style."
            ),
        },
        {
            "panel_number": 4,
            "title": "The Solution",
            "scene_description": (
                f"{character_name} finds a clever way "
                f"to solve the problem."
            ),
            "image_prompt": (
                f"{character_name} solving the problem "
                f"in the {setting}, {art_style} style."
            ),
        },
        {
            "panel_number": 5,
            "title": "The Ending",
            "scene_description": (
                f"{character_name} completes the adventure "
                f"with a happy ending."
            ),
            "image_prompt": (
                f"{character_name} celebrating in the "
                f"{setting}, happy ending, "
                f"{art_style} style."
            ),
        },
    ]


def generate_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style,
):

    if settings.mock_ai:

        return generate_mock_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style,
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

        prompt = f"""
Create a five-panel comic outline.

Story idea:
{story_prompt}

Character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return exactly 5 panels.

Each panel must contain:
panel_number
title
scene_description
image_prompt

Return only JSON.
"""

        response = client.models.generate_content(
            model=settings.gemini_outline_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )

        data = extract_json(response.text)

        if not isinstance(data, list):
            raise ValueError(
                "AI response must be a list."
            )

        if len(data) != 5:
            raise ValueError(
                f"Expected 5 panels, got {len(data)}."
            )

        return data

    except ImportError:

        raise RuntimeError(
            "google-genai is not installed."
        )

    except Exception as error:

        raise RuntimeError(
            f"Gemini outline generation failed: {error}"
        )