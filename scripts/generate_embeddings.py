#!/usr/bin/env python3
"""anaokulu.json için sentence-transformers kullanarak embedding üretir.
Kullanım:
  python scripts/generate_embeddings.py -i anaokulu.json -o anaokulu.embeddings.json --model all-MiniLM-L6-v2
Model seçimini size bıraktım; örnek modeller README'de.
"""
from sentence_transformers import SentenceTransformer
from pathlib import Path
import argparse
import json
import sys


def load_entries(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_embeddings(out_path: Path, entries, embeddings, model_name: str):
    out = []
    for entry, emb in zip(entries, embeddings):
        out.append({
            "id": entry.get("id"),
            "embedding": emb.tolist() if hasattr(emb, "tolist") else list(emb),
            "model": model_name
        })
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for anaokulu.json using sentence-transformers")
    parser.add_argument("-i", "--input", default="anaokulu.json", help="input JSON file with entries")
    parser.add_argument("-o", "--output", default="anaokulu.embeddings.json", help="output JSON file to write embeddings")
    parser.add_argument("-m", "--model", default="all-MiniLM-L6-v2",
                        help="sentence-transformers model name (e.g. all-MiniLM-L6-v2, all-mpnet-base-v2)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Hata: girdi bulunamadı: {input_path}")
        sys.exit(1)

    entries = load_entries(input_path)
    texts = [e.get("content", "") for e in entries]

    print(f"Model yükleniyor: {args.model} (bu bir kez gerçekleşir)")
    model = SentenceTransformer(args.model)

    print(f"{len(texts)} içerik için embedding üretiliyor...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    out_path = Path(args.output)
    save_embeddings(out_path, entries, embeddings, args.model)
    print(f"Kaydedildi: {out_path}")


if __name__ == '__main__':
    main()
