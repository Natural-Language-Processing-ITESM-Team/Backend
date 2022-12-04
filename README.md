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

7. Coneguir claves para servicios.

8. Crear y llenar archivos de credenciales, yo lo hice en la consola con nano pero se puede usar algún otro como vim o emacs.
```bash
touch secrets.env
touch private_key.json
```

9. Descargar el instalador de MiniForge para Linux de nuestra carpeta de Google Drive
```bash
gdown https://drive.google.com/uc?id=1pcs9sN_doO88au-RgMLM0AEk06IG2Pmm
```

10. Instalar MiniForge
```bash
bash Miniconda3-latest-Linux-x86_64.sh
```

11. Descargar el modelo que entrenamos de BertTopic para nuestro proyecto.
```bash
gdown https://drive.google.com/uc?id=15jGkWhx5TH5RBCoIXsgGqX0vGB4IbHyo
```

12. Por alguna razón el BertTopic intentaba usar gpu con cuda, entonces mi solución fue sobreescribir archivos de la biblioteca de 

13. Crear ambiente de anaconda.
```bash
conda create --name back-env
```

14. Activar ambiente
```bash
conda activate
```

15. Instalar paquetes de python
```bash
TODO
```
### Ejecución

Para dejar nuestro proceso corriendo indefinidamente en segundo plano en nuestra "Compute Engine", utilizamos el administrador de procesos pm2.

1. Instalar node
2. instalar pm2
```bash
pm2 start server.py --interpreter python
```

También se puede ejecutar como archivo de python
```bash
python server.py
```

### Autores
Luis Ignacio Ferro Salinas

Rubén Sánchez Mayén