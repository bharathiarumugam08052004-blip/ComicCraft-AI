from pathlib import Path

from fpdf import FPDF

from app.config import BASE_DIR, EXPORTS_DIR


def save_pdf(layout):

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.cell(
            0,
            10,
            str(panel["title"]),
            ln=True,
        )

        image_path = panel.get(
            "image_path",
            "",
        )

        if image_path.startswith("/static/"):

            local_path = (
                BASE_DIR
                / image_path.lstrip("/")
            )

        else:

            local_path = Path(image_path)

        if local_path.exists():

            pdf.image(
                str(local_path),
                x=15,
                y=30,
                w=180,
                h=110,
            )

        pdf.set_xy(
            15,
            145,
        )

        pdf.set_font(
            "Helvetica",
            "",
            11,
        )

        text = (
            f"Caption: {panel.get('caption', '')}\n\n"
            f"Narration: {panel.get('narration', '')}\n\n"
            f"Dialogue: {panel.get('dialogue', '')}"
        )

        pdf.multi_cell(
            180,
            7,
            text,
        )

    output_file = EXPORTS_DIR / "comic.pdf"

    pdf.output(
        str(output_file)
    )

    return "/static/exports/comic.pdf"