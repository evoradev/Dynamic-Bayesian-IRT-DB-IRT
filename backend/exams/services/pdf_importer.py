import re
import numpy
from pathlib import Path
import PyPDF2 # Usaremos PyPDF2 como exemplo principal

def try_extract_text(file_object):
    """
    Extrai texto de um objeto de arquivo em memória (de um upload) ou de um stream de arquivo.
    """
    text = []
    try:
        # PyPDF2.PdfReader funciona diretamente com o objeto de arquivo do Django
        reader = PyPDF2.PdfReader(file_object)
        for page in reader.pages:
            text.append(page.extract_text() or "")
        return "\n".join(text)
    except Exception as e:
        raise RuntimeError(f"Falha ao extrair texto do PDF com PyPDF2: {e}")


def process_test_pdfs(pdf_prova_file, pdf_gabarito_file, initial_params=None):
    """
    Recebe objetos de arquivo PDF, processa-os e retorna uma lista de dicionários
    com os dados das questões prontas para serem salvas.

    Args:
        pdf_prova_file: Objeto de arquivo do PDF da prova.
        pdf_gabarito_file: Objeto de arquivo do PDF do gabarito.
        initial_params (dict, optional): Um dicionário com parâmetros iniciais
                                        onde a chave é o número da questão (str)
                                        e o valor é outro dict {'a':, 'b':, 'c':}.
                                        Defaults to None.
    """
    raw_text_prova = try_extract_text(pdf_prova_file)
    raw_text_gabarito = try_extract_text(pdf_gabarito_file)

    # --- INÍCIO DO CÓDIGO DE PARSING ORIGINAL ---
    # Esta é a sua lógica de extração de questões e alternativas via Regex
    parts = re.split(r"(Questão\s+\d+\.)", raw_text_prova)
    if len(parts) < 3:
        raise RuntimeError("Não foi possível localizar questões no PDF da prova.")

    items_extracted = []
    pairs = []
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i+1].strip()
        pairs.append((heading, body))

    for heading, body in pairs:
        m = re.search(r"Questão\s+(\d+)\.", heading)
        if not m:
            continue
        
        qnum = int(m.group(1))
        alt_start = re.search(r"\(\s*A\s*\)|A\)", body)
        enunciado = body
        alternatives = {}
        
        if alt_start:
            idx = alt_start.start()
            enunciado = body[:idx].strip()
            alt_block = body[idx:].strip()
            alt_matches = re.findall(r"\(?([A-E])\)?\s*[\.\-]?\s*([^\n(]+(?:\n(?!\(?[A-E]\)?).+)*)", alt_block)
            for lab, txt in alt_matches:
                alternatives[lab] = " ".join(line.strip() for line in txt.splitlines()).strip()
        
        enunciado = re.sub(r"\n{2,}", "\n\n", enunciado).strip()
        items_extracted.append({
            "number": qnum,
            "enunciado": enunciado,
            "alternatives": alternatives if alternatives else None,
        })
    
    items_extracted.sort(key=lambda x: x["number"])
    # --- FIM DO CÓDIGO DE PARSING ORIGINAL ---

    # ==== Processamento Final e Calibração ====
    gabarito_map = dict(re.findall(r"(\d+)\.\s*([A-E])", raw_text_gabarito))
    
    # Gera os valores padrão apenas se não forem fornecidos parâmetros iniciais
    if not initial_params:
        b_values = [round(x, 3) for x in list(numpy.linspace(-2, 2, len(items_extracted)))]

    processed_data = []
    for i, item in enumerate(items_extracted):
        q_num_str = str(item["number"])
        
        # Lógica para definir os parâmetros a, b, c
        if initial_params and q_num_str in initial_params:
            # Cenário 1: Usa os parâmetros fornecidos pelo frontend
            params = initial_params[q_num_str]
            param_a = float(params.get('a', 1.0))
            param_b = float(params.get('b', 0.0))
            param_c = float(params.get('c', 0.2))
        else:
            # Cenário 2: Calcula os parâmetros padrão (fallback)
            param_a = 1.0
            param_b = float(b_values[i])
            num_alts = len(item["alternatives"]) if item["alternatives"] else 0
            param_c = round(1.0 / num_alts, 3) if num_alts > 1 else 0.2

        processed_data.append({
            'original_number': item["number"],
            'enunciado': item["enunciado"],
            'correct_answer': gabarito_map.get(q_num_str),
            'param_a': param_a,
            'param_b': param_b,
            'param_c': param_c,
            'alternatives': item["alternatives"] or {}
        })

    return processed_data