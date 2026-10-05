# Site www.dr-cievet-bonfils.fr

Site statique du Dr Maxime Cievet-Bonfils, chirurgien de la main, du poignet et du coude à Lyon. Générateur Python sans dépendance.

- `config.json` : identité, liens, adresses, téléphone, requête PubMed, ORCID. Toute donnée d'identité se modifie ici, jamais en dur.
- `content/fr/pathologies/*.md` : fiches patients. Pour en créer ou modifier une : skill `nouvelle-fiche`.
- `data/publications.json` : généré par `scripts/update_publications.py` (PubMed + ORCID + Crossref). Ne pas éditer à la main.
- `static/` : CSS (charte ICMMS : #2E3B57, #D9BBA8, #F7F0E8, Montserrat auto-hébergée), images, polices.
- `scripts/indexnow.py` + `static/<clé>.txt` : après chaque déploiement, les pages nouvelles ou modifiées sont signalées à Bing (IndexNow). Soumission complète : Actions → Build and deploy → Run workflow → cocher « Soumettre toutes les pages ». Ne pas supprimer le fichier de clé.
- `build.py` → `dist/` ; `.github/workflows/deploy.yml` construit et publie sur GitHub Pages à chaque push sur `main` et chaque lundi.

Règles déontologiques (R.4127-19-1 CSP) : information factuelle, pas de superlatif ni de comparaison, pas de témoignage, pas de promesse de résultat. Toute affirmation médicale nouvelle est validée par le Dr Cievet-Bonfils avant publication.

Vérifier avant push : `python3 build.py` sans erreur, JSON-LD valide, aucun lien interne cassé.
