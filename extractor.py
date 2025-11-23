import re
import json
from typing import List, Dict, Any
from docx import Document

def extract_requirements_from_docx(path: str) -> Dict[str, Any]:
    doc = Document(path)
    sections = []
    current_section = {"title": None, "paragraphs": []}

    for para in doc.paragraphs:
        text = para.text.strip()

        if not text:
            continue

        style = para.style.name if para.style else ""

        if style.startswith("Heading"):
            if current_section["title"] or current_section["paragraphs"]:
                sections.append(current_section)
            current_section = {"title": text, "paragraphs": []}
        else:
            current_section["paragraphs"].append(text)

    if current_section["title"] or current_section["paragraphs"]:
        sections.append(current_section)

    # Detectar requisitos (REQ-xxx ou sentenças obrigatórias)
    for section in sections:
        requirements = []
        for p in section["paragraphs"]:
            req_ids = re.findall(r'\bREQ[- ]?(\d+)\b', p)
            if req_ids:
                for rid in req_ids:
                    requirements.append({"id": f"REQ-{rid}", "text": p})
            else:
                # Heurística básica para identificar requisitos implícitos
                if p.lower().startswith(("o sistema", "deve", "deverá", "quando", "caso", "se")):
                    requirements.append({"id": None, "text": p})

        section["requirements"] = requirements

    return {
        "file": path,
        "sections": sections
    }

if __name__ == "__main__":
    result = extract_requirements_from_docx("requisitos.docx")
    with open("saida.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Extração concluída! Arquivo salvo como saida.json")