# PreçoFinder — Comparador de Preços (PC + Telemóvel, PWA)

**Desenvolvido por Hugo Eugénio**  
Repositório: https://github.com/HUMIJEEU/precofinder

Aplicação Web responsiva e PWA para pesquisar automaticamente **produtos**, **hotéis** e **termos genéricos**, extraindo preços em €, ordenando e destacando o **melhor preço**. Inclui **alerta de preço** (valor alvo).

## Estrutura
```
/backend   → API Flask (Render)
/frontend  → Site/PWA (Netlify)
```

## Deploy rápido
- Backend (Render): ver `/backend/README_RENDER_WINDOWS.md`
- Frontend (Netlify): ver `/frontend/README_NETLIFY_WINDOWS.md`

## Notas
- Alguns sites podem bloquear scraping ou exigir APIs oficiais; este projeto é educativo.
- Para produção, considera **SerpAPI / Google Custom Search** e parsers por domínio.