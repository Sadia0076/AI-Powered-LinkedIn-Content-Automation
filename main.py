from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io


app = FastAPI(
    title="DLeaders LinkedIn Image Generator",
    version="1.0.0"
)


# ============================================================
# Configuration
# ============================================================

CANVAS_W = 1200
CANVAS_H = 627

FOOTER_H = 45

LOGO_MAX_W = 160
LOGO_MAX_H = 60

LOGO_MARGIN_X = 25
LOGO_MARGIN_Y = 25

BRAND_TEXT = "www.dleaders.online"

FOOTER_COLOR = (17, 17, 17, 235)
TEXT_COLOR = (255, 255, 255)


# ============================================================
# Health Check
# ============================================================

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "DLeaders LinkedIn Image Generator",
        "version": "1.0.0"
    }


# ============================================================
# Generate LinkedIn Image
# ============================================================

@app.post("/generate-image")
async def generate_image(
    person_image: UploadFile = File(...),
    logo: UploadFile = File(...)
):

    try:

        # ----------------------------------------------------
        # 1. Read person image
        # ----------------------------------------------------

        person_bytes = await person_image.read()

        person_img = Image.open(
            io.BytesIO(person_bytes)
        ).convert("RGB")


        # ----------------------------------------------------
        # 2. Read DLeaders logo
        # ----------------------------------------------------

        logo_bytes = await logo.read()

        logo_img = Image.open(
            io.BytesIO(logo_bytes)
        ).convert("RGBA")


        # ----------------------------------------------------
        # 3. Create LinkedIn canvas
        # ----------------------------------------------------

        canvas = Image.new(
            "RGBA",
            (CANVAS_W, CANVAS_H),
            (255, 255, 255, 255)
        )


        # ----------------------------------------------------
        # 4. Make person image cover entire canvas
        # ----------------------------------------------------

        person_img = ImageOps.fit(
            person_img,
            (CANVAS_W, CANVAS_H),
            method=Image.Resampling.LANCZOS
        )

        canvas.paste(
            person_img,
            (0, 0)
        )


        # ----------------------------------------------------
        # 5. Add footer
        # ----------------------------------------------------

        draw = ImageDraw.Draw(
            canvas,
            "RGBA"
        )

        footer_top = CANVAS_H - FOOTER_H

        draw.rectangle(
            [
                (0, footer_top),
                (CANVAS_W, CANVAS_H)
            ],
            fill=FOOTER_COLOR
        )


        # ----------------------------------------------------
        # 6. Load footer font
        # ----------------------------------------------------

        try:

            font = ImageFont.truetype(
                "DejaVuSans-Bold.ttf",
                20
            )

        except:

            font = ImageFont.load_default()


        # ----------------------------------------------------
        # 7. Center footer text
        # ----------------------------------------------------

        bbox = draw.textbbox(
            (0, 0),
            BRAND_TEXT,
            font=font
        )

        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        text_x = (
            CANVAS_W - text_w
        ) // 2

        text_y = (
            footer_top
            + (FOOTER_H - text_h) // 2
            - bbox[1]
        )


        draw.text(
            (text_x, text_y),
            BRAND_TEXT,
            fill=TEXT_COLOR,
            font=font
        )


        # ----------------------------------------------------
        # 8. Resize DLeaders logo
        # ----------------------------------------------------

        logo_ratio = (
            logo_img.width /
            logo_img.height
        )

        logo_w = LOGO_MAX_W

        logo_h = int(
            logo_w / logo_ratio
        )

        if logo_h > LOGO_MAX_H:

            logo_h = LOGO_MAX_H

            logo_w = int(
                logo_h * logo_ratio
            )


        logo_img = logo_img.resize(
            (logo_w, logo_h),
            Image.Resampling.LANCZOS
        )


        # ----------------------------------------------------
        # 9. Paste logo top-left
        # ----------------------------------------------------

        canvas.paste(
            logo_img,
            (
                LOGO_MARGIN_X,
                LOGO_MARGIN_Y
            ),
            logo_img
        )


        # ----------------------------------------------------
        # 10. Convert to PNG
        # ----------------------------------------------------

        output_buffer = io.BytesIO()

        canvas.convert("RGB").save(
            output_buffer,
            format="PNG",
            optimize=True
        )

        output_buffer.seek(0)


        # ----------------------------------------------------
        # 11. Return PNG
        # ----------------------------------------------------

        return Response(
            content=output_buffer.getvalue(),
            media_type="image/png",
            headers={
                "Content-Disposition":
                    'attachment; filename="dleaders_linkedin_image.png"'
            }
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )