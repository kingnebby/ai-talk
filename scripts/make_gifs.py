"""Build the looping sticker graphics for the deck."""

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "images"
SIZE = 800
INK = (20, 18, 11, 255)
YELLOW = (255, 225, 74, 255)
PINK = (255, 59, 122, 255)
CYAN = (29, 224, 194, 255)
CREAM = (243, 239, 228, 255)
GOLD = (255, 186, 32, 255)
VIOLET = (109, 74, 255, 255)


def canvas():
    return Image.new("RGBA", (SIZE, SIZE), INK)


def save(frames, name, duration):
    rgb = [frame.convert("RGB") for frame in frames]
    palette = rgb[0].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    quantized = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in rgb
    ]
    quantized[0].save(
        OUT / name,
        save_all=True,
        append_images=quantized[1:],
        duration=duration,
        loop=0,
        disposal=2,
    )


def node_layers():
    cols = [150, 400, 650]
    rows = [
        [190, 400, 610],
        [120, 290, 460, 640],
        [190, 400, 610],
    ]
    return [[(x, y) for y in ys] for x, ys in zip(cols, rows)]


def net_frames():
    layers = node_layers()
    edges = []
    for left, right in zip(layers, layers[1:]):
        for index, start in enumerate(left):
            edges.append((start, right[min(index, len(right) - 1)]))
            edges.append((start, right[min(index + 1, len(right) - 1)]))
    edge_colors = [CYAN, PINK, YELLOW, VIOLET]
    frames = []
    steps = 28
    for tick in range(steps):
        image = canvas()
        draw = ImageDraw.Draw(image)
        for index, (start, end) in enumerate(edges):
            draw.line([start, end], fill=edge_colors[index % 4], width=10)
        for slot in range(3):
            edge = edges[(tick + slot * 7) % len(edges)]
            phase = ((tick + slot * 5) % steps) / steps
            x = edge[0][0] + (edge[1][0] - edge[0][0]) * phase
            y = edge[0][1] + (edge[1][1] - edge[0][1]) * phase
            draw.ellipse((x - 16, y - 16, x + 16, y + 16), fill=CREAM, outline=INK, width=6)
        for layer in layers:
            for x, y in layer:
                draw.ellipse((x - 34, y - 34, x + 34, y + 34), fill=YELLOW, outline=INK, width=8)
        frames.append(image)
    return frames


def sticker_face(kind):
    face = Image.new("RGBA", (460, 460), (0, 0, 0, 0))
    draw = ImageDraw.Draw(face)
    if kind == "person":
        draw.ellipse((165, 40, 295, 170), fill=CREAM, outline=INK, width=10)
        draw.rounded_rectangle((130, 190, 330, 400), radius=70, fill=CREAM, outline=INK, width=10)
    else:
        draw.rounded_rectangle((125, 125, 335, 335), radius=28, fill=INK, outline=INK, width=8)
        draw.rounded_rectangle((160, 160, 300, 300), radius=16, fill=YELLOW)
        for offset in range(4):
            y = 155 + offset * 48
            draw.rounded_rectangle((78, y, 125, y + 18), radius=4, fill=CREAM, outline=INK, width=6)
            draw.rounded_rectangle((335, y, 382, y + 18), radius=4, fill=CREAM, outline=INK, width=6)
    return face


def coin_frames():
    person = sticker_face("person")
    chip = sticker_face("chip")
    frames = []
    steps = 24
    for tick in range(steps):
        image = canvas()
        draw = ImageDraw.Draw(image)
        angle = (tick / steps) * math.tau
        scale = math.cos(angle)
        width = max(18, int(300 * abs(scale)))
        height = 300
        left = 400 - width
        top = 400 - height
        box = (left, top, 400 + width, 400 + height)
        draw.ellipse((left - 28, top - 28, 400 + width + 28, 400 + height + 28), fill=INK)
        draw.ellipse(box, fill=GOLD)
        if abs(scale) > 0.22:
            source = person if scale >= 0 else chip
            scaled = source.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
            layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
            layer.paste(scaled, (400 - scaled.width // 2, 400 - scaled.height // 2), scaled)
            mask = Image.new("L", (SIZE, SIZE), 0)
            ImageDraw.Draw(mask).ellipse(box, fill=255)
            layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
            image.alpha_composite(layer)
        frames.append(image)
    return frames


def bomb_frames():
    fuse = []
    for step in range(20):
        t = step / 19
        fuse.append((500 + t * 150, 250 - math.sin(t * math.pi) * 90 - t * 20))
    frames = []
    for tick in range(20):
        image = canvas()
        draw = ImageDraw.Draw(image)
        draw.line(fuse, fill=CREAM, width=18)
        draw.ellipse((150, 230, 560, 640), fill=PINK, outline=YELLOW, width=14)
        draw.ellipse((230, 300, 330, 390), fill=(255, 214, 232, 255))
        spark = fuse[tick]
        draw.ellipse((spark[0] - 22, spark[1] - 22, spark[0] + 22, spark[1] + 22), fill=YELLOW, outline=INK, width=6)
        draw.ellipse((spark[0] - 8, spark[1] - 8, spark[0] + 8, spark[1] + 8), fill=CREAM)
        frames.append(image)
    return frames


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    save(net_frames(), "net.gif", 80)
    save(coin_frames(), "coin.gif", 80)
    save(bomb_frames(), "bomb.gif", 90)
