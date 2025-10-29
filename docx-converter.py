#!/usr/bin/env python3
from docx import Document
from pathlib import Path
import argparse
import sys


def convert_docx_to_md(docx_path: Path, md_path: Path):
    doc = Document(str(docx_path))
    md_path.parent.mkdir(parents=True, exist_ok=True)
    with md_path.open("w", encoding="utf-8") as f:
        for para in doc.paragraphs:
            style = (para.style.name or "").lower()
            text = para.text.rstrip()
            if not text:
                f.write("\n")
                continue
            if "heading 1" in style or style.startswith("heading 1"):
                f.write(f"# {text}\n\n")
            elif "heading 2" in style or style.startswith("heading 2"):
                f.write(f"## {text}\n\n")
            else:
                f.write(f"{text}\n\n")


def main():
    parser = argparse.ArgumentParser(description="DOCX -> Markdown dönüştürücü (cross-platform)")
    parser.add_argument("-i", "--input", required=True,
                        help="Girdi olarak bir .docx dosyası veya .docx dosyalarının bulunduğu dizin yolu")
    parser.add_argument("-o", "--output", required=False,
                        help="Çıktı olarak bir .md dosyası veya dizin (dizin verilmezse aynı konuma .md olarak kaydeder)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Hata: Girdi bulunamadı: {input_path}")
        sys.exit(1)

    # Eğer bir klasör verilmişse bütün .docx dosyalarını dönüştür
    if input_path.is_dir():
        out_dir = Path(args.output) if args.output else input_path
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for docx_file in sorted(input_path.glob("*.docx")):
            md_file = out_dir / (docx_file.stem + ".md")
            convert_docx_to_md(docx_file, md_file)
            print(f"Dönüştürüldü: {docx_file} -> {md_file}")
    else:
        # Tek dosya
        out_file = Path(args.output) if args.output else input_path.with_suffix('.md')
        convert_docx_to_md(input_path, out_file)
        print(f"Dönüştürüldü: {input_path} -> {out_file}")


if __name__ == "__main__":
    main()