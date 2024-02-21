from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from PyPDF2 import PdfReader
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Configura tu API key de OpenAI
openai.api_key = "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"

@app.route("/convertir_a_binario", methods=["POST"])
def convertir_a_binario():
    print(request.form)
    try:
        numero_decimal = int(request.form["numero_decimal"])
        
        # Consultar a OpenAI para generar una respuesta basada en el número decimal
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Convertir el número decimal {numero_decimal} a binario."}
            ]
        )
        respuesta_binaria = respuesta['choices'][0]['message']['content'].strip()
        print("el pdf es",pdf_text)
        return jsonify({"numero_binario": respuesta_binaria})
    except ValueError:
        return jsonify({"error": "Entrada inválida. Proporciona un número decimal válido."})

@app.route("/procesar_pdf", methods=["POST"])
def procesar_pdf():
    try:
        # Obtén el archivo PDF del formulario de solicitud
        pdf_file = request.files["pdf_file"]
        
        # Lee el archivo PDF
        pdf_reader = PdfReader(BytesIO(pdf_file.read()))
        
        # Extrae el texto del PDF
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Divide el texto en segmentos de 1000 caracteres
        segments = [text[i:i+1000] for i in range(0, len(text), 1000)]
        
        # Procesa cada segmento con la API de OpenAI
        responses = []
        for segment in segments:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": segment}
                ]
            )
            responses.append(response['choices'][0]['message']['content'].strip())
        
        return jsonify({"responses": responses})
    except Exception as e:
        return jsonify({"error": str(e)})

pdf_text = ""

@app.route("/cargar_pdf", methods=["POST"])
def cargar_pdf():
    try:
        # Verificar si se envió un archivo en la solicitud
        if 'pdf_file' not in request.files:
            return jsonify({"error": "No se proporcionó ningún archivo PDF"}), 400
        
        # Obtener el archivo PDF del formulario de solicitud
        pdf_file = request.files["pdf_file"]

        # Leer el contenido del archivo PDF como bytes
        pdf_content = pdf_file.read()
        
        # Verificar si el archivo PDF está vacío
        if len(pdf_content) == 0:
            return jsonify({"error": "El archivo PDF está vacío"}), 400
        
        # Crear un objeto BytesIO con el contenido del archivo PDF
        pdf_buffer = BytesIO(pdf_content)
        
        # Crear el lector de PDF
        pdf_reader = PdfReader(pdf_buffer)
        
        # Extraer el texto del PDF
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        
        print(pdf_text)
        return jsonify({"status": "PDF cargado correctamente", "pdf_text": pdf_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hacer_pregunta", methods=["POST"])
def hacer_pregunta():
    try:
        # Obtén la pregunta y el texto del PDF del formulario de solicitud
        pregunta = request.form["pregunta"]
        pdf_text = request.form["pdf_text"]
        
        print('Pregunta recibida:', pregunta)  # Imprimir la pregunta en la consola
        print('Texto del PDF recibido:', pdf_text)  # Imprimir el texto del PDF en la consola
        
        # Consulta a OpenAI para generar una respuesta basada en el texto del PDF y la pregunta
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": pdf_text},
                {"role": "user", "content": pregunta}
            ]
        )
        respuesta_texto = respuesta['choices'][0]['message']['content'].strip()
        
        print('Respuesta generada:', respuesta_texto)  # Imprimir la respuesta en la consola
        
        return jsonify({"respuesta": respuesta_texto})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
