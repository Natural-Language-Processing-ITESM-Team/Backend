from flask import Flask, request, jsonify
import nemo.collections.asr as 
import wget
from os import remove

#Creamos servidor
nemo_server = Flask(__name__)

#Creamos ruta para recibir un link de un audio en un bucket S3
@nemo_server.route("/Nvidia",methods=["POST"])
#Función para transcribir
def Nvidia():
    #Hacemos el request del json
    contenido = request.json
    #Creamos un url con la información recibida
    url=contenido["data"]["audio_response_link"]
    #Descargamos el audio del url
    filename=wget.download(url)
    #Inicializamos el modelo de speech to text
    quartznet=nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name="stt_enes_conformer_ctc_large_codesw")
    #Introducimos el audio en una lista
    files=[filename]
    #Variable raw text para almacenar la transcripción
    raw_text = ''
    print("test")
    #Realizamos la transcipción del audio
    for fname,transcription in zip(files,quartznet.transcribe(paths2audio_files=files)):
        #Almacenamos la transcipción en el string raw_text
        raw_text=transcription
    #Imprimimos para verificar la transcripción
    print(f"Raw text: {raw_text}")
    #Imprimimos para verificar que raw_text se mantuvo como string
    print(f"Type: {type(raw_text)}")
    #Eliminamos el audio para liberar memoria
    remove(filename)
    #Regresamos la transcipción en un json
    return jsonify({"transcripcion":raw_text})
    
#Script para ejecutar el servidor
if __name__ == '__main__':
    nemo_server.run(debug=False,host='0.0.0.0',port='8080')