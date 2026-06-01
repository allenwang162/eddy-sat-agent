from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "assets" / "eddy-demo.gif"

W, H = 720, 405
FPS = 12
DURATION_SECONDS = 6
FRAMES = FPS * DURATION_SECONDS

INK = (16, 38, 48)
MUTED = (92, 108, 116)
TEAL = (18, 96, 122)
PANEL = (251, 253, 252)
LINE = (213, 224, 229)
CORAL = (239, 91, 126)
VIOLET = (124, 92, 255)
LIME = (178, 226, 92)
AMBER = (255, 226, 141)


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT_XS = font(12)
FONT_SM = font(15)
FONT_MD = font(20)
FONT_LG = font(28, bold=True)
FONT_TITLE = font(34, bold=True)
FONT_BOLD = font(18, bold=True)
FONT_HUGE = font(42, bold=True)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def gradient(size, left, right):
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for x in range(size[0]):
        ratio = x / max(1, size[0] - 1)
        color = tuple(int(left[i] * (1 - ratio) + right[i] * ratio) for i in range(3))
        draw.line([(x, 0), (x, size[1])], fill=color)
    return image


def text(draw, xy, value, fill=INK, fnt=FONT_SM):
    draw.text(xy, value, fill=fill, font=fnt)


def wrap(draw, xy, value, max_width, fill=INK, fnt=FONT_SM, line_gap=5):
    x, y = xy
    words = value.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    for index, line in enumerate(lines):
        draw.text((x, y + index * (fnt.size + line_gap)), line, fill=fill, font=fnt)
    return y + len(lines) * (fnt.size + line_gap)


def pill(draw, box, label, fill=(232, 246, 248), label_fill=INK):
    rounded(draw, box, 18, fill)
    text(draw, (box[0] + 14, box[1] + 7), label, fill=label_fill, fnt=FONT_XS)


def draw_cursor(draw, x, y):
    points = [(x, y), (x, y + 26), (x + 7, y + 20), (x + 13, y + 33), (x + 20, y + 30), (x + 14, y + 18), (x + 24, y + 18)]
    draw.polygon(points, fill=(255, 255, 255), outline=(12, 28, 36))


def lerp(a, b, t):
    return a + (b - a) * max(0, min(1, t))


def frame(step):
    image = gradient((W, H), (7, 54, 70), (32, 30, 84)).convert("RGB")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    rounded(draw, (28, 28, W - 28, H - 28), 22, (255, 255, 255, 238))
    text(draw, (54, 54), "Eddy SAT GOAT", fill=TEAL, fnt=FONT_BOLD)
    text(draw, (54, 82), "AI tutoring, review, and progress analysis for SAT practice", fill=MUTED, fnt=FONT_SM)

    scene = 0 if step < 24 else 1 if step < 48 else 2
    active_tabs = ["AI Tutor", "Review", "Progress"]
    for index, label in enumerate(active_tabs):
        x = 420 + index * 78
        fill = (232, 246, 248) if index == scene else (245, 248, 249)
        rounded(draw, (x, 50, x + 68, 80), 15, fill, LINE)
        text(draw, (x + 10, 58), label, fill=TEAL if index == scene else MUTED, fnt=FONT_XS)

    if scene == 0:
        rounded(draw, (54, 122, 318, 326), 16, PANEL, LINE)
        text(draw, (76, 146), "SAT AI Tutor", fill=TEAL, fnt=FONT_MD)
        pill(draw, (226, 142, 286, 172), "Codex")
        rounded(draw, (76, 194, 296, 278), 18, (236, 251, 252), (182, 232, 238))
        wrap(draw, (94, 212), "Hint: this is a transition question. Look for the relationship between the two ideas before choosing.", 176, fnt=FONT_SM)
        rounded(draw, (332, 122, 646, 326), 16, PANEL, LINE)
        wrap(draw, (354, 146), "Students get help while working", 250, fill=INK, fnt=FONT_MD, line_gap=2)
        wrap(draw, (354, 196), "Ask Eddy for hints, concept checks, answer explanations, or help eliminating choices without leaving the test.", 250, fill=MUTED, fnt=FONT_SM)
        rounded(draw, (354, 276, 464, 310), 17, (241, 238, 255), (205, 190, 255))
        text(draw, (382, 284), "Hint", fill=INK, fnt=FONT_SM)
        rounded(draw, (474, 276, 604, 310), 17, (241, 238, 255), (205, 190, 255))
        text(draw, (494, 284), "Concept", fill=INK, fnt=FONT_SM)
        cursor_points = [(416, 294), (260, 250)]
    elif scene == 1:
        rounded(draw, (54, 122, 318, 326), 16, PANEL, LINE)
        text(draw, (76, 144), "Review", fill=TEAL, fnt=FONT_MD)
        text(draw, (76, 188), "Score range", fill=MUTED, fnt=FONT_XS)
        text(draw, (76, 206), "1240-1320", fill=INK, fnt=FONT_HUGE)
        text(draw, (76, 266), "38 of 54 Math correct", fill=MUTED, fnt=FONT_SM)
        rounded(draw, (332, 122, 646, 326), 16, PANEL, LINE)
        text(draw, (354, 146), "Mistake analysis", fill=INK, fnt=FONT_MD)
        rounded(draw, (354, 188, 618, 224), 18, (255, 239, 238), (244, 194, 190))
        text(draw, (372, 197), "Review: Advanced Math", fill=(143, 50, 50), fnt=FONT_SM)
        wrap(draw, (354, 244), "Eddy explains why the selected answer missed the constraint and recommends two similar questions.", 252, fill=MUTED, fnt=FONT_SM)
        cursor_points = [(558, 206), (430, 206)]
    else:
        rounded(draw, (54, 122, 318, 326), 16, PANEL, LINE)
        text(draw, (76, 144), "Progress", fill=TEAL, fnt=FONT_MD)
        axis = (86, 292, 286, 188)
        draw.line((axis[0], axis[1], axis[2], axis[1]), fill=LINE, width=2)
        draw.line((axis[0], axis[1], axis[0], axis[3]), fill=LINE, width=2)
        points = [(96, 264), (142, 248), (188, 232), (234, 214), (280, 196)]
        draw.line(points, fill=TEAL, width=5)
        for p in points:
            draw.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), fill=TEAL)
        text(draw, (86, 304), "Attempts improving", fill=MUTED, fnt=FONT_XS)
        rounded(draw, (332, 122, 646, 326), 16, PANEL, LINE)
        text(draw, (354, 146), "Personal study plan", fill=INK, fnt=FONT_MD)
        for i, (label, pct, color) in enumerate([
            ("Words in context", 82, TEAL),
            ("Advanced Math", 54, CORAL),
            ("Geometry", 68, VIOLET),
        ]):
            y = 194 + i * 42
            text(draw, (354, y), label, fill=INK, fnt=FONT_XS)
            rounded(draw, (474, y + 1, 618, y + 14), 7, (232, 236, 238))
            rounded(draw, (474, y + 1, 474 + int(144 * pct / 100), y + 14), 7, color)
            text(draw, (624, y - 1), f"{pct}%", fill=MUTED, fnt=FONT_XS)
        text(draw, (354, 306), "Next: Advanced Math with tutor review.", fill=MUTED, fnt=FONT_XS)
        cursor_points = [(150, 248), (540, 214)]

    captions = [
        (0, "AI Tutor gives targeted hints while students practice"),
        (24, "Review turns each attempt into explanations and next steps"),
        (48, "Progress tracks trends and highlights what to study next"),
    ]
    caption = captions[0][1]
    for start, value in captions:
        if step >= start:
            caption = value
    rounded(draw, (58, 354, 662, 382), 14, (11, 40, 52, 210))
    text(draw, (76, 360), caption, fill=(255, 255, 255), fnt=FONT_SM)

    local_step = step % 24
    start, end = cursor_points
    x, y = lerp(start[0], end[0], local_step / 23), lerp(start[1], end[1], local_step / 23)
    draw_cursor(draw, int(x), int(y))

    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    return image.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [frame(i) for i in range(FRAMES)]
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
