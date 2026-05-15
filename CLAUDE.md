# Projet Veille IA Gouvernance — Instructions Claude

## Profil de l'utilisateur

Guillaume Dubois-Gordeeff, moins de 40 ans.

**Parcours** :
- 6 ans de conseil en stratégie (Bain & Company, Kurt Salmon, BearingPoint)
- 2 ans Chief of Staff
- 4,5 ans Directeur des Opérations
- Expertise sectorielle TMT (Webedia)
- Certifications IA : Google AI Professional Certificate, Anthropic Academy, DeepLearning.AI

**Projet "administrateur"** : se positionner comme candidat board member indépendant pour des sociétés de plus de 50 salariés. Conviction centrale : les conseils d'administration sont composés de profils seniors (moyenne ~61 ans), peu opérationnels et démunis face à l'IA et aux usages des jeunes générations (Gen Z, Millennials). Guillaume incarne le profil complémentaire : opérationnel, digital, IA-natif, connecté aux nouvelles générations.

**Cible LinkedIn** : actionnaires et dirigeants d'entreprises de plus de 10 salariés.

---

## Commande principale : "Génère mon briefing"

Quand l'utilisateur dit "génère mon briefing" (ou formulation proche), tu dois :

### 1. Trouver le fichier de la semaine
Lire le fichier le plus récent dans le dossier `briefings/` dont le nom se termine par `_raw.json`.

### 2. Analyser et sélectionner
Parmi tous les articles collectés :
- Identifier les **5 articles les plus pertinents** pour la gouvernance de l'IA en entreprise
- Priorité aux articles concernant : réglementation IA, rôle des boards face à l'IA, risques et responsabilités des dirigeants, adoption de l'IA en entreprise, publications des acteurs majeurs (Anthropic, OpenAI, DeepMind)
- Écarter les articles trop techniques (recherche pure), trop grand public, ou déjà traités
- Classer par **ordre d'importance décroissant** pour un dirigeant d'entreprise

### 3. Rédiger le briefing

Format exact à respecter :

---

**VEILLE IA GOUVERNANCE — Semaine du [date]**

---

**1. [Titre court et percutant]**
[Une phrase simple, claire, sans jargon, qui explique l'actualité et pourquoi elle compte pour un dirigeant.]
Source : [Nom de la source] → [URL directe vers l'article]

**2. [Titre]**
[Une phrase.]
Source : [Nom] → [URL]

*(répéter jusqu'à 5)*

---

**3 ANGLES LINKEDIN POUR VOTRE PROJET ADMINISTRATEUR**

Ces angles doivent exploiter le positionnement de Guillaume : executive < 40 ans, opérationnel, expert IA, pont entre direction et nouvelles générations.

**Angle 1 — [Titre accrocheur]**
[2-3 phrases : l'idée centrale du post/carrousel, pourquoi ça parle à votre cible (dirigeants, actionnaires), et comment ça renforce votre positionnement board member.]

**Angle 2 — [Titre]**
[2-3 phrases.]

**Angle 3 — [Titre]**
[2-3 phrases.]

---

### 4. Après le briefing
Proposer à l'utilisateur :
- "Voulez-vous que je développe l'un de ces angles en plan détaillé de post LinkedIn ?"
- "Souhaitez-vous approfondir l'un des articles ?"

---

## Gestion des sources

Le fichier `sources.json` liste toutes les sources de veille.
- Pour **ajouter une source** : l'utilisateur peut dire "ajoute [nom] avec l'adresse [url]"
- Pour **désactiver une source** : mettre `"active": false` dans sources.json
- Chaque source a une catégorie : `gouvernance`, `ia-acteurs`, `ia-recherche`

## Mémoire

Le fichier `memory.json` liste les URLs déjà traitées. Ne jamais recommander un article dont l'URL figure dans cette liste.
