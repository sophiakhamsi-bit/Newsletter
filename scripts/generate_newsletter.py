#!/usr/bin/env python3
"""Collect the last seven days of EDF-related news and publish a concise French digest."""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote_plus

import feedparser
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "newsletters"
NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(days=7)

# Broad global coverage, with focused searches for major group entities and business lines.
QUERIES = [
    '"EDF" OR "Électricité de France"',
    '"EDF Energy" OR "EDF UK"',
    '"EDF power solutions" OR "EDF Renewables"',
    '"Framatome" OR "Dalkia"',
    '"Edison" AND EDF energy',
    '"Luminus" AND EDF',
    'EDF nuclear OR EPR2 OR nuclear projects',
    'EDF electricity grid digital AI cybersecurity',
    'EDF hydropower OR offshore wind OR solar energy',
]

TRUSTED_DOMAINS = (
    "edf.fr", "edfenergy.com", "edf-powersolutions.com", "framatome.com",
    "dalkia.com", "reuters.com", "ft.com", "bloomberg.com", "lesechos.fr",
    "montelnews.com", "energynews.pro", "world-nuclear-news.org",
)

def published_datetime(entry):
    value = entry.get("published") or entry.get("updated")
    if value:
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (TypeError, ValueError, OverflowError):
            pass
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc)
    return None

def clean(value):
    return re.sub(r"\\s+", " ", re.sub(r"<[^>]+>", " ", value or "")).strip()

def collect_articles():
    articles = {}
    for query in QUERIES:
        url = (
            "https://news.google.com/rss/search?q="
            + quote_plus(query + " when:7d")
            + "&hl=fr&gl=FR&ceid=FR:fr"
        )
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = published_datetime(entry)
            link = entry.get("link", "")
            title = clean(entry.get("title", ""))
            summary = clean(entry.get("summary", ""))
            if not link or not title or not published or published < CUTOFF:
                continue
            key = link.split("&oc=", 1)[0]
            articles[key] = {
                "title": title,
                "link": link,
                "published": published,
                "summary": summary[:700],
                "source": clean(entry.get("source", {}).get("title", "")),
            }
    return sorted(articles.values(), key=lambda item: item["published"], reverse=True)

def build_prompt(articles):
    lines = []
    for index, item in enumerate(articles, 1):
        lines.append(
            f"{index}. {item['title']}\n"
            f"Date : {item['published'].strftime('%Y-%m-%d')} | Média : {item['source'] or 'non précisé'}\n"
            f"Résumé disponible : {item['summary'] or 'aucun'}\n"
            f"Lien : {item['link']}"
        )
    return """Tu es analyste de veille stratégique spécialisé dans le Groupe EDF et le secteur de l'énergie.
Rédige une newsletter hebdomadaire COURTE en français, couvrant le Groupe EDF mondial et ses principales filiales/activités.
Période : les 7 derniers jours.

Règles impératives :
- Utilise uniquement les éléments du corpus ci-dessous. N'invente aucun fait, chiffre, citation ou lien.
- Sélectionne au maximum 8 informations réellement importantes et évite les doublons.
- Donne pour chaque information un titre, 1 à 2 phrases factuelles, la date et le média, puis le lien source.
- Priorise les nouvelles concernant EDF et ses entités ; garde au plus 2 informations de contexte sectoriel/concurrentiel si elles éclairent directement EDF.
- Classe les informations par importance, pas par source.
- Termine par « À surveiller » avec 2 ou 3 sujets concrets, uniquement s'ils découlent du corpus.
- Si le corpus est pauvre, indique-le clairement au lieu de remplir artificiellement la newsletter.
- Ne présente pas une hypothèse comme un fait.
- Format Markdown, concis et facile à parcourir.

Corpus d'articles :
""" + "\n\n".join(lines)

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit("Secret OPENAI_API_KEY manquant. Ajoutez-le dans Settings → Secrets and variables → Actions.")
    articles = collect_articles()
    if not articles:
        sys.exit("Aucun article récent n'a été collecté ; aucune newsletter vide ne sera publiée.")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL") or "gpt-4.1-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Tu rédiges une veille exécutive fiable, concise et sourcée."},
            {"role": "user", "content": build_prompt(articles)},
        ],
    )
    digest = response.choices[0].message.content or ""
    if not digest.strip():
        sys.exit("La génération IA a renvoyé un contenu vide.")

    today = NOW.astimezone(timezone.utc).date().isoformat()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{today}.md"
    header = (
        f"# Newsletter EDF — semaine du {today}\n\n"
        f"*Veille Groupe EDF mondial · Français · Sources collectées sur les 7 derniers jours.*\n\n"
        f"> Générée automatiquement. Vérifier les articles originaux pour toute décision ou réutilisation externe.\n\n"
    )
    output.write_text(header + digest.strip() + "\n", encoding="utf-8")
    print(f"Newsletter créée : {output.relative_to(BASE_DIR)} ({len(articles)} articles collectés)")

if __name__ == "__main__":
    main()
