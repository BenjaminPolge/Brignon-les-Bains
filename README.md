# Brignon-les-Bains — Agent municipal « Brigitte »

> ⚠️ **DÉMONSTRATION UNIQUEMENT.** Ce dépôt est une **démonstration d'un agent IA construit en CLI** (avec `agents-cli`, l'outil en ligne de commande de Google fondé sur l'ADK). Ce n'est **pas un service en production**. **Brignon-les-Bains est une commune fictive** : la ville thermale, ses habitants, ses services et tous les documents produits par l'agent sont imaginaires et n'ont **aucune valeur légale ou administrative**.

## Description

« Brigitte » est un agent conversationnel de service public qui simule l'accueil numérique de la mairie (fictive) de Brignon-les-Bains, petite commune thermale imaginaire des Cévennes ardéchoises.

L'agent :

- répond aux questions des usagers en s'appuyant sur les pages du site web de la commune (recherche documentaire) ;
- classe les demandes par thématique municipale ;
- accompagne pas à pas les démarches administratives (rendez-vous, réservation de salle, inscription scolaire, état civil, signalement de voirie) ;
- génère des **documents administratifs fictifs** (convocations, arrêtés, récépissés, acte de naissance, etc.) au format PDF, clairement estampillés comme sans valeur.

Le dépôt contient également le **site web statique** (HTML/CSS/JS à la racine et dans `assets/`) que l'agent interroge, ainsi qu'une **suite d'évaluation** (`tests/eval/`).

## Pile technique

| Élément | Rôle |
| --- | --- |
| **agents-cli** (`google-agents-cli`) | Outil CLI de scaffolding et de cycle de vie de l'agent |
| **Google ADK** (Agent Development Kit) | Framework d'exécution de l'agent (`google-adk[gcp]`) |
| **Gemini** | Modèle de langage (`gemini-flash-latest`) |
| **FastAPI** | Serveur backend de l'agent |
| **Protocole A2A** (`a2a-sdk`) | Interopérabilité entre agents |
| **reportlab** | Génération des PDF fictifs |
| **uv** | Gestion des dépendances et exécution Python |

## Structure du projet

```
Brignon-les-Bains/
├── app/                    # Code de l'agent
│   ├── agent.py            # Définition de l'agent « Brigitte » (instructions, modèle, outils)
│   └── tools.py            # Outils : recherche doc, classification, démarches, génération PDF
├── tests/
│   ├── unit/               # Tests unitaires
│   ├── integration/        # Tests d'intégration (agent + serveur)
│   └── eval/               # Suite d'évaluation (datasets, métriques, config)
├── assets/                 # CSS, JS, images et documents du site
├── *.html                  # Pages du site municipal fictif (index, démarches, horaires…)
├── GEMINI.md               # Guide de développement assisté par IA
├── pyproject.toml          # Dépendances et configuration du projet
└── .env.example            # Modèle de configuration (SANS clé API)
```

## Prérequis

- **uv** — gestionnaire de paquets Python — [installation](https://docs.astral.sh/uv/getting-started/installation/)
- **agents-cli** — installer avec `uv tool install google-agents-cli`
- Une **clé API Gemini** (voir la section Configuration ci-dessous)

## Configuration : votre propre clé API

> 🔑 **Le dépôt ne contient volontairement AUCUNE clé API.** Vous devez fournir la vôtre.

Copiez le modèle fourni, puis renseignez vos identifiants :

```bash
cp .env.example .env
```

Éditez ensuite `.env`. Deux options sont possibles :

- **Vertex AI** (par défaut) : renseignez `GOOGLE_CLOUD_PROJECT` et `GOOGLE_CLOUD_LOCATION`.
- **Gemini API via Google AI Studio** : commentez les lignes Vertex AI et renseignez `GEMINI_API_KEY=votre-cle`.

## Démarrage rapide

Installer `agents-cli` et ses composants (si ce n'est pas déjà fait) :

```bash
uvx google-agents-cli setup
```

Installer les dépendances du projet :

```bash
agents-cli install
```

Lancer l'agent dans un environnement local (playground web, rechargement automatique) :

```bash
agents-cli playground
```

## Tests

Lancer les tests unitaires et d'intégration :

```bash
uv run pytest tests/unit tests/integration
```

## Commandes utiles

| Commande | Description |
| --- | --- |
| `agents-cli install` | Installe les dépendances via uv |
| `agents-cli playground` | Lance l'environnement de développement local |
| `agents-cli lint` | Vérifie la qualité du code |
| `agents-cli eval` | Évalue le comportement de l'agent (voir `agents-cli eval --help`) |
| `uv run pytest tests/unit tests/integration` | Exécute les tests unitaires et d'intégration |

## Développement

Modifiez la logique de l'agent dans `app/agent.py` et ses outils dans `app/tools.py`, puis testez avec `agents-cli playground` (rechargement à chaque sauvegarde). Le fichier `GEMINI.md` documente le flux de développement assisté par IA (phases de build, boucle d'évaluation, tests avant déploiement).

---

*Projet de démonstration. Commune, services et documents entièrement fictifs — sans valeur administrative ou juridique.*
