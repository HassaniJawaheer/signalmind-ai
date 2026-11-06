# SignalMind AI

Agent IA d'investigation qui détecte et analyse des anomalies dans les séries temporelles d'une pompe à eau simulée, avec Python, LangGraph et un LLM via l'API Groq.

## Objectif

Le projet associe simulation, détection et investigation pour :

* générer des mesures liées par un modèle physique simplifié ;
* simuler des dégradations progressives ;
* détecter les comportements anormaux ;
* consulter l'historique et calculer des statistiques ;
* formuler des hypothèses et une conclusion explicative.

L'objectif est de dépasser la simple alerte en laissant l'agent choisir les analyses utiles pour comprendre les signaux observés.

## Scénario simulé

Une pompe centrifuge à vitesse variable fait circuler de l'eau dans une boucle fermée. Son moteur électrique est refroidi par ventilation.

Cinq mesures décrivent son fonctionnement :

* température du moteur (°C) ;
* vitesse de rotation (tr/min) ;
* puissance électrique (kW) ;
* pression différentielle entre la sortie et l'entrée (bar) ;
* débit d'eau (m³/h).

La vitesse et la résistance du circuit déterminent le débit et la pression. La puissance dépend du travail hydraulique, tandis que la température évolue selon les pertes du moteur et sa ventilation.

Trois scénarios sont disponibles : fonctionnement normal, restriction du circuit et dégradation de la ventilation. Ce dernier est activé par défaut. Les paramètres se règlent dans [config/pump.py](config/pump.py).

Le modèle est destiné à l'expérimentation et n'est pas calibré sur un équipement réel. Les équations sont décrites dans [la documentation du simulateur](doc/simulation/simulator_model.md).

## Workflow

```text
Simulation de la pompe
↓
Mesure horodatée → ajout au journal JSONL
↓
Détection par règles et seuils
↓
Alerte → investigation LangGraph
↓
LLM → choix d'un outil → résultat → nouvelle décision
↓
Conclusion ou arrêt explicite avec son motif
```

Le détecteur surveille la température ainsi que le débit et la pression rapportés à la vitesse. Le LLM intervient uniquement après une alerte.

L'agent dispose de deux outils : `history` pour consulter les mesures et `statistics` pour les résumer. Le prompt conserve les quatre derniers tours, tandis que le contexte Python garde l'historique complet de l'enquête. Les volumes de données et le nombre de décisions sont limités.

Le programme principal suspend la simulation pendant l'investigation, puis affiche son statut, les observations, les hypothèses et la conclusion disponible avant de s'arrêter.

## Installation

Cloner le dépôt :

```bash
git clone https://github.com/HassaniJawaheer/signalmind-ai.git
cd signalmind-ai
```

Créer un environnement virtuel et installer les dépendances :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Créer un fichier `.env` à la racine du projet :

```env
GROQ_API_KEY="votre_cle_api"
GROQ_MODEL=qwen/qwen3.8-27b
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_TEMPERATURE=0.0
GROQ_MAX_TOKENS=4096
```

L'exemple reprend le modèle utilisé lors des derniers essais ; adapter son identifiant aux modèles accessibles sur votre compte Groq.

Les seuils, les limites de contexte et le délai entre appels se règlent dans [config/settings.py](config/settings.py). Les appels sont espacés de 60 secondes par défaut ; une enquête peut donc prendre plusieurs minutes.

## Lancer une simulation

Depuis la racine du projet :

```bash
bash run.sh
```

Le script active `.venv` et lance `main.py`. Chaque exécution crée un historique de mesures dans `experiments/outputs/jsonl/`, puis déclenche une investigation à la première alerte.

## Exemple de résultat

Lors d'un essai, une alerte à **80,026 °C** a déclenché une enquête. L'agent a effectué quatre appels à `statistics`, puis produit une conclusion à la cinquième décision.

Extrait de la sortie réelle (conclusion abrégée) :

```text
========== INVESTIGATION FINISHED ==========

Status: completed
Stop reason: agent_finished
Final conclusion:
[...] The cause of the temperature increase is most likely the speed increase
itself, but a ventilation issue cannot be definitively excluded. Further
monitoring at the new operating speed is recommended to confirm thermal stability.
```

## Tests

Depuis la racine du projet, avec l'environnement virtuel activé, lancer les tests hors réseau:

```bash
python -m unittest discover
```