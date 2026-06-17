# SignalMind AI

Agent IA d'investigation capable de détecter, analyser et expliquer automatiquement des anomalies dans des séries temporelles simulées.

## Objectif

Le projet vise à construire progressivement une architecture agentique capable de :

* générer des séries temporelles simulées ;
* injecter différents types d'anomalies ;
* détecter les anomalies ;
* analyser l'historique ;
* comparer plusieurs signaux ;
* proposer une hypothèse explicative ;
* générer une recommandation.

L'objectif n'est pas seulement de détecter une anomalie, mais également de comprendre son origine et d'expliquer ce qui a pu provoquer le comportement observé.

## Scénario simulé

Le projet simule une usine fabriquant des pièces métalliques pour l'industrie automobile. Une machine de production critique fonctionne en continu pour découper, usiner et assembler des composants métalliques selon la demande.

Lorsque la production augmente, la machine travaille davantage, consomme plus d'énergie et génère plus de chaleur. Un système de refroidissement dédié maintient des conditions de fonctionnement stables afin d'éviter la surchauffe et la dégradation du matériel.

Plusieurs capteurs observent le système en temps réel :

* température ;
* vibration ;
* consommation électrique ;
* activité machine ;
* pression du circuit ;
* débit du liquide de refroidissement ;
* événements système.

Des anomalies sont volontairement injectées dans les signaux, comme des dérives progressives, des ruptures, des changements de régime ou des dégradations de sous-systèmes.

L'objectif est de détecter ces anomalies, d'enquêter sur leur origine et d'expliquer leur cause à partir des signaux observés.

## Workflow

```text
Capteurs 
↓ 
Séries temporelles 
↓ 
Détecteur d'anomalies 
↓ 
Alerte 
↓ 
Agent IA (LangGraph + LLM) 
↓ 
Enquête dynamique 
↓ 
Hypothèse 
↓ 
Recommandation
```

Afin d'éviter qu'un modèle de langage analyse les signaux en continu des milliers de fois par jour, un module déterministe surveille d'abord les séries temporelles.

Par exemple :

* dérive progressive de température ;
* rupture brutale ;
* comportement statistique inhabituel ;
* dépassement de seuil ;
* changement de régime.

Lorsqu'un comportement suspect est détecté, une alerte est envoyée à l'agent. Celui-ci mène alors une enquête en choisissant dynamiquement les outils les plus pertinents selon le contexte observé.

## Installation

Cloner le dépôt :

```bash
git clone <repository-url>
cd signalmind-ai
```

Créer un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Configuration

Le projet utilise actuellement l'API Groq pour exécuter le modèle de langage.

Créer un fichier `.env` à la racine du projet :

```env
GROQ_API_KEY="..."

GROQ_MODEL=qwen/qwen3-32b

GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions

GROQ_TEMPERATURE=0.0

GROQ_MAX_TOKENS=4096
```

La clé API n'est pas fournie dans le dépôt.

## Lancer une simulation

Depuis la racine du projet :

```bash
PYTHONPATH=. python main.py
```

Le système exécute alors les différentes étapes du workflow : simulation, detection et investigation.

## État du projet

Les prochaines évolutions porteront principalement sur la gestion de la mémoire et l'amélioration des outils d'investigation.

