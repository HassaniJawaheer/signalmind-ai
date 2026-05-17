# SignalMind AI

Agent IA d'investigation pour détecter, analyser et expliquer automatiquement des anomalies dans des séries temporelles simulées.

## Objectif

Le projet vise à construire progressivement une architecture agentique capable de :
- générer des séries temporelles simulées ;
- injecter différents types d'anomalies ;
- détecter les anomalies ;
- analyser l'historique ;
- comparer plusieurs signaux ;
- proposer une hypothèse explicative ;
- générer une recommandation.

## Scénario simulé

Le projet simule une usine fabriquant des pièces métalliques pour l’industrie automobile. Une machine de production critique fonctionne en continu pour découper, usiner et assembler des composants métalliques selon la demande.

Lorsque la production augmente, la machine travaille davantage, consomme plus d’énergie et génère plus de chaleur. Un système de refroidissement dédié maintient des conditions de fonctionnement stables afin d’éviter la surchauffe et la dégradation du matériel.

Plusieurs capteurs observent le système en temps réel :

* température
* vibration
* consommation électrique
* activité machine
* pression du circuit
* débit du liquide de refroidissement
* événements système

Des anomalies sont volontairement injectées dans les signaux, comme des dérives progressives, des ruptures, des changements de régime ou des dégradations de sous-systèmes.

L’objectif est de détecter des anomalies, d’enquêter sur leur origine et d’expliquer leur cause à partir des signaux observés.

## Workflow agentique

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
Pour éviter que le LLM analyse les signaux en continu des milliers de fois par jour, un **module déterministe** de détection d’anomalies surveille d’abord les séries temporelles. Par exemples

* dérive progressive de température
* rupture brutale
* comportement statistique inhabituel
* dépassement de seuil
* changement de régime

Lorsqu’un comportement suspect est détecté, une alerte est envoyée à l’agent. L’agent mène alors une enquête en choisissant dynamiquement les outils les plus pertinents selon le contexte observé.
