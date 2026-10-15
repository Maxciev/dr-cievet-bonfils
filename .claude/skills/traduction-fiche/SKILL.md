---
name: traduction-fiche
description: Traduit en anglais une fiche pathologie française validée de www.dr-cievet-bonfils.fr (content/fr/pathologies/<slug>.md vers content/en/conditions/<slug-en>.md), ou répercute en anglais une correction faite sur une fiche française. Utiliser après chaque publication ou modification d'une fiche française, ou quand le Dr Cievet-Bonfils demande "traduis", "version anglaise", "English version".
---

# Traduction d'une fiche en anglais

Validé par le Dr Cievet-Bonfils le 2026-10-15 sur 3 fiches (carpal-tunnel-syndrome, dupuytrens-disease, trigger-finger) : ce sont les modèles.

## Règle permanente
Toute fiche française publiée a sa traduction anglaise. Toute correction validée sur une fiche française est répercutée dans la même session sur la fiche anglaise (même commit). Une fiche française encore en brouillon n'est pas traduite.

## Procédure
1. Lire la fiche française `content/fr/pathologies/<slug>.md` et un modèle anglais (`content/en/conditions/trigger-finger.md`).
2. Écrire `content/en/conditions/<slug-en>.md` (slug anglais de la table ci-dessous ; pour une nouvelle fiche, slug anglais court, minuscules, tirets, sans apostrophe).
3. `python3 build.py` puis contrôle des liens internes (aucun lien cassé, script de contrôle habituel sur `dist/`).
4. Ajouter l'adresse `https://www.dr-cievet-bonfils.fr/en/conditions/<slug-en>.html` dans `A-INDEXER.md` (« En attente »).

## Front matter (une ligne par clé, pas de guillemets)
```
---
title: <Name>: <symptoms/treatment/surgery> in Lyon
h1: <Condition name>
description: <1-2 phrases, ≤ 160 caractères si possible, avec "Dr Maxime Cievet-Bonfils, hand surgeon in Lyon, France">
condition: <English condition name>
procedure: <main procedure in English>
group: <identique à la fiche française : main | poignet | coude | nerfs | autres>
fr: <slug français>
image: <identique à la fiche française>
image_alt: <traduction de image_alt>
related_pmids: <identique>
---
```
Pas de clé `condition_en`. Pas de `status` (sauf si la fiche française est elle-même en brouillon : ne pas traduire).

## Corps
- Traduction FIDÈLE et complète : même structure, mêmes sections, mêmes listes, même nombre de questions. Ne rien ajouter, ne rien retirer, ne rien « améliorer » médicalement. Chiffres, durées, techniques, indications identiques.
- Titres de sections : What is …? / What are the symptoms? / How is it diagnosed? / What are the non-surgical treatments? / When is surgery needed? / How is the operation performed? / After the operation / Frequently asked questions (exactement « Frequently asked questions », le parseur s'en sert pour le balisage FAQ).
- Anglais britannique : anaesthesia, haematoma, oedema, orthopaedic, splint, GP, physiotherapist, day case.
- Registre patient, « you », phrases courtes, termes techniques expliqués entre parenthèses.
- Liens internes : remplacer chaque `[texte](slug-fr.html)` par `[text](slug-en.html)` avec la table. Liens externes (doi.org, GEMMSOR) conservés tels quels.
- Interdits déontologiques identiques au français : aucun superlatif sur le chirurgien (best, leading, expert, renowned, reference), aucune comparaison, aucun témoignage, aucune promesse de résultat.

## Terminologie imposée
- kinésithérapeute (spécialisé en rééducation de la main) → hand therapist (physiotherapist) ; ne jamais introduire « occupational therapist ».
- orthèse → splint (orthèse thermoformée sur mesure → custom-made thermoplastic splint)
- anesthésie locorégionale du bras → regional anaesthesia of the arm ; anesthésie locale sans garrot → wide-awake local anaesthesia with no tourniquet (WALANT)
- électromyogramme → electromyogram (EMG, nerve conduction study)
- algodystrophie → complex regional pain syndrome
- infiltration de corticoïdes → corticosteroid injection
- en ambulatoire → as a day case
- broches → pins (K-wires) ; retirées au bloc opératoire → removed in the operating theatre
- l'ulna → the ulna ; effet Stener → Stener lesion (Stener effect)
- SOS Mains → SOS Mains (emergency hand unit)

## Table des slugs (FR → EN)
| fr | en |
|---|---|
| canal-carpien | carpal-tunnel-syndrome |
| maladie-de-dupuytren | dupuytrens-disease |
| doigt-a-ressaut | trigger-finger |
| walant | walant |
| rhizarthrose | thumb-base-arthritis |
| tenosynovite-de-de-quervain | de-quervains-tenosynovitis |
| arthrose-des-doigts | finger-arthritis |
| kyste-mucoide | mucous-cyst |
| doigt-en-maillet | mallet-finger |
| entorse-des-doigts | finger-sprains |
| entorse-du-pouce | skiers-thumb |
| fractures-des-doigts-et-metacarpes | finger-and-metacarpal-fractures |
| lesions-des-poulies | pulley-injuries |
| urgences-de-la-main | hand-emergencies |
| fracture-du-poignet | wrist-fracture |
| pseudarthrose-du-scaphoide | scaphoid-nonunion |
| lesion-ligament-scapho-lunaire | scapholunate-ligament-injury |
| lesion-tfcc | tfcc-tear |
| kyste-du-poignet | wrist-ganglion |
| arthrose-du-poignet | wrist-arthritis |
| carpe-bossu | carpal-boss |
| conflit-ulno-carpien | ulnocarpal-impaction |
| maladie-de-kienbock | kienbocks-disease |
| denervation-du-poignet | wrist-denervation |
| epicondylite | tennis-elbow |
| micro-instabilite-tete-radiale | radial-head-micro-instability |
| raideur-du-coude | elbow-stiffness |
| osteochondromatose-du-coude | elbow-synovial-chondromatosis |
| rupture-du-biceps-distal | distal-biceps-rupture |
| hygroma-du-coude | olecranon-bursitis |
| compression-nerf-ulnaire-coude | cubital-tunnel-syndrome |
| compression-nerf-interosseux-posterieur | posterior-interosseous-nerve-compression |
| algodystrophie | complex-regional-pain-syndrome |
