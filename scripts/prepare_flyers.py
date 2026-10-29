"""Prepare the event flyers, services banner and review cards for the website.

Usage:   python scripts/prepare_flyers.py <folder with the WhatsApp images> app/static/img

What it does:
  1. Covers payment details (bank and Palmpay accounts), other people's phone numbers, links to private
     groups and QR codes, because flyers for past events must not leave live payment details online.
  2. Covers the sender's name and picture on the email review card.
  3. Shrinks every image for the web and saves it under the clean file name the site expects.

The boxes are written as pixel positions on the ORIGINAL image size (REF). They scale automatically if the
image size differs. To keep something visible, delete its line. To cover more, add a line.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

MAX_SIDE = 1400

# source file -> (output name, reference size, [ (x0, y0, x1, y1, (sample_x, sample_y)) ... ])
# The sample point is a spot of plain background whose colour is used to fill the box.
JOBS = {
    "IMG-20261021-WA0058.jpg": ("event-upgrade-to-explore.jpg", (761, 1080), [
        (50, 672, 400, 744, (420, 710)),      # bank account block
        (70, 955, 450, 985, (460, 970)),      # private sign-up link
        (88, 994, 672, 1022, (30, 1008)),     # other organisers' phone numbers
    ]),
    "IMG-20261021-WA0062.jpg": ("event-book-launch.jpg", (936, 1080), [
        (90, 1030, 462, 1074, (475, 1050)),   # Palmpay number and account name
    ]),
    "IMG-20261021-WA0065.jpg": ("event-beyond-the-book.jpg", (864, 1080), [
        (548, 888, 690, 1046, (520, 960)),    # QR code for the Telegram group
    ]),
    "IMG-20261021-WA0067.jpg": ("event-book-writing-bootcamp.jpg", (864, 1080), [
        (60, 945, 820, 1066, (30, 1000)),     # bank account and payment instructions
    ]),
    "IMG-20261021-WA0060.jpg": ("services-flyer.jpg", (1638, 2048), []),   # her own business contact: kept
    "IMG-20261021-WA0082.jpg": ("review-email.jpg", (864, 1080), [
        (196, 304, 494, 342, (330, 400)),     # sender name and date
        (196, 304, 278, 386, (330, 400)),     # sender picture
    ]),
    "IMG-20261021-WA0084.jpg": ("review-whatsapp.jpg", (864, 1080), []),
}


def main(src_dir: str, out_dir: str) -> None:
    src, out = Path(src_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, (dst, ref, boxes) in JOBS.items():
        path = src / name
        if not path.exists():
            print(f"MISSING  {name}  (skipped)")
            continue
        img = Image.open(path).convert("RGB")
        sx, sy = img.width / ref[0], img.height / ref[1]
        draw = ImageDraw.Draw(img)
        for x0, y0, x1, y1, (px, py) in boxes:
            colour = img.getpixel((int(px * sx), int(py * sy)))
            draw.rectangle((int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy)), fill=colour)
        img.thumbnail((MAX_SIDE, MAX_SIDE))
        img.save(out / dst, "JPEG", quality=84, optimize=True, progressive=True)
        print(f"{name} -> {dst:34} {img.width}x{img.height}  ({len(boxes)} area(s) covered)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
