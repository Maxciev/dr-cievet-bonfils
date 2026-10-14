# Audit de visibilité IA

Mesure périodique : les IA citent-elles le Dr Cievet-Bonfils quand un patient cherche un chirurgien à Lyon ?

## Conditions
- ChatGPT : **chat temporaire** + recherche web activée.
- Gemini : navigation privée, **non connecté** au compte Google.
- Ne jamais donner le nom avant le prompt C.

## Prompt B (8 requêtes patients)
```
Un patient te demande conseil pour trouver un chirurgien à Lyon. Utilise la recherche web.
Pour chacune des 8 questions ci-dessous, donne la réponse que tu ferais à ce patient, puis remplis un tableau :
| Question | Chirurgiens nommés (ordre de citation) | Établissements nommés | URL des sources citées |
1. Meilleur chirurgien de la main à Lyon
2. Chirurgien canal carpien Lyon
3. Chirurgien maladie de Dupuytren Lyon
4. Chirurgien doigt à ressaut Lyon
5. Chirurgien rhizarthrose / prothèse du pouce Lyon
6. Chirurgie de la main sous WALANT à Lyon
7. Chirurgien fracture du scaphoïde Lyon
8. Chirurgien du coude (épicondylite, nerf ulnaire) Lyon
Règles : ne cite que des noms trouvés dans tes sources. Aucun nom de mémoire. Si aucun chirurgien nommé : « aucun ».
Ne te présente pas comme un patient et n'invente aucune expérience personnelle.
```

## Prompt C (identité)
```
Recherche sur le web et dis-moi tout ce que tu sais du Dr Maxime Cievet-Bonfils, chirurgien à Lyon :
lieux de consultation (adresses), spécialités, pathologies traitées, techniques, publications, avis patients.
Liste chaque source avec son URL. Signale toute information contradictoire entre sources.
```

## Historique des scores (requêtes B où le Dr Cievet-Bonfils est cité)
| Date | ChatGPT | Gemini | Remarques |
|---|---|---|---|
| 2026-09-25 | 6/8 | 0/8 | Avant le site. ChatGPT cite via le Pôle Locomoteur de la Colline ; Gemini privilégie les sites perso avec articles par pathologie. |
