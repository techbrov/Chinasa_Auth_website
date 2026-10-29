"""Extract and optimise the client's images from her portfolio .docx.
Usage:  python scripts/prepare_assets.py MY_PORTFOLIO.docx app/static/img
Only public-safe images are extracted. Chat screenshots and students' certificates are skipped on purpose:
they show other people's names and private messages and need written permission first."""
import sys
import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image

MAP = {  # name inside the .docx  ->  clean file name used by the site
    "image32.jpg": "author-photo.jpg", "image33.jpg": "business-card.jpg", "image18.jpg": "award.jpg",
    "image13.jpg": "the-drive.jpg", "image4.jpg": "upgrade-to-explore.jpg",  # cover confirmed by the client
    "image2.jpg": "unveil.jpg", "image3.jpg": "worthy-of-wealth.jpg", "image5.jpg": "becoming-a-smart-mom.jpg",
    "image11.jpg": "dude-without-limits.jpg", "image17.jpg": "40-affirmations.jpg",
    "image35.png": "course-manual.jpg",
    "image28.jpg": "cert-grammar.jpg", "image21.jpg": "cert-english.jpg", "image27.jpg": "cert-ghostwriting.jpg",
    "image19.jpg": "cert-digital-tools.jpg", "image31.jpg": "cert-content-weaving.jpg",
    "image8.jpg": "cert-manual-writing.jpg", "image34.png": "cert-book-editing.jpg",
    "image10.jpg": "sample-preface.jpg", "image15.jpg": "sample-chapter.jpg",
    "image22.jpg": "sample-acknowledgement.jpg",
}
MAX_SIDE = 1400
# Fractions (left, top, right, bottom) to keep. The author photo has a photographer's watermark in the
# top-right corner, in the empty space above her head, so the top 11% is removed.
CROPS = {"author-photo.jpg": (0, 0.11, 1, 1)}


def main(docx_path: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx_path) as z:
        for src, dst in MAP.items():
            data = z.read(f"word/media/{src}")
            img = Image.open(BytesIO(data))
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
                bg = Image.new("RGB", img.size, "white")
                bg.paste(img, mask=img.split()[-1])
                img = bg
            else:
                img = img.convert("RGB")
            if dst in CROPS:
                l, t, rt, b = CROPS[dst]
                img = img.crop((int(img.width * l), int(img.height * t), int(img.width * rt), int(img.height * b)))
            img.thumbnail((MAX_SIDE, MAX_SIDE))
            img.save(out / dst, "JPEG", quality=82, optimize=True, progressive=True)
            print(f"{src:12} -> {dst:28} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
