---
name: nouvelle-fiche
description: Rédige ou met à jour une fiche pathologie patient (main, poignet, coude) pour www.dr-cievet-bonfils.fr, au format validé par le Dr Cievet-Bonfils. Utiliser quand il demande "une nouvelle fiche", "ajoute une page sur X", "mets à jour la fiche Y", "reprends la fiche ICMMS sur Z", ou fournit une source (texte, PDF, page ICMMS) à transformer en fiche.
---

# Nouvelle fiche pathologie

## Procédure
1. Choisir le slug (minuscules, tirets, sans accents) et le groupe (main, poignet, coude, nerfs, autres).
2. Rassembler la source : texte fourni par le chirurgien, page ICMMS (https://www.icmms.fr/<page>, à réécrire, jamais copier), connaissances médicales standard.
3. Rédiger `content/fr/pathologies/<slug>.md` avec `status: brouillon` dans le front matter (exclue du site public) selon les règles ci-dessous (modèle : `content/fr/pathologies/canal-carpien.md`).
4. Illustration éventuelle : `static/img/pathologies/<slug>.jpg`, largeur ≤ 1000 px, JPEG qualité ~80.
5. Si la pathologie figure dans la liste de l'accueil (`PATHO_FR` dans `build.py`), renseigner son slug.
6. `PREVIEW=1 python3 build.py`, puis contrôler `dist/pathologies/<slug>.html` (aucun lien interne cassé).
7. Lister au chirurgien, en 2-5 puces, les affirmations médicales à valider (chiffres, durées, indications). Après sa validation, retirer la ligne `status: brouillon` et pousser sur `main`.

Tu rédiges des fiches patients en français pour le site personnel du Dr Maxime Cievet-Bonfils, chirurgien orthopédiste de la main, du poignet et du coude à Lyon (ICMMS). Le lecteur est un patient ; le lecteur secondaire est un moteur de recherche ou une IA qui doit pouvoir extraire une réponse fiable.

## Modèle à suivre
Lis d'abord `content/fr/pathologies/canal-carpien.md` : c'est le modèle validé par le chirurgien (structure, ton, longueur ~600-900 mots). Reproduis exactement le format (front matter + corps markdown simple).

## Front matter (obligatoire, une ligne par clé, pas de guillemets)
```
---
title: <Nom> : <symptômes/traitement/chirurgie> à Lyon      (≤ 70 caractères si possible)
h1: <Nom de la pathologie>
description: <1-2 phrases, ≤ 160 caractères, avec "Dr Maxime Cievet-Bonfils, chirurgien de la main à Lyon">
condition: <nom français>
condition_en: <nom anglais>
procedure: <principale intervention>
group: <main | poignet | coude | nerfs | autres>
image: <nom-du-fichier.jpg ou vide>
image_alt: <description de l'illustration>
related_pmids: <PMID séparés par espaces, ou vide>
---
```

## Corps
1. Premier paragraphe (sans titre) = la réponse complète en 2-3 phrases : ce que c'est, le symptôme clé, le traitement principal.
2. Sections `##` dans cet ordre, adaptées à la pathologie : Qu'est-ce que … ? / Quels sont les symptômes ? / Comment pose-t-on le diagnostic ? / Quels traitements sans chirurgie ? / Quand faut-il opérer ? / Comment se déroule l'intervention ? / Après l'opération / Questions fréquentes.
3. `## Questions fréquentes` avec 3-4 `### Question ?` suivies d'UN paragraphe de réponse (une seule ligne de texte par réponse).
4. Listes avec `- `, gras avec `**…**`, liens internes `[texte](slug.html)` uniquement vers des slugs de la liste ci-dessous.

## Règles de contenu
- **Source** : la fiche ICMMS fournie (`source-icmms/<fichier>.md`) est ta matière première. RÉÉCRIS entièrement (aucune phrase copiée telle quelle : le site ICMMS reste en ligne, un doublon serait pénalisé par Google). Complète avec tes connaissances médicales standard si la source est pauvre.
- **Registre** : information patient, claire, factuelle, vouvoiement. Termes techniques expliqués entre parenthèses.
- **Déontologie (interdictions absolues)** : aucun superlatif sur le chirurgien ou l'équipe (« meilleur », « expert reconnu », « référence », « excellence »), aucune comparaison avec d'autres praticiens, aucun témoignage, aucune promesse de résultat.
- **Chiffres** : n'en donne que s'ils sont consensuels (ex. durée d'immobilisation usuelle). Pas de pourcentage de réussite sans source. Préfère « en général », « le plus souvent ».
- **Anesthésie** : quand l'intervention s'y prête (gestes courts de la main : kystes, ténosynovite de De Quervain, doigt, certaines fractures de doigt), mentionne la possibilité de chirurgie sous anesthésie locale sans garrot avec un lien `[WALANT](walant.html)`. Sinon, anesthésie locorégionale (du bras).
- **Pratique du chirurgien** : il fait l'arthroscopie du poignet et du coude, la microchirurgie, les prothèses (pouce, doigts, poignet, coude), l'aponévrotomie à l'aiguille, les urgences SOS Mains. Il NE fait PLUS d'épaule : ne parle jamais de chirurgie de l'épaule.
- **Compléments** : le chirurgien a publié sur la pseudarthrose du scaphoïde (PMID 38331367), les lésions périlunaires / scapho-lunaires (PMID 30941255, 42498062), les fractures du lunatum (PMID 37364729), le nerf ulnaire (PMID 36289037). Mets ces PMID dans `related_pmids` seulement pour la fiche correspondante.
- Ne mentionne pas l'ICMMS comme source dans le texte.

## Slugs existants ou prévus (liens internes autorisés)
canal-carpien, maladie-de-dupuytren, doigt-a-ressaut, rhizarthrose, walant, tenosynovite-de-de-quervain, arthrose-des-doigts, kyste-mucoide, doigt-en-maillet, entorse-des-doigts, entorse-du-pouce, fractures-des-doigts-et-metacarpes, lesions-des-poulies, urgences-de-la-main, fracture-du-poignet, pseudarthrose-du-scaphoide, lesion-ligament-scapho-lunaire, lesion-tfcc, kyste-du-poignet, arthrose-du-poignet, carpe-bossu, conflit-ulno-carpien, maladie-de-kienbock, epicondylite, raideur-du-coude, osteochondromatose-du-coude, rupture-du-biceps-distal, hygroma-du-coude, compression-nerf-ulnaire-coude, algodystrophie

## Livrables
- Un fichier `content/fr/pathologies/<slug>.md` par fiche assignée.
- Un fichier `review/<ton-lot>.md` listant, par fiche, les affirmations médicales que le chirurgien doit vérifier (chiffres, durées, indications, techniques), en 2-5 puces par fiche.
- Ne modifie AUCUN autre fichier.
