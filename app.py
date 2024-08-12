from flask import Flask, render_template, request, redirect, url_for
import os
import openai
import requests
import json

app = Flask(__name__)

api_key = os.getenv('OPENAI_API_KEY')
# Inicialize o cliente OpenAI com a chave API
openai.api_key = api_key

# Pasta onde as imagens serão armazenadas
UPLOAD_FOLDER = '/app/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração para permitir apenas certos tipos de arquivo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def formatar_dados(dados):
    return json.dumps(dados, indent=4, ensure_ascii=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analisa_imagem(filepath):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    with open(filepath, "rb") as image_file:
        img_data = image_file.read()

    files = {
        'file': (os.path.basename(filepath), img_data)
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "me diga o que está escrito na placa desse carro. O padrão sempre será 3 letras seguido de um número. Os demais caracteres podem variar, mas os 3 primeiros obrigatoriamente devem ser letras e o quarto caractere deve ser um número. Leve isso em conta em sua análise. Me responda apenas com a placa no seguinte formato: NNN0XXX - sendo a letra 'N' correspondente a alguma letra, o '0' correspondente a algum número e a letra 'X' correspondente a qualquer outro caractere que você identificar."
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    resp = response.json()

    resposta = resp['choices'][0]['message']['content']
    url = f"https://wdapi2.com.br/consulta/{resposta}/1c192c007ea240de7a6d5d57bea000c7"
    
    dados = requests.get(url)
    carro = dados.json()
    return carro

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('upload_file'))

        # Verifica se o post request tem o arquivo
        if 'file' not in request.files:
            return "Nenhum arquivo selecionado"

        file = request.files['file']

        # Se o usuário não selecionar nenhum arquivo, o browser envia um arquivo vazio sem nome
        if file.filename == '':
            return "Nenhum arquivo selecionado"

        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Exibe a URL da imagem
            image_url = url_for('static', filename=f'uploads/{filename}', _external=True)
            
            # Envia a imagem para análise
            dados = analisa_imagem(filepath)
            
            return render_template('upload.html', dados_formatados=dados, image_url=image_url)
        
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
