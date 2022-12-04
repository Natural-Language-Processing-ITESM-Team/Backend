# Backend
Repositorio de Backend para el equipo NLP ITESM

### Descripción
En este repositorio está el código que integra a todos los componentes del proyecto HERA, y procesa la iformación de forma adecuada para servir al cliente en página web, en Whatsapp y Messenger.

Para ver las configuraciones individuales de los servicios en la nube que utilizamos, refiérase al repositorio de [wiki](https://github.com/Natural-Language-Processing-ITESM-Team/Wiki/wiki)

### Instalación (Linux Debian 11)
Esta instalación la hice directamente en la "Compute Engine" de Google que tiene Linux Debian.

1. Actualizar "Advanced Package Tool" (apt)
```
sudo apt update
sudo apt upgrade
```

2. Instalar git
```
sudo apt install git
```

3. Clonar repositorio de Backend
```bash
git clone https://github.com/Natural-Language-Processing-ITESM-Team/Backend.git
```

4. Entrar a directorio con código de Backend.
```bash
cd Backend
```

5. La compute engine ya viene con python 3.7, entonces solamente fue necesario instalar pip para administrar los paquetes de python.
```
sudo apt-get install pip
```

6. Instalar ffmpeg en la consola de Linux (para convertir formatos de audio)
```bash
sudo apt install ffmpeg
```

7. Conseguir claves para servicios.

Para conseguir las claves para diferentes servicios de nube, se explica el proceso más detallado en la [wiki](https://github.com/Natural-Language-Processing-ITESM-Team/Wiki/wiki). 
Cuando se tengan todas las claves, se debe generar un archivo "private_key.json", y un archivo "secrets.env", ambos archivos deben de estar colocados en el directorio Backend.

Los contenidos del archivo "private_key.json" se explican en la [wiki](https://github.com/Natural-Language-Processing-ITESM-Team/Wiki/wiki) pero los contenidos del archivo "secrets.env" deben ser los siguientes, sustituyendo en cada clave el valor correspondiente.
```
# Amazon keys
AWS_ACCESS_KEY_ID=<>
AWS_SECRET_ACCESS_KEY=<>
AWS_SESSION_TOKEN=<>
REGION_NAME=<>
RDS_PASS=<>

# IBM keys
IAM_AUTHENTICATOR=<>
ASSISTANT_ID=<>
WATSON_STT_URL=<>
WATSON_STT_KEY=<>
WATSON_TTS_KEY=<>
WATSON_TTS_URL=<>

# Azure keys
AZURE_SPEECH_KEY=<>
AZURE_SPEECH_REGION=<>

# Whatsapp keys
WHATSAPP_ACCESS_TOKEN=<>
PAGE_ACCESS_TOKEN=<>
VERIFY_TOKEN=<>
PAGE_ID=<>
WHATSAPP_NUMBER=<>
TOKEN=<>
```

8. Crear y llenar archivos de credenciales, yo lo hice en la consola con nano pero se puede usar algún otro como vim o emacs.
```bash
touch secrets.env
touch private_key.json
```

9. Instalar gdown con pip para descargar archivos desde Google Drive porque el modelo era tan pesado que no se puede subir a Github.
```bash
pip install gdown
```

10. Descargar el instalador de MiniForge para Linux de nuestra carpeta de Google Drive
```bash
gdown https://drive.google.com/uc?id=1pcs9sN_doO88au-RgMLM0AEk06IG2Pmm
```

1Instalar MiniForge
```bash
bash Miniconda3-latest-Linux-x86_64.sh
```

12. Descargar el modelo que entrenamos de BertTopic para nuestro proyecto.
```bash
gdown https://drive.google.com/uc?id=15jGkWhx5TH5RBCoIXsgGqX0vGB4IbHyo
```

13. Crear ambiente de anaconda.
```bash
conda create --name back-env
```

14. Activar ambiente
```bash
conda activate back-env
```

15. Instalar paquetes de python
```bash
TODO
```

16. Por alguna razón el BertTopic intentaba usar gpu con cuda, entonces mi solución fue sobreescribir archivos de la biblioteca de torch, en las partes donde se indica el "device", yo escribía explícitamente "cpu".
Ejemplos de archivos que tuve que sobreescribir
* /home/a01378248/miniconda3/envs/back-env/lib/python3.7/site-packages/torch/nn/modules
module.py en la función "convert"
* /home/a01378248/miniconda3/envs/back-env/lib/python3.7/site-packages/sentence_transformers
util.py
En la función "batch_to_device"

### Ejecución

Para dejar nuestro proceso corriendo indefinidamente en segundo plano en nuestra "Compute Engine", utilizamos el administrador de procesos pm2.

1. Instalar node
```bash
sudo apt install nodejs npm -y
```
2. instalar pm2
```bash
npm install pm2 -g
```
3. Encender proceso de servidor en segundo plano.
```bash
pm2 start server.py --interpreter python
```

También se puede ejecutar como archivo de python (esta forma la utilizábamos para depurar)
```bash
python server.py
```

### Autores
Luis Ignacio Ferro Salinas [Perfil de LinkedIn](https://www.linkedin.com/in/luis-ferro10192000/)

Rubén Sánchez Mayén