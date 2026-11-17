# Newsletter EDF — veille hebdomadaire

Ce dépôt publie une synthèse courte en français de l'actualité du **Groupe EDF à l'échelle mondiale**.

## Fonctionnement

- Exécution automatique chaque lundi à 06:00 UTC (07:00 à Paris en hiver, 08:00 en été).
- Déclenchement manuel possible depuis l'onglet **Actions**.
- Collecte d'articles publiés au cours des 7 derniers jours via Google News RSS, avec priorité aux sources officielles et médias économiques/énergie reconnus.
- Synthèse en français par IA, avec liens et dates des sources.
- Publication dans `newsletters/AAAA-MM-JJ.md`.

## Configuration requise

Dans **Settings → Secrets and variables → Actions**, ajouter le secret :

- `OPENAI_API_KEY` : clé API OpenAI utilisée pour rédiger la synthèse.

Variable facultative :

- `OPENAI_MODEL` : modèle à utiliser (par défaut `gpt-4.1-mini`).

Le workflow utilise également le `GITHUB_TOKEN` fourni automatiquement par GitHub Actions pour publier le fichier dans ce dépôt. Aucun token GitHub personnel n'est nécessaire.

## Périmètre de veille

Groupe EDF mondial et principales entités/activités : EDF, EDF Energy, EDF power solutions / EDF Renewables, Framatome, Dalkia, Edison, Luminus, nucléaire, hydraulique, renouvelables, services énergétiques, clients, finances, gouvernance, numérique et cybersécurité.

La couverture dépend des articles effectivement indexés dans les flux RSS. La newsletter distingue les faits rapportés des analyses et conserve les liens vers les publications originales.

## Sources de départ

- [Actualités du Groupe EDF](https://www.edf.fr/groupe-edf/espaces-dedies/journalistes/actualites)
- [Communiqués de presse du Groupe EDF](https://www.edf.fr/groupe-edf/espaces-dedies/journalistes/tous-les-communiques-de-presse)
- [EDF — All press releases (English)](https://www.edf.fr/en/the-edf-group/dedicated-sections/journalists/all-press-releases)

## Dépannage

Si l'exécution échoue, ouvrir **Actions → Weekly EDF Newsletter → dernier run**. Vérifier notamment que le secret `OPENAI_API_KEY` est bien configuré et que les permissions Actions du dépôt autorisent le workflow à écrire dans le dépôt.
