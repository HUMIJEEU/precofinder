# Deploy do Backend (Flask) no Render — Windows

1. **Repositório GitHub**: https://github.com/HUMIJEEU/precofinder
2. Cria conta em **https://render.com** e clica em **New > Web Service**.
3. Liga o Render ao teu GitHub e escolhe o repositório `precofinder`, pasta **/backend**.
4. Configuração:
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Port: **5000**
5. Deploy. O Render vai gerar um domínio do tipo:
   `https://melhorprecofinder.onrender.com` (ou semelhante).
6. Testa a API: abre no browser o domínio — deves ver `{"service":"PrecoFinder API","status":"online"}`.