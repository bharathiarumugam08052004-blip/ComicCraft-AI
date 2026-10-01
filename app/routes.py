from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.schemas import PromptRequest
from app.ai.gemini_flash import generate_outline
from app.ai.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


router = APIRouter()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None,
        },
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Hero"),
    setting: str = Form("Fantasy"),
    tone: str = Form("Fun"),
    art_style: str = Form("Cartoon"),
):
    try:
        prompt_data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        # Step 1: Generate 5-panel outline
        outline = generate_outline(
            prompt_data.story_prompt,
            prompt_data.character_name,
            prompt_data.setting,
            prompt_data.tone,
            prompt_data.art_style,
        )

        # Step 2: Generate story
        story = generate_story(
            outline,
            prompt_data.character_name,
            prompt_data.tone,
        )

        # Step 3: Generate images
        images = []

        for index, scene in enumerate(story):
            image_path = generate_image(
                scene["image_prompt"],
                index,
            )
            images.append(image_path)

        # Step 4: Build comic layout
        layout = build_comic_layout(
            story,
            images,
        )

        # Step 5: Save PDF
        pdf_path = save_pdf(layout)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_path": pdf_path,
            },
        )

    except Exception as error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(error),
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_comic_json(data: PromptRequest):
    try:
        # Step 1: Generate 5-panel outline
        outline = generate_outline(
            data.story_prompt,
            data.character_name,
            data.setting,
            data.tone,
            data.art_style,
        )

        # Step 2: Generate story
        story = generate_story(
            outline,
            data.character_name,
            data.tone,
        )

        # Step 3: Generate images
        images = []

        for index, scene in enumerate(story):
            image_path = generate_image(
                scene["image_prompt"],
                index,
            )
            images.append(image_path)

        # Step 4: Build comic layout
        layout = build_comic_layout(
            story,
            images,
        )

        # Step 5: Save PDF
        pdf_path = save_pdf(layout)

        return {
            "success": True,
            "story": story,
            "layout": layout,
            "pdf_path": pdf_path,
        }

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(error),
            },
        )


@router.get("/test-image")
async def test_image():
    image_path = generate_image(
        "A cute cartoon character standing in a colorful fantasy world",
        0,
    )

    return {
        "success": True,
        "image": image_path,
    }


@router.get("/api/health")
async def health():
    return {
        "status": "ok",
        "message": "ComicCraft API is running",
    }