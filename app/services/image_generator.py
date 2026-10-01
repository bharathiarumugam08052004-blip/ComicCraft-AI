from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from app.config import settings, PANELS_DIR


def _safe_font(size=28):

    try:
        return ImageFont.truetype(
            "arial.ttf",
            size,
        )
    except Exception:
        return ImageFont.load_default()


def create_mock_image(
    prompt: str,
    panel_number: int,
    output_path: Path,
):

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height,
        ),
        "white",
    )

    draw = ImageDraw.Draw(image)

    title_font = _safe_font(36)
    text_font = _safe_font(22)

    draw.rectangle(
        [
            10,
            10,
            settings.image_width - 10,
            settings.image_height - 10,
        ],
        outline="black",
        width=5,
    )

    draw.text(
        (40, 40),
        f"COMIC PANEL {panel_number}",
        fill="black",
        font=title_font,
    )

    draw.text(
        (40, 120),
        prompt[:300],
        fill="black",
        font=text_font,
    )

    draw.text(
        (40, settings.image_height - 80),
        "ComicCraft AI",
        fill="black",
        font=text_font,
    )

    image.save(
        output_path,
        format="PNG",
    )


def generate_image(
    prompt: str,
    panel_number: int,
):

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S%f"
    )

    filename = f"panel_{panel_number}_{timestamp}.png"

    output_path = PANELS_DIR / filename

    provider = settings.image_provider.lower().strip()

    if settings.mock_ai or provider == "mock":

        create_mock_image(
            prompt,
            panel_number,
            output_path,
        )

        return f"/static/panels/{filename}"

    if provider == "hf":

        if not settings.hf_token:
            raise RuntimeError(
                "HF_TOKEN is missing in .env"
            )

        try:

            from huggingface_hub import InferenceClient

            client = InferenceClient(
                api_key=settings.hf_token,
            )

            image = client.text_to_image(
                prompt=prompt,
                model=settings.hf_image_model,
            )

            image.save(
                output_path,
                format="PNG",
            )

            return f"/static/panels/{filename}"

        except ImportError:

            raise RuntimeError(
                "huggingface_hub is not installed."
            )

        except Exception as error:

            raise RuntimeError(
                f"Hugging Face image generation failed: {error}"
            )

    raise ValueError(
        f"Unsupported IMAGE_PROVIDER: {provider}"
    )