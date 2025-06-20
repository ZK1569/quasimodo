# Quasimodo - IOT

Ce projet s’inscrit dans le cadre du cours 8INF924 – Internet des Objets de l’Université du Québec à Chicoutimi. Il a pour objectif la réalisation d’un système de sonnette intelligente capable de détecter une présence devant une porte, d’interagir avec le visiteur, et de notifier à distance l'utilisateur.

La solution proposée repose sur une architecture distribuée composée de deux parties principales : un module embarqué tournant sur un Raspberry Pi 4B et un serveur backend développé avec FastAPI. Le Raspberry se charge de capturer des flux audio et vidéo, d’analyser les signaux de capteurs physiques, et d’envoyer ces données au serveur via WebSocket. Le backend assure la détection faciale, la gestion des interactions vocales, l’envoi de notifications, et l’historique des visites.

L’approche retenue vise à combiner différents domaines techniques tels que la vision par ordinateur, l’audio embarqué, les protocoles WebSocket, ainsi que les API d’intelligence artificielle (OpenAI et ElevenLabs). L’ensemble constitue une plateforme interactive et évolutive permettant d’expérimenter les principes fondamentaux de l’IoT appliqués à un cas concret de sécurité et de domotique.

## Installation
Le système se compose de deux parties distinctes hébergées dans des dépôts Git séparés :
- Le serveur backend, nommé quasimodo : github.com/ZK1569/quasimodo
- Le module embarqué IoT, nommé clochette : github.com/ZK1569/clochette

**1. Installation du serveur backend (quasimodo)**
Commencer par cloner le dépôt, puis créer un environnement virtuel Python :
```bash
git clone https://github.com/ZK1569/quasimodo.git
cd quasimodo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Un fichier .env.example est fourni pour configurer les variables d’environnement, notamment les clés d’API pour OpenAI ou ElevenLabs. Il peut être copié et adapté à l’aide de :
```bash
mv .env.example .env
```

Enfin, lancer le serveur avec la commande :
```bash
python main.py
```

**2. Installation du module IoT (clochette)**
Comme pour le backend, il faut d'abord cloner le projet puis configurer l'environnement virtuel :
```bash
git clone https://github.com/ZK1569/clochette.git
cd clochette
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configurer le fichier .env localement :
```bash
mv .env.example .env
```

Et démarrer l’exécution du module embarqué :

```bash
python main.py
```

**3. Schéma de câblage**
Le câblage des capteurs (caméra, capteur IR, haut-parleur, bouton tactile) sera représenté dans le schéma ci-dessous dès qu’il sera disponible.

(voie schéma de cablage)

## Matériel Utilisé
Dans le cadre de ce projet, un ensemble de composants matériels était mis à disposition selon les spécifications du cours 8INF924. Parmi ces éléments, nous avons sélectionné et utilisé ceux qui répondaient le mieux aux contraintes techniques de la sonnette intelligente. Le développement s’est appuyé sur les composants suivants :
- Raspberry Pi 4B : cœur du système embarqué, chargé de piloter les capteurs, de gérer les flux audio/vidéo et de communiquer avec le backend.
- Caméra Logitech C270 : utilisée pour la détection de présence et la capture du visage du visiteur. Son micro intégré a également été utilisé comme entrée audio.
- Capteur PIR SEN0018 : permet de détecter le mouvement devant la porte et de déclencher les différentes actions du système.
- Capteur tactile capacitif DFR0030 : sert de bouton physique de secours pour déclencher manuellement la sonnette.
- Speaker FIT0449 : prévu initialement pour assurer la sortie audio vers le visiteur.
- DFR0034 - Capteur sonore : disponible, mais non retenu pour l'implémentation finale.

### Limitations rencontrées avec le matériel
Au cours du développement, certains composants se sont révélés inadaptés à l’usage prévu.

Le capteur sonore DFR0034, par exemple, s’est avéré ne pas convenir à la capture vocale : il fournit uniquement un signal de niveau sonore brut, sans capacité à capter ou transmettre un message vocal exploitable. Pour contourner cela, nous avons opté pour l'utilisation du micro intégré à la caméra Logitech C270, bien plus adapté à l’enregistrement de la voix.

Concernant la sortie audio, le speaker FIT0449 a d’abord été considéré comme fonctionnel : nous avons validé son fonctionnement en lui faisant jouer des notes simples, ce qui nous a conduit à croire qu’il pourrait être utilisé pour de la synthèse vocale. Ce n’est qu’à la fin du projet que nous avons réalisé qu’il s’agissait plutôt d’un buzzer, incapable de restituer un flux audio complexe ou un message vocal. Faute de solution de remplacement immédiate, nous avons connecté des écouteurs jack à la Raspberry Pi pour tester et valider la partie audio du projet.

### Composants effectivement utilisés
- Raspberry Pi 4B
-Caméra Logitech C270
-Micro intégré à la caméra
- Capteur PIR SEN0018
- Capteur tactile DFR0030
- Écouteurs jack (remplaçant temporaire du speaker)

## Architecture Logicielle / Fonctionnalités
Le système repose sur une architecture répartie articulée autour de deux grands modules : un module embarqué (Raspberry Pi) pour la capture et la détection locale, et un serveur backend pour le traitement, l’interprétation et la réponse aux événements. Les deux modules communiquent via le protocole WebSocket, ce qui permet une transmission bidirectionnelle en temps réel.

### Communication WebSocket
Initialement, l’objectif était de n’utiliser qu’un unique canal WebSocket pour transmettre à la fois les flux vidéo et audio, ainsi que les événements liés aux capteurs. Cependant, la synchronisation du flux vidéo avec d’autres tâches s’est rapidement révélée instable et difficile à maintenir. La gestion du temps réel, la fréquence des images, et les risques de blocage mutuel entre tâches audio/vidéo rendaient la solution fragile.

Pour améliorer la robustesse et la lisibilité du système, nous avons donc décidé de séparer les canaux de communication en deux WebSockets indépendants :
- Une WebSocket dédiée au flux vidéo
- Une autre WebSocket pour la gestion du flux audio, des messages, et des événements liés aux capteurs

Cette séparation nous a permis de garantir un meilleur découplage des traitements, une gestion plus fluide des erreurs, et une organisation modulaire du backend.

### Traitement sur la WebSocket vidéo
La WebSocket vidéo s'occupe exclusivement de la transmission du flux d'images capturées par la caméra du Raspberry Pi. Voici les étapes de traitement côté serveur :
1. Réception des images : le Raspberry envoie en continu des images encodées à intervalles réguliers.
2. Décodage et traitement : les images sont décodées puis analysées pour détecter la présence d’un visage.
3. Détection faciale : à l’aide de la bibliothèque InsightFace, un encodage du visage est généré.
4. Historisation : si un nouveau visage est détecté, une entrée est ajoutée à l’historique des visites.
5. Déclenchement d’une interaction : selon la présence détectée, une réponse vocale ou une action peut être initiée via la deuxième WebSocket.

### Traitement sur la WebSocket audio/événement
Cette seconde WebSocket centralise les interactions vocales et les signaux provenant des capteurs ou boutons physiques :
1. Détection de mouvement : le Raspberry transmet un signal lorsqu’un mouvement est capté par le capteur PIR.
2. Synthèse vocale : si l'utilisateur n’est pas disponible, le serveur utilise l’API ElevenLabs pour générer un message audio informant le visiteur.
3. Lecture du message : le Raspberry récupère ce fichier audio et le joue (via écouteurs).
4. Capture vocale du visiteur : le visiteur peut alors laisser un message via le micro de la caméra.
5. Transcription : le fichier audio est envoyé à l’API OpenAI Whisper pour être transcrit en texte.
6. Notification distante : la transcription du message est envoyée à l’utilisateur (via Discord, par exemple).

## Pistes d’Amélioration
Bien que le prototype actuel remplisse les principales fonctionnalités attendues, il reste plusieurs limitations techniques et possibilités d’amélioration à envisager pour une version plus aboutie ou déployable à l’échelle.

### Perspectives d’amélioration
Plusieurs pistes d’amélioration ont été identifiées pour corriger ces limites et enrichir le système :
- Refonte de la gestion audio avec un véritable module amplificateur (ex. : PAM8403) et un haut-parleur adapté à la restitution vocale.
- Ajout d’un modèle de détection local pour affiner les déclenchements (par exemple, corriger les faux positifs du capteur PIR en combinant plusieurs signaux).
- Mise en place d’une architecture multi-utilisateurs, permettant à chaque instance de clochette d’être associée à un compte utilisateur distinct, avec authentification, historique dédié, et notifications personnalisées.
- Gestion asynchrone optimisée des composants sur le Raspberry (caméra, capteurs, microphone) pour améliorer la stabilité générale du système.
- Interface web ou mobile permettant de visualiser l’historique des visites, de configurer les messages, ou d’interagir à distance avec le visiteur en temps réel.
- Éventuelle suppression des dépendances cloud par l'intégration de modèles open-source exécutés en local, si les ressources matérielles le permettent.
