import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import click
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def find_font(font_arg: str | None) -> str:
    if font_arg:
        p = Path(font_arg).expanduser()
        if not p.exists():
            raise FileNotFoundError(f"Font does not exist: {p}")
        return str(p)

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/usr/share/fonts/opentype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    raise FileNotFoundError("Could not find a font. Use --font /path/to/font.ttf")


def make_frame(
    width: int,
    height: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    rng: random.Random,
    frame_no: int,
    fps: int,
    strength: float,
):
    # Near-black background with old-film flicker
    flicker = rng.randint(-7, 9)
    bg = max(0, min(255, 14 + flicker))
    img = Image.new("L", (width, height), bg)
    draw = ImageDraw.Draw(img)

    # Grain
    grain_points = int(width * height * 0.006)
    for _ in range(grain_points):
        x = rng.randrange(width)
        y = rng.randrange(height)
        v = rng.choice((20, 28, 35, 45, 55, 70, 90))
        draw.point((x, y), fill=v)

    # Scratches and dust
    if rng.random() < 0.35:
        for _ in range(rng.randint(1, 4)):
            x = rng.randrange(width)
            shade = rng.randint(45, 110)
            draw.line((x, 0, x + rng.randint(-3, 3), height), fill=shade, width=1)

    for _ in range(rng.randint(2, 10)):
        x = rng.randrange(width)
        y = rng.randrange(height)
        r = rng.choice((1, 1, 2, 3))
        draw.ellipse((x-r, y-r, x+r, y+r), fill=rng.randint(45, 120))

    # Small global vertical jump, projector-style
    global_y = rng.randint(-2, 2)

    # Text measurement and position
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=1)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # Deliberately rough and somewhat irregular shake
    t = frame_no / fps
    shake_x = (
        math.sin(t * 2 * math.pi * 7.2) * 2.2 +
        math.sin(t * 2 * math.pi * 13.7) * 1.1 +
        rng.uniform(-2.0, 2.0)
    ) * strength
    shake_y = (
        math.sin(t * 2 * math.pi * 5.4) * 1.7 +
        rng.uniform(-1.8, 1.8)
    ) * strength

    x = (width - tw) / 2 + shake_x
    y = (height - th) / 2 + shake_y + global_y

    # Shadow/misregistration for an old print/projection feel
    ghost = rng.choice((-1, 0, 0, 1))
    draw.text(
        (x + ghost, y + ghost),
        text,
        font=font,
        fill=205,
        stroke_width=1,
        stroke_fill=120,
        anchor=None,
    )

    # Title brightness variation
    title_level = max(150, min(245, 220 + rng.randint(-20, 18)))
    draw.text(
        (x, y),
        text,
        font=font,
        fill=title_level,
        stroke_width=1,
        stroke_fill=150,
    )

    # Very faint horizontal lines
    for yy in range(0, height, 6):
        draw.line((0, yy, width, yy), fill=max(0, bg - 5), width=1)

    # Slight irregular blur
    if rng.random() < 0.25:
        img = img.filter(ImageFilter.GaussianBlur(radius=rng.choice((0.3, 0.5, 0.7))))

    return img.convert("RGB")


@click.command(help="Generates a shaky video title card in an old-film/old-recording style.")
@click.argument("text", default="TO BE CONTINUED...", required=False)
@click.option("-o", "--output", default="old_title.mp4", help="Output file")
@click.option("--seconds", type=float, default=4.0, help="Duration in seconds")
@click.option("--fps", type=int, default=24, help="FPS")
@click.option("--width", type=int, default=1280, help="Width")
@click.option("--height", type=int, default=720, help="Height")
@click.option("--font-size", type=int, default=92, help="Font size")
@click.option("--font", default=None, help="Path to a TTF/OTF font")
@click.option("--shake", type=float, default=1.0, help="Shake intensity")
@click.option("--seed", type=int, default=7, help="Random seed")
def main(text, output, seconds, fps, width, height, font_size, font, shake, seed):
    if shutil.which("ffmpeg") is None:
        click.echo("ffmpeg is missing. Install it with: sudo apt install ffmpeg", err=True)
        sys.exit(1)

    font_path = find_font(font)
    ft = ImageFont.truetype(font_path, font_size)
    total_frames = max(1, round(seconds * fps))
    rng = random.Random(seed)

    with tempfile.TemporaryDirectory(prefix="oldtitle_") as tmp:
        tmp_path = Path(tmp)

        for i in range(total_frames):
            frame = make_frame(
                width, height, text, ft, rng,
                i, fps, shake
            )
            frame.save(tmp_path / f"frame_{i:06d}.png")

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(tmp_path / "frame_%06d.png"),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output,
        ]
        subprocess.run(cmd, check=True)

    click.echo(f"Created: {output}")


if __name__ == "__main__":
    main()
