
# Modèle interne du simulateur

Dans un contexte industriel, les signaux observés par les capteurs sont la conséquence d’un état physique sous-jacent. Une hausse de température ou une augmentation des vibrations n’apparaît pas spontanément. Ces comportements sont généralement provoqués par une cause interne, comme une augmentation de charge, une usure progressive, une baisse d’efficacité d’un sous-système ou l’apparition d’une panne.

Je propose donc une approche en deux niveaux :

```text
Variables internes cachées
↓
Lois internes du système
↓
Capteurs
↓
Séries temporelles observées
↓
Détection
↓
Agent IA
```

L’agent ne voit jamais l’état interne réel du système. Il observe uniquement les conséquences visibles produites par les capteurs et doit reconstruire une explication à partir des signaux observés.


## Variables internes cachées

### Charge machine

```text
load
```

Représente la demande de production actuelle.

Exemple :

```text
20%
40%
80%
```

Effets possibles :

* consommation augmente
* chaleur produite augmente
* sollicitation machine augmente

### Santé machine

```text
health
```

Représente l’état général du système.

Exemple :

```text
100 → machine saine
40 → système dégradé
```

Effets possibles :

* perte de performance
* consommation légèrement plus élevée
* comportements instables

### Usure mécanique

```text
wear
```

Représente le vieillissement progressif des composants.

Exemple :

```text
0.1
0.4
0.8
```

Effets possibles :

* vibration augmente
* rendement diminue
* consommation augmente légèrement

### Température interne réelle

```text
core_temperature
```

Température réelle interne de la machine.

Les capteurs ne mesurent qu’une approximation bruitée.

### Efficacité du refroidissement

```text
cooling_efficiency
```

Détermine la capacité du système à évacuer la chaleur.

Exemple :

```text
1.0
0.8
0.5
```

Effets possibles :

* température augmente
* ventilateur compense
* consommation augmente

### Vitesse ventilateur

```text
fan_speed
```

Permet d’adapter automatiquement le refroidissement.

Exemple :

```text
800 rpm
1500 rpm
2500 rpm
```

### Débit liquide

```text
flow_rate
```

Quantité de liquide circulant dans le circuit.

Une fuite ou une dégradation de la pompe peut réduire ce débit.

### Pression circuit

```text
pressure
```

Représente l’état du circuit de refroidissement.

Une baisse peut révéler :

* fuite
* pompe dégradée
* problème système

## Principe de simulation

*Les anomalies ne modifient jamais directement les capteurs.*

Par exemple, interdit de faire :

```text
temperature += 20
```

On modifie une cause interne :

```text
cooling_efficiency : 1 → 0.6
```

Puis le système réagit naturellement. Par exemple :

```text
refroidissement ↓
↓
température ↑
↓
ventilateur ↑
↓
consommation ↑
```
