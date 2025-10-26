import os
import re
import csv
import io
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from datetime import datetime

from parsers import clean_text, extract_euro_prices, SITE_HINTS

app = Flask(__name__)
CORS(app)

DEFAULT_MAX_LINKS = 12
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}


def build_query(term: str, tipo: str) -> str:
    term = term.strip()
    if tipo == "produtos":
        domains = ["worten.pt", "fnac.pt", "kuantokusta.pt", "pcdiga.com", "globaldata.pt"]
    elif tipo == "hoteis":
        domains = ["booking.com", "trivago.pt", "expedia.com", "hotels.com"]
    else:
        domains = []  # genérico
    if domains:
        domain_filter = " OR ".join([f"site:{d}" for d in domains])
        return f"{term} {domain_filter}"
    return term


def fetch_text(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "img"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
        return clean_text(text)
    except Exception:
        return ""


def score_result(url: str, price: float, term: str) -> float:
    """Heurística simples: menor preço e domínio mais relevante."""
    host = urlparse(url).netloc
    base = price
    for weight, domain in [(0.98, "worten.pt"), (0.985, "fnac.pt"), (0.99, "kuantokusta.pt"),
                           (0.985, "booking.com"), (0.99, "trivago.pt"), (0.992, "expedia.com")]:
        if domain in host:
            base *= weight
            break
    if term.lower().replace(" ", "-") in url.lower():
        base *= 0.995
    return base


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json(force=True)
    term = data.get("term", "").strip()
    tipo = data.get("tipo", "generico").strip().lower()
    max_links = int(data.get("max_links", DEFAULT_MAX_LINKS))

    if not term:
        return jsonify({"ok": False, "error": "Termo vazio."}), 400

    query = build_query(term, tipo)

    try:
        urls = list(search(query, num_results=max_links))
    except Exception as e:
        return jsonify({"ok": False, "error": f"Falha na pesquisa: {e}"}), 500

    results = []
    for url in urls:
        text = fetch_text(url)
        if not text:
            continue
        hint = SITE_HINTS.get(tipo, None)
        prices = extract_euro_prices(text, hint_words=hint)
        if not prices:
            continue
        best_price = min(prices)
        score = score_result(url, best_price, term)
        results.append({
            "url": url,
            "price": round(best_price, 2),
            "score": round(score, 4)
        })

    if not results:
        return jsonify({"ok": False, "items": [], "message": "Nenhum preço encontrado."})

    results.sort(key=lambda x: x["score"])
    best = results[0]

    return jsonify({
        "ok": True,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "query": {"term": term, "tipo": tipo, "max_links": max_links},
        "items": results,
        "best": best
    })


@app.route("/api/export_csv", methods=["POST"])
def export_csv():
    data = request.get_json(force=True)
    items = data.get("items", [])
    if not items:
        return jsonify({"ok": False, "error": "Sem dados."}), 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["URL", "Preço (€)", "Score"])
    for it in items:
        writer.writerow([it.get("url", ""), it.get("price", ""), it.get("score", "")])
    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="resultados.csv")


@app.route("/", methods=["GET"])
def root():
    return jsonify({"ok": True, "service": "PrecoFinder API", "status": "online"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))