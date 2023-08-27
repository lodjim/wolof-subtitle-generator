# Wolof Subtitles Generator API

Wolof Subtitles Generator permet de générer des sous-titres en wolof pour des fichiers audio et de créer des vidéos avec les sous-titres incrustés. L'API utilise le modèle de traitement automatique du langage naturel [whisper-small-wolof](https://huggingface.co/cifope/whisper-small-wolof) pour générer les transcriptions et les sous-titres.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants :

1. **Système d'exploitation Linux**: Cette API a été conçue pour fonctionner sur un système d'exploitation Linux.

2. **ffmpeg**: Assurez-vous que le logiciel `ffmpeg` est installé sur votre système. Cet outil est nécessaire pour le traitement audio et vidéo. Si vous ne l'avez pas déjà installé, vous pouvez le faire en utilisant la commande suivante :

   ```bash
   sudo apt-get install ffmpeg
   ```

3. **Dépendances Python**: Installez les dépendances Python nécessaires en exécutant la commande suivante :

   ```bash
   python3 -m venv env 
   source env/bin/activate
   pip install -r requirements.txt
   ```
4. **Dépendances Modele**: Téléchargez le modèle directement depuis google drive à l'aide de la commande gdown :
   
   ```bash
   pip3 install gdown
   cd whisper-wolof
   gdown "https://drive.google.com/uc?id=1MYfZ0oyCjZZ2z3h0S_cTNC17hzqS2rAF"
   ```

## Configuration

La configuration de l'API peut être ajustée en modifiant les paramètres dans le fichier `main.py`.

- `host`: L'adresse IP sur laquelle l'API écoutera les requêtes. Par défaut, elle est configurée pour écouter sur toutes les interfaces réseau (`0.0.0.0`).
- `port`: Le port sur lequel l'API écoutera les requêtes. Par défaut, le port est `8080`.
- `model`: Le chemin vers le modèle Whisper à utiliser pour la génération de sous-titres. Par défaut, le chemin est configuré pour utiliser `./whisper-wolof`.
- `device`: L'appareil à utiliser pour l'inférence du modèle. Par défaut, l'appareil est configuré pour utiliser le CPU (`cpu`).

## Utilisation

1. Lancez l'API en exécutant la commande suivante :

   ```bash
   python main.py --host <adresse_ip> --port <port> --model <chemin_du_modele> --device <cpu_ou_gpu>
   ```

   Remplacez `<adresse_ip>`, `<port>`, `<chemin_du_modele>` et `<cpu_ou_gpu>` par les valeurs appropriées.

2. Faites une requête POST à l'URL `http://<adresse_ip>:<port>/makevideo` en envoyant un fichier audio en tant que champ de formulaire `upload_file`. L'API générera les sous-titres en wolof et retournera un objet JSON contenant les informations sur les sous-titres générés et le lien vers la vidéo avec les sous-titres.

 ```bash
   curl -X 'POST' \
  'http://0.0.0.0:8080/makevideo' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'upload_file=@test1.wav;type=audio/wav'
 ```

 ```json
   {
   "srt": "1\n00:00:00,000 --> 00:00:05,794\ndem na bé ne ma ke ma ak moom foog na ne raba ko jàpp\n\n",
   "text": "dem na bé ne ma ke ma ak moom foog na ne raba ko jàpp\n",
   "video_path": "https://0.0.0.0:8080/static/video/dae6d5c4-feee-48b0-a39a-f325d07595bc-video.mp4"
   }
 ```
3. Voir la documentation de l'api sur `http://<adresse_ip>:<port>/docs`

## Utilisation Libre

Ce projet est libre et peut être utilisé à des fins commerciales. Vous êtes libre de l'utiliser, de le modifier et de le distribuer selon vos besoins.

## Remarque

Assurez-vous d'avoir les droits nécessaires pour l'utilisation des fichiers audio et vidéo, ainsi que pour l'accès au modèle Whisper. Cette API a été conçue pour fonctionner exclusivement sur des systèmes d'exploitation Linux en raison de sa dépendance à `ffmpeg`.

N'hésitez pas à contacter [Djim Momar Lo](https://github.com/lodjim) pour toute question ou préoccupation concernant cette API.
