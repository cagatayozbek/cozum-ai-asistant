from docx import Document

def convert_docx_to_md(docx_path, md_path):
    doc = Document(docx_path)
    with open(md_path, "w", encoding="utf-8") as f:
        for para in doc.paragraphs:
            style = para.style.name.lower()
            if "heading 1" in style:
                f.write(f"# {para.text}\n\n")
            elif "heading 2" in style:
                f.write(f"## {para.text}\n\n")
            else:
                f.write(f"{para.text}\n\n")

# Örnek kullanım
convert_docx_to_md("Anaokulu.VeliBilgilendirmeMetni.docx", "Anaokulu.md")