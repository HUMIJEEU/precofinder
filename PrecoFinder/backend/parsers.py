import re

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.replace("€ ", "€ ").replace(" €", " €")
    return text

def extract_euro_prices(text: str, hint_words=None):
    """
    Extrai preços em euros. Formatos: 1.234,56 € | 1.234€ | 1234.56€ | 1 234 €
    hint_words: lista opcional de palavras que devem estar perto do preço para considerar válido.
    """
    euro_regex = r"(?:€\s*|\b)(\d{1,3}(?:[\.\s]\d{3})*(?:[\.,]\d{2})|\d+(?:[\.,]\d{2})?|\d{1,3})(?=\s*€)"
    candidates = []

    if hint_words:
        window = 80
        for m in re.finditer(r".{0,%d}€\s*\d[\d\.,\s]*.{0,%d}" % (window, window), text):
            chunk = m.group(0)
            if any(hw.lower() in chunk.lower() for hw in hint_words):
                for n in re.finditer(euro_regex, chunk):
                    candidates.append(n.group(1))
    else:
        for m in re.finditer(euro_regex, text):
            candidates.append(m.group(1))

    prices = []
    for raw in candidates:
        v = raw.strip()
        v = v.replace(" ", "")
        if "," in v and "." in v:
            v = v.replace(".", "").replace(",", ".")
        elif "," in v and "." not in v:
            v = v.replace(",", ".")
        try:
            num = float(v)
            if 0.5 <= num <= 100000:
                prices.append(num)
        except ValueError:
            continue
    return prices

SITE_HINTS = {
    "produtos": ["preço", "€", "comprar", "adicionar", "produto", "carrinho"],
    "hoteis": ["noite", "estadia", "quarto", "tarifa", "€"],
    "generico": None
}