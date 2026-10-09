#!/usr/bin/env python3
"""Static site generator for www.dr-cievet-bonfils.fr — no dependencies.

Inputs : config.json, content/fr/pathologies/*.md, data/publications.json, static/
Output : dist/
"""
import html
import json
import os
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "dist"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
PUBS = json.loads((ROOT / "data" / "publications.json").read_text(encoding="utf-8"))
BASE = CFG["base_url"].rstrip("/")
NAME = CFG["name"]
L = CFG["links"]
e = html.escape
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def date_fr(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MOIS[int(m) - 1]} {y}"

# ---------------------------------------------------------------- content data
SPECIALTY_FR = "Chirurgien de la main, du poignet et du coude à Lyon"
SPECIALTY_EN = "Hand, Wrist and Elbow Surgeon in Lyon, France"

GROUPS = {"main": "Main et doigts", "poignet": "Poignet", "coude": "Coude", "nerfs": "Nerfs", "autres": "Autres"}
FEATURED = ["canal-carpien", "maladie-de-dupuytren", "doigt-a-ressaut", "rhizarthrose", "walant", "fracture-du-poignet", "epicondylite", "kyste-du-poignet"]

# (label, page slug or None) — linked only if the page exists
PATHO_FR = {
    "Main et doigts": [
        ("Maladie de Dupuytren (doigts rétractés dans la paume)", "maladie-de-dupuytren"),
        ("Doigt à ressaut", "doigt-a-ressaut"),
        ("Tendinite de De Quervain", "tenosynovite-de-de-quervain"),
        ("Arthrose du pouce (rhizarthrose) : prothèse trapézo-métacarpienne", "rhizarthrose"),
        ("Arthrose des doigts : prothèse interphalangienne proximale", "arthrose-des-doigts"),
        ("Kystes : kyste mucoïde, kyste de la gaine des fléchisseurs", "kyste-mucoide"),
        ("Plaies, lésions des tendons et fractures de la main et des doigts", "fractures-des-doigts-et-metacarpes"),
    ],
    "Poignet": [
        ("Fractures du poignet (radius distal), du scaphoïde et des os du carpe", "fracture-du-poignet"),
        ("Pseudarthrose du scaphoïde", "pseudarthrose-du-scaphoide"),
        ("Entorses graves et lésions ligamentaires (ligament scapho-lunaire, TFCC), luxations du carpe", "lesion-ligament-scapho-lunaire"),
        ("Arthrose du poignet", "arthrose-du-poignet"),
        ("Kyste arthrosynovial du poignet", "kyste-du-poignet"),
    ],
    "Coude": [
        ("Épicondylite (tennis elbow)", "epicondylite"),
        ("Fractures du coude", None),
        ("Raideur (arthrolyse), ostéochondrite, chondromatose et corps étrangers articulaires", "raideur-du-coude"),
        ("Arthrose et prothèse du coude", None),
    ],
    "Nerfs": [
        ("Syndrome du canal carpien (compression du nerf médian au poignet)", "canal-carpien"),
        ("Compression du nerf ulnaire au coude (fourmillements de l'annulaire et de l'auriculaire)", "compression-nerf-ulnaire-coude"),
        ("Syndrome du lacertus (compression du nerf médian au coude)", None),
        ("Compression du nerf interosseux postérieur (branche du nerf radial au coude)", None),
    ],
    "Urgences de la main (SOS Mains)": [
        ("Plaies, sections de tendons et de nerfs, fractures, replantations de doigts et de membre", "urgences-de-la-main"),
    ],
}
PATHO_EN = {
    "Hand and fingers": [
        "Dupuytren's disease (fingers bent into the palm)", "Trigger finger", "De Quervain's tenosynovitis",
        "Thumb base arthritis: trapeziometacarpal joint replacement",
        "Finger arthritis: proximal interphalangeal (PIP) joint replacement",
        "Cysts: mucous cysts, flexor tendon sheath cysts", "Hand wounds, tendon injuries, hand and finger fractures",
    ],
    "Wrist": [
        "Wrist (distal radius), scaphoid and carpal bone fractures", "Scaphoid non-union",
        "Severe sprains and ligament injuries (scapholunate ligament, TFCC), carpal dislocations",
        "Wrist arthritis", "Wrist ganglion",
    ],
    "Elbow": [
        "Tennis elbow (lateral epicondylitis)", "Elbow fractures",
        "Stiffness (arthrolysis), osteochondritis, synovial chondromatosis and loose bodies",
        "Elbow arthritis and elbow replacement",
    ],
    "Nerves": [
        "Carpal tunnel syndrome (median nerve compression at the wrist)",
        "Cubital tunnel syndrome (ulnar nerve compression at the elbow)",
        "Lacertus syndrome (median nerve compression at the elbow)",
        "Posterior interosseous nerve compression (radial nerve branch at the elbow)",
    ],
    "Hand emergencies (SOS Mains)": ["Wounds, tendon and nerve injuries, fractures, finger and limb replantation"],
}
TECH_FR = [("Chirurgie sous anesthésie locale sans garrot (WALANT)", "walant"), ("Arthroscopie du poignet et du coude", None),
           ("Prothèses du pouce, des doigts, du poignet et du coude", None), ("Microchirurgie", None), ("Chirurgie ambulatoire", None)]
TECH_EN = ["Wide-awake local anaesthesia no tourniquet (WALANT) surgery", "Wrist and elbow arthroscopy",
           "Thumb, finger, wrist and elbow joint replacement", "Microsurgery", "Day surgery"]
DIPLOMAS_FR = ["DIU de chirurgie de la main", "DIU d'arthroscopie", "DU de microchirurgie",
               "DU de pathologie du coude et de l'épaule", "DU de réparation juridique du dommage corporel"]
DIPLOMAS_EN = ["Inter-university diploma (DIU) in hand surgery", "Inter-university diploma (DIU) in arthroscopy",
               "University diploma (DU) in microsurgery", "University diploma (DU) in elbow and shoulder pathology",
               "University diploma (DU) in medico-legal assessment of personal injury"]
SOCIETIES_FR = ["Collège français de chirurgie orthopédique et traumatologique (CFCOT)",
                "Société française de chirurgie orthopédique et traumatologique (SOFCOT)",
                "Société française de chirurgie de la main (SFCM)", "Société française d'arthroscopie (SFA)",
                "Société française de l'épaule et du coude (SOFEC)"]
SOCIETIES_EN = ["French College of Orthopaedic and Trauma Surgery (CFCOT)",
                "French Society of Orthopaedic and Trauma Surgery (SOFCOT)", "French Society for Surgery of the Hand (SFCM)",
                "French Arthroscopy Society (SFA)", "French Shoulder and Elbow Society (SOFEC)"]

LEAD_FR = ("Le Dr Maxime Cievet-Bonfils est chirurgien orthopédiste spécialisé en chirurgie de la main, du poignet et du coude, "
           "à l'Institut Chirurgical de la Main et du Membre Supérieur (ICMMS) à Lyon. Il prend en charge le syndrome du canal carpien, "
           "la maladie de Dupuytren, le doigt à ressaut, l'arthrose du pouce (rhizarthrose), les fractures et lésions ligamentaires du poignet, "
           "les pathologies du coude et les urgences de la main (SOS Mains). Il pratique la chirurgie sous anesthésie locale sans garrot (WALANT). "
           "Il consulte à Lyon 6e et à Caluire-et-Cuire, et opère au Médipôle Lyon-Villeurbanne, à la Clinique de l'Infirmerie Protestante "
           "et à la Clinique Saint-Charles.")
LEAD_EN = ("Dr Maxime Cievet-Bonfils is an orthopaedic surgeon specialising in hand, wrist and elbow surgery at the Institut Chirurgical "
           "de la Main et du Membre Supérieur (ICMMS, Hand and Upper Limb Surgery Institute) in Lyon, France. He treats carpal tunnel syndrome, "
           "Dupuytren's disease, trigger finger, thumb base arthritis, wrist fractures and ligament injuries, elbow disorders and hand emergencies. "
           "He performs wide-awake local anaesthesia no tourniquet (WALANT) surgery. He sees patients in Lyon (6th arrondissement) and "
           "Caluire-et-Cuire, and operates at Médipôle Lyon-Villeurbanne, Clinique de l'Infirmerie Protestante and Clinique Saint-Charles.")
CAREER_FR = ("Ancien interne des Hôpitaux de Lyon (2014-2019), il a été assistant spécialiste dans le service de chirurgie orthopédique "
             "de la main et du membre supérieur de l'hôpital Édouard-Herriot (Hospices Civils de Lyon, SOS Mains) de 2019 à 2021. "
             "Il exerce à l'ICMMS depuis janvier 2022. Il est accrédité par la Haute Autorité de Santé en chirurgie orthopédique et traumatologique.")
CAREER_EN = ("After his residency at the Lyon University Hospitals (2014–2019), he was a post-residency fellow in the Hand and Upper Limb "
             "Surgery Department of Édouard Herriot University Hospital (Hospices Civils de Lyon, SOS Mains emergency hand unit) from 2019 "
             "to 2021. He has practised at ICMMS since January 2022. He is accredited by the French National Authority for Health (HAS) "
             "in orthopaedic and trauma surgery.")
RESEARCH_FR = ("Auteur ou coauteur d'articles indexés dans PubMed, principalement sur l'arthroscopie du poignet (fractures du lunatum, "
               "lésions périlunaires, pseudarthrose du scaphoïde), la prothèse trapézo-métacarpienne, le nerf ulnaire et "
               "l'intelligence artificielle en chirurgie de la main.")
RESEARCH_EN = ("Author or co-author of PubMed-indexed articles, mainly on wrist arthroscopy (lunate fractures, perilunate injuries, "
               "scaphoid non-union), trapeziometacarpal joint replacement, the ulnar nerve and artificial intelligence in hand surgery.")

OTHER = set(CFG["other_ids"])


def is_other(p):
    return p.get("pmid") in OTHER or p.get("doi") in OTHER


PUBMED_URL = "https://pubmed.ncbi.nlm.nih.gov/?term=" + CFG["pubmed_query"].replace(" ", "+").replace("[", "%5B").replace("]", "%5D") + "&sort=date"

# ---------------------------------------------------------------- helpers
def md_inline(text):
    text = e(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)


def parse_md(path):
    raw = path.read_text(encoding="utf-8")
    _, fm, body = raw.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    meta["slug"] = path.stem
    blocks, faq, lead = [], [], None
    in_faq, current_q, list_open = False, None, False
    for line in body.strip().splitlines():
        s = line.strip()
        if s.startswith("- "):
            if not list_open:
                blocks.append("<ul>")
                list_open = True
            blocks.append(f"<li>{md_inline(s[2:])}</li>")
            continue
        if list_open:
            blocks.append("</ul>")
            list_open = False
        if not s:
            continue
        if s.startswith("## "):
            title = s[3:]
            in_faq = title.lower().startswith("questions fréquentes")
            blocks.append(f'<h2 id="{slugify(title)}">{md_inline(title)}</h2>')
        elif s.startswith("### "):
            current_q = s[4:]
            blocks.append(f"<h3>{md_inline(current_q)}</h3>")
        else:
            if lead is None:
                lead = s
                continue
            blocks.append(f"<p>{md_inline(s)}</p>")
            if in_faq and current_q:
                faq.append((current_q, s))
                current_q = None
    if list_open:
        blocks.append("</ul>")
    meta["lead"] = lead
    meta["body"] = "\n".join(blocks)
    meta["faq"] = faq
    return meta


def slugify(s):
    s = s.lower()
    for a, b in (("é", "e"), ("è", "e"), ("ê", "e"), ("à", "a"), ("ç", "c"), ("ô", "o"), ("î", "i"), ("'", "-"), ("’", "-")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def fmt_address(a, lang="fr"):
    detail = a.get(f"detail_{lang}")
    return f"{e(a['street'])}, {e(a['postal'])} {e(a['city'])}" + (f" ({e(detail)})" if detail else "")


def fmt_pub(p, highlight=True):
    authors = ", ".join(p["authors"]) + (", et al" if p.get("et_al") else "")
    if highlight:
        authors = e(authors)
        for v in CFG["author_variants"]:
            authors = authors.replace(e(v), f"<strong>{e(v)}</strong>")
    loc = p["year"]
    if p.get("volume"):
        loc += f";{p['volume']}" + (f"({p['issue']})" if p.get("issue") else "")
    if p.get("pages"):
        loc += f":{p['pages']}"
    doi = f' <a href="https://doi.org/{e(p["doi"])}">doi:{e(p["doi"])}</a>' if p.get("doi") else ""
    pmid = f' <a href="https://pubmed.ncbi.nlm.nih.gov/{e(p["pmid"])}/">PMID {e(p["pmid"])}</a>' if p.get("pmid") else ""
    head = f"{authors}. " if authors else ""
    journal = f' <em>{e(p["journal"])}</em>.' if p.get("journal") else ""
    return f'{head}{e(p["title"])}{journal} {e(loc)}.{doi}{pmid}'


def tile(p, up=""):
    img = f'<img src="{up}img/pathologies/{e(p["image"])}" alt="" loading="lazy" width="400" height="300">' if p.get("image") else ""
    return (f'<a class="tile" href="{up}pathologies/{p["slug"]}.html">{img}<span class="tile-body">'
            f'<span class="tile-group">{e(GROUPS.get(p.get("group", ""), ""))}</span>'
            f'<span class="tile-title">{e(p["h1"])}</span></span></a>')


def person_node():
    return {
        "@type": "Person",
        "@id": BASE + "/#person",
        "name": NAME,
        "givenName": CFG["given_name"],
        "familyName": CFG["family_name"],
        "honorificPrefix": "Dr",
        "jobTitle": "Chirurgien orthopédiste — chirurgie de la main, du poignet et du coude",
        "url": BASE + "/",
        "worksFor": {"@type": "MedicalOrganization", "name": "Institut Chirurgical de la Main et du Membre Supérieur (ICMMS)"},
        "memberOf": [{"@type": "Organization", "name": n} for n in SOCIETIES_FR],
        "image": BASE + "/img/portrait.jpg",
        "telephone": CFG["phone"]["e164"],
        "identifier": {"@type": "PropertyValue", "propertyID": "RPPS", "value": CFG["legal"]["rpps"]},
        "knowsLanguage": ["fr", "en"],
        "knowsAbout": ["Chirurgie de la main", "Chirurgie du poignet", "Chirurgie du coude", "Syndrome du canal carpien",
                       "Maladie de Dupuytren", "Doigt à ressaut", "Rhizarthrose", "WALANT", "Arthroscopie du poignet"],
        "sameAs": [L[k] for k in ("orcid", "researchgate", "linkedin", "doctolib", "icmms", "pole", "infirmerie", "medipole")],
    }


def physician_node():
    return {
        "@type": "Physician",
        "@id": BASE + "/#practice",
        "name": NAME,
        "url": BASE + "/",
        "medicalSpecialty": ["https://schema.org/Surgical", "https://schema.org/Musculoskeletal"],
        "address": [{"@type": "PostalAddress", "streetAddress": a["street"], "postalCode": a["postal"],
                     "addressLocality": a["city"], "addressCountry": "FR"} for a in CFG["consultations"]],
        "hospitalAffiliation": [{"@type": "Hospital", "name": s["name"],
                                 "address": {"@type": "PostalAddress", "streetAddress": s["street"], "postalCode": s["postal"],
                                             "addressLocality": s["city"], "addressCountry": "FR"}} for s in CFG["surgery_sites"]],
        "availableService": [{"@type": "MedicalProcedure", "name": n} for n in (
            "Libération du nerf médian au canal carpien", "Aponévrectomie pour maladie de Dupuytren",
            "Ouverture de poulie pour doigt à ressaut", "Prothèse trapézo-métacarpienne", "Arthroscopie du poignet",
            "Arthroscopie du coude", "Chirurgie sous anesthésie locale sans garrot (WALANT)")],
        "employee": {"@id": BASE + "/#person"},
        "telephone": CFG["phone"]["e164"],
        "image": BASE + "/img/portrait.jpg",
        "priceRange": "Secteur 2",
    }


def jsonld(graph):
    return ('<script type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
            + "</script>")


# ---------------------------------------------------------------- layout
def page(*, lang, path, title, description, body, graph, depth=0, alt=None):
    up = "../" * depth
    home = f"{up}index.html" if lang == "fr" else f"{up}en/index.html"
    if lang == "fr":
        nav = (f'<a href="{up}pathologies/index.html">Pathologies</a><a href="{up}pathologies/walant.html">WALANT</a>'
               f'<a href="{up}publications.html">Publications</a><a href="{up}index.html#consultations">Consultations</a>'
               f'<a href="{up}en/index.html" hreflang="en" lang="en">EN</a>')
        cta, footer_note = "Prendre rendez-vous", ("Les informations de ce site sont générales et ne remplacent pas une consultation. "
                                                   "En cas d'urgence de la main, contactez le SOS Mains ou le 15.")
        legal = f'<a href="{up}mentions-legales.html">Mentions légales</a>'
    else:
        nav = (f'<a href="{up}en/index.html#conditions">Conditions</a><a href="{up}publications.html">Publications</a>'
               f'<a href="{up}en/index.html#locations">Locations</a><a href="{up}index.html" hreflang="fr" lang="fr">FR</a>')
        cta, footer_note = "Book an appointment", ("The information on this website is general and does not replace a consultation. "
                                                   "For a hand emergency, contact the SOS Mains unit or call 15.")
        legal = f'<a href="{up}mentions-legales.html">Legal notice</a>'
    alts = ""
    if alt:
        alts = (f'<link rel="alternate" hreflang="fr" href="{BASE}/{alt["fr"]}">'
                f'<link rel="alternate" hreflang="en" href="{BASE}/{alt["en"]}">')
    consult = "".join(f"<li><strong>{e(a['name'])}</strong><br>{fmt_address(a, lang)}</li>" for a in CFG["consultations"])
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{BASE}/{path}">
{alts}
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}/{path}">
<link rel="stylesheet" href="{up}style.css">
{jsonld(graph)}
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{home}"><span class="brand-name">{e(NAME)}</span><span class="brand-sub">{e(SPECIALTY_FR if lang == "fr" else SPECIALTY_EN)}</span></a>
    <nav class="nav">{nav}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div><p class="footer-name">{e(NAME)}</p><p>{e(SPECIALTY_FR if lang == "fr" else SPECIALTY_EN)}</p>
    <p><a href="tel:{CFG['phone']['e164']}">{CFG['phone']['display']}</a></p>
    <p><a class="btn btn-small" href="{e(L['doctolib'])}" rel="noopener">{cta}</a></p></div>
    <div><p class="footer-h">{"Consultations" if lang == "fr" else "Consultations"}</p><ul class="plain">{consult}</ul></div>
    <div><p class="footer-h">{"Profils" if lang == "fr" else "Profiles"}</p><ul class="plain">
      <li><a href="{e(L['orcid'])}">ORCID</a></li><li><a href="{e(PUBMED_URL)}">PubMed</a></li>
      <li><a href="{e(L['researchgate'])}">ResearchGate</a></li><li><a href="{e(L['icmms'])}">ICMMS</a></li>
      <li><a href="{e(L['linkedin'])}">LinkedIn</a></li></ul></div>
  </div>
  <div class="wrap footer-note"><p>{footer_note}</p><p>{legal} · {"Mis à jour le " + date_fr(CFG["updated"]) if lang == "fr" else "Updated " + CFG["updated"]}</p></div>
</footer>
</body>
</html>
"""


def write(rel, content):
    out = DIST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------- pages
def build_home_fr(pathos):
    exists = {p["slug"] for p in pathos}
    by_slug = {p["slug"]: p for p in pathos}
    groups = ""
    for group, items in PATHO_FR.items():
        lis = "".join(f'<li><a href="pathologies/{s}.html">{e(t)}</a></li>' if s in exists else f"<li>{e(t)}</li>" for t, s in items)
        groups += f'<div class="card"><h3>{e(group)}</h3><ul>{lis}</ul></div>'
    tech = "".join(f'<li><a href="pathologies/{s}.html">{e(t)}</a></li>' if s else f"<li>{e(t)}</li>" for t, s in TECH_FR)
    featured = "".join(tile(by_slug[s]) for s in FEATURED if s in by_slug)
    consult = "".join(f"<li><strong>{e(a['name'])}</strong><br>{fmt_address(a)}</li>" for a in CFG["consultations"])
    surg = "".join(f"<li><strong>{e(a['name'])}</strong><br>{fmt_address(a)}</li>" for a in CFG["surgery_sites"])
    main_pubs = [p for p in PUBS["items"] if not is_other(p)][:3]
    pubs = "".join(f"<li>{fmt_pub(p)}</li>" for p in main_pubs)
    body = f"""
<section class="hero"><div class="wrap hero-inner">
  <div class="hero-text">
    <p class="eyebrow">Chirurgie de la main · du poignet · du coude</p>
    <h1>{e(NAME)}</h1>
    <p class="hero-sub">{e(SPECIALTY_FR)}</p>
    <p class="lead">{e(LEAD_FR)}</p>
    <p class="actions"><a class="btn" href="{e(L['doctolib'])}" rel="noopener">Prendre rendez-vous sur Doctolib</a>
    <a class="btn btn-ghost" href="tel:{CFG['phone']['e164']}">Secrétariat : {CFG['phone']['display']}</a>
    <a class="btn btn-ghost" href="pathologies/index.html">Fiches pathologies</a></p>
  </div>
  <img class="portrait" src="img/portrait.jpg" width="480" height="600" alt="Portrait du Dr Maxime Cievet-Bonfils">
</div></section>

<section class="wrap section"><h2>Pour comprendre votre pathologie</h2><div class="tiles">{featured}</div>
  <p><a class="btn btn-ghost" href="pathologies/index.html">Toutes les fiches ({len(pathos)})</a></p></section>

<section class="wrap section" id="pathologies"><h2>Pathologies prises en charge</h2><div class="cards">{groups}</div></section>

<section class="band"><div class="wrap section two-col">
  <div><h2>Techniques</h2><ul>{tech}</ul></div>
  <div><h2>Parcours</h2><p>{e(CAREER_FR)}</p></div>
</div></section>

<section class="wrap section two-col">
  <div><h2>Diplômes</h2><ul>{"".join(f"<li>{e(d)}</li>" for d in DIPLOMAS_FR)}</ul></div>
  <div><h2>Sociétés savantes</h2><ul>{"".join(f"<li>{e(d)}</li>" for d in SOCIETIES_FR)}</ul><h2>Langues</h2><p>Français, anglais</p></div>
</section>

<section class="band-navy" id="consultations"><div class="wrap section two-col">
  <div><h2>Lieux de consultation</h2><ul class="plain">{consult}</ul>
  <p>{e(CFG['phone']['label_fr'])} : <a href="tel:{CFG['phone']['e164']}">{CFG['phone']['display']}</a></p>
  <p>{e(CFG['legal']['secteur'])}.</p>
  <p><a class="btn" href="{e(L['doctolib'])}" rel="noopener">Prendre rendez-vous sur Doctolib</a></p></div>
  <div><h2>Lieux d'intervention</h2><ul class="plain">{surg}</ul></div>
</div></section>

<section class="wrap section" id="recherche"><h2>Recherche</h2><p>{e(RESEARCH_FR)}</p>
  <h3>Publications récentes</h3><ol class="pubs">{pubs}</ol>
  <p><a href="publications.html">Toutes les publications</a> · <a href="{e(PUBMED_URL)}">PubMed</a> · <a href="{e(L['orcid'])}">ORCID</a> · <a href="{e(L['researchgate'])}">ResearchGate</a></p>
</section>
"""
    graph = [person_node(), physician_node(),
             {"@type": "WebPage", "@id": BASE + "/#webpage", "url": BASE + "/", "name": f"{NAME} — {SPECIALTY_FR}",
              "inLanguage": "fr", "about": {"@id": BASE + "/#person"}, "dateModified": CFG["updated"]}]
    write("index.html", page(lang="fr", path="", title=f"{NAME} — {SPECIALTY_FR}",
                             description=LEAD_FR[:155].rsplit(" ", 1)[0] + "…", body=body, graph=graph,
                             alt={"fr": "", "en": "en/"}))


def build_home_en():
    groups = "".join(f'<div class="card"><h3>{e(g)}</h3><ul>{"".join(f"<li>{e(t)}</li>" for t in items)}</ul></div>'
                     for g, items in PATHO_EN.items())
    consult = "".join(f"<li><strong>{e(a['name'])}</strong><br>{fmt_address(a, 'en')}</li>" for a in CFG["consultations"])
    surg = "".join(f"<li><strong>{e(a['name'])}</strong><br>{fmt_address(a, 'en')}</li>" for a in CFG["surgery_sites"])
    body = f"""
<section class="hero"><div class="wrap hero-inner">
  <div class="hero-text">
    <p class="eyebrow">Hand · Wrist · Elbow surgery</p>
    <h1>{e(NAME)}</h1>
    <p class="hero-sub">{e(SPECIALTY_EN)}</p>
    <p class="lead">{e(LEAD_EN)}</p>
    <p class="actions"><a class="btn" href="{e(L['doctolib'])}" rel="noopener">Book on Doctolib</a>
    <a class="btn btn-ghost" href="tel:{CFG['phone']['e164']}">Secretary: +33 4 87 25 83 35</a>
    <a class="btn btn-ghost" href="#conditions">Conditions treated</a></p>
  </div>
  <img class="portrait" src="../img/portrait.jpg" width="480" height="600" alt="Portrait of Dr Maxime Cievet-Bonfils">
</div></section>
<section class="wrap section" id="conditions"><h2>Conditions treated</h2><div class="cards">{groups}</div></section>
<section class="band"><div class="wrap section two-col">
  <div><h2>Techniques</h2><ul>{"".join(f"<li>{e(t)}</li>" for t in TECH_EN)}</ul></div>
  <div><h2>Training</h2><p>{e(CAREER_EN)}</p></div>
</div></section>
<section class="wrap section two-col">
  <div><h2>Qualifications</h2><ul>{"".join(f"<li>{e(d)}</li>" for d in DIPLOMAS_EN)}</ul></div>
  <div><h2>Professional societies</h2><ul>{"".join(f"<li>{e(d)}</li>" for d in SOCIETIES_EN)}</ul><h2>Languages</h2><p>French, English</p></div>
</section>
<section class="band" id="locations"><div class="wrap section two-col">
  <div><h2>Consultations</h2><ul class="plain">{consult}</ul>
  <p>{e(CFG['phone']['label_en'])}: <a href="tel:{CFG['phone']['e164']}">+33 4 87 25 83 35</a></p>
  <p>Contracted with the French national health insurance, sector 2 (fees above the standard tariff, not OPTAM).</p></div>
  <div><h2>Surgery</h2><ul class="plain">{surg}</ul></div>
</div></section>
<section class="wrap section"><h2>Research</h2><p>{e(RESEARCH_EN)}</p>
<p><a href="../publications.html">Full list of publications</a> · <a href="{e(PUBMED_URL)}">PubMed</a> · <a href="{e(L['orcid'])}">ORCID</a></p></section>
"""
    graph = [person_node(), physician_node(),
             {"@type": "WebPage", "url": BASE + "/en/", "name": f"{NAME} — {SPECIALTY_EN}", "inLanguage": "en",
              "about": {"@id": BASE + "/#person"}, "dateModified": CFG["updated"]}]
    write("en/index.html", page(lang="en", path="en/", title=f"{NAME} — {SPECIALTY_EN}",
                                description=LEAD_EN[:155].rsplit(" ", 1)[0] + "…", body=body, graph=graph, depth=1,
                                alt={"fr": "", "en": "en/"}))


def build_pathology(p, all_pathos):
    # A link to a fiche that is still a draft would 404 on the public site: keep only its text.
    published = {o["slug"] for o in all_pathos}
    p = {**p, "body": re.sub(r'<a href="([a-z0-9-]+)\.html">(.*?)</a>',
                             lambda m: m.group(0) if m.group(1) in published else m.group(2), p["body"])}
    related = [x for x in PUBS["items"] if x["pmid"] in p.get("related_pmids", "").split()]
    rel_html = ""
    if related:
        rel_html = '<section class="related"><h2>Publication du Dr Cievet-Bonfils sur ce sujet</h2><ol class="pubs">' + \
                   "".join(f"<li>{fmt_pub(x)}</li>" for x in related) + "</ol></section>"
    same = [o for o in all_pathos if o["slug"] != p["slug"] and o.get("group") == p.get("group")]
    others = "".join(f'<li><a href="{o["slug"]}.html">{e(o["h1"])}</a></li>' for o in (same or all_pathos[:6])[:8])
    figure = (f'<figure class="figure"><img src="../img/pathologies/{e(p["image"])}" alt="{e(p.get("image_alt", ""))}" width="1000" height="750">'
              f'<figcaption>Illustration © ICMMS</figcaption></figure>') if p.get("image") else ""
    consult = "".join(f"<li><strong>{e(a['name'])}</strong>, {fmt_address(a)}</li>" for a in CFG["consultations"])
    body = f"""
<article class="wrap article">
  <nav class="crumbs"><a href="../index.html">Accueil</a> › <a href="index.html">Fiches pathologies</a> › {e(GROUPS.get(p.get("group", ""), ""))} › {e(p["h1"])}</nav>
  <h1>{e(p["h1"])}</h1>
  <p class="byline">Par le {e(NAME)}, chirurgien de la main, du poignet et du coude à Lyon · Mis à jour le {e(date_fr(CFG["updated"]))}</p>
  <p class="lead">{md_inline(p["lead"])}</p>
  {figure}
  {p["body"]}
  {rel_html}
  <section class="consult-box"><h2>Consulter à Lyon</h2>
    <p>Le {e(NAME)} consulte :</p><ul>{consult}</ul>
    <p>{e(CFG['phone']['label_fr'])} : <a href="tel:{CFG['phone']['e164']}">{CFG['phone']['display']}</a></p>
    <p><a class="btn" href="{e(L['doctolib'])}" rel="noopener">Prendre rendez-vous sur Doctolib</a></p>
  </section>
  <aside class="see-also"><h2>Voir aussi</h2><ul>{others}</ul></aside>
  <p class="disclaimer">Cette page donne une information générale. Elle ne remplace pas une consultation : chaque situation est différente.</p>
</article>
"""
    url = f"{BASE}/pathologies/{p['slug']}.html"
    about_type = "MedicalProcedure" if p.get("kind") == "procedure" else "MedicalCondition"
    about = {"@type": about_type, "name": p["condition"], "alternateName": p.get("condition_en", "")}
    if about_type == "MedicalCondition":
        about["possibleTreatment"] = {"@type": "MedicalProcedure", "name": p["procedure"]}
    graph = [
        {"@type": "MedicalWebPage", "@id": url, "url": url, "name": p["title"], "description": p["description"], "inLanguage": "fr",
         "about": about, "audience": {"@type": "Patient"}, **({"image": f"{BASE}/img/pathologies/{p['image']}"} if p.get("image") else {}), "author": {"@id": BASE + "/#person"},
         "reviewedBy": {"@id": BASE + "/#person"}, "lastReviewed": CFG["updated"], "dateModified": CFG["updated"]},
        person_node(),
    ]
    if p["faq"]:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]})
    write(f"pathologies/{p['slug']}.html", page(lang="fr", path=f"pathologies/{p['slug']}.html", title=p["title"],
                                                description=p["description"], body=body, graph=graph, depth=1))


def build_index(pathos):
    sections = ""
    for key, label in GROUPS.items():
        items = [p for p in pathos if p.get("group") == key]
        if items:
            sections += f'<h2 id="{key}">{e(label)}</h2><div class="tiles">' + "".join(tile(p, "../") for p in items) + "</div>"
    body = f"""
<article class="wrap section">
  <nav class="crumbs"><a href="../index.html">Accueil</a> › Fiches pathologies</nav>
  <h1>Fiches pathologies</h1>
  <p class="lead">Informations pour les patients sur les pathologies de la main, du poignet et du coude prises en charge par le {e(NAME)} à Lyon : symptômes, examens, traitements et suites opératoires.</p>
  {sections}
</article>"""
    graph = [person_node(), {"@type": "CollectionPage", "url": BASE + "/pathologies/", "name": "Fiches pathologies",
                             "hasPart": [{"@type": "MedicalWebPage", "url": f"{BASE}/pathologies/{p['slug']}.html", "name": p["h1"]} for p in pathos]}]
    write("pathologies/index.html", page(lang="fr", path="pathologies/", title=f"Fiches pathologies de la main, du poignet et du coude — {NAME}",
                                         description="Fiches d'information patient : main, poignet, coude. Symptômes, traitements, chirurgie à Lyon.",
                                         body=body, graph=graph, depth=1))


def build_publications():
    arts = {"journal-article", "review", "book-chapter", "book", "editorial", "letter"}
    is_art = lambda p: p.get("type", "journal-article") in arts
    main = [p for p in PUBS["items"] if is_art(p) and not is_other(p)]
    other = [p for p in PUBS["items"] if is_art(p) and is_other(p)]
    comms = [p for p in PUBS["items"] if not is_art(p)]
    body = f"""
<article class="wrap article">
  <h1>Publications</h1>
  <p class="lead">Travaux du {e(NAME)} référencés dans PubMed et ORCID. Liste mise à jour automatiquement chaque semaine (dernière mise à jour : {e(date_fr(PUBS["fetched"]))}).</p>
  <p><a href="{e(PUBMED_URL)}">Voir sur PubMed</a> · <a href="{e(L['orcid'])}">ORCID</a> · <a href="{e(L['researchgate'])}">ResearchGate</a></p>
  <h2>Main, poignet et coude</h2><ol class="pubs">{"".join(f"<li>{fmt_pub(p)}</li>" for p in main)}</ol>
  {"<h2>Autres publications (internat)</h2><ol class='pubs'>" + "".join(f"<li>{fmt_pub(p)}</li>" for p in other) + "</ol>" if other else ""}
  {"<h2>Communications et autres travaux</h2><ol class='pubs'>" + "".join(f"<li>{fmt_pub(p)}</li>" for p in comms) + "</ol>" if comms else ""}
</article>
"""
    graph = [person_node(), {"@type": "CollectionPage", "url": BASE + "/publications.html", "name": f"Publications — {NAME}",
                             "about": {"@id": BASE + "/#person"},
                             "hasPart": [{"@type": "ScholarlyArticle", "headline": p["title"], "datePublished": p["year"],
                                          **({"sameAs": f"https://doi.org/{p['doi']}"} if p.get("doi") else {"sameAs": f"https://pubmed.ncbi.nlm.nih.gov/{p['pmid']}/"} if p.get("pmid") else {}),
                                          "author": {"@id": BASE + "/#person"}} for p in PUBS["items"]]}]
    write("publications.html", page(lang="fr", path="publications.html", title=f"Publications — {NAME}",
                                    description=f"Publications scientifiques du {NAME}, chirurgien de la main à Lyon, indexées dans PubMed.",
                                    body=body, graph=graph))


def build_legal():
    lg = CFG["legal"]
    c0 = CFG["consultations"][0]
    body = f"""
<article class="wrap article"><h1>Mentions légales</h1>
<h2>Éditeur du site</h2><p>{e(NAME)}, chirurgien orthopédiste<br>{e(c0['name'])}, {fmt_address(c0)}<br>
RPPS : {e(lg['rpps'])}<br>{e(lg['ordre'])}<br>{e(lg['secteur'])}<br>Téléphone : {CFG['phone']['display']}</p>
<h2>Hébergement</h2><p>{e(lg['host'])}</p>
<h2>Nature des informations</h2><p>Ce site a pour objet l'information des patients, conformément aux articles R.4127-13 et R.4127-19-1 du code de la santé publique. Les informations présentées sont générales et ne remplacent pas une consultation médicale.</p>
<h2>Données personnelles et cookies</h2><p>Ce site ne dépose aucun cookie, n'utilise aucun outil de mesure d'audience et ne collecte aucune donnée personnelle. La prise de rendez-vous s'effectue sur Doctolib, qui dispose de sa propre politique de confidentialité.</p>
</article>"""
    write("mentions-legales.html", page(lang="fr", path="mentions-legales.html", title=f"Mentions légales — {NAME}",
                                        description="Mentions légales du site.", body=body, graph=[person_node()]))


def build_meta(pathos):
    urls = ["", "en/", "pathologies/", "publications.html", "mentions-legales.html"] + [f"pathologies/{p['slug']}.html" for p in pathos]
    sm = "".join(f"<url><loc>{BASE}/{u}</loc><lastmod>{CFG['updated']}</lastmod></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
            "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended"]
    write("robots.txt", "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    pages = "\n".join(f"- [{p['h1']}]({BASE}/pathologies/{p['slug']}.html): {p['description']}" for p in pathos)
    write("llms.txt", f"# {NAME}\n\n> {LEAD_FR}\n\n## Pages\n\n- [Accueil]({BASE}/): présentation, pathologies, lieux\n"
                      f"- [English]({BASE}/en/): presentation in English\n- [Publications]({BASE}/publications.html): articles indexés dans PubMed\n"
                      f"{pages}\n\n## Rendez-vous\n\n- [Doctolib]({L['doctolib']})\n")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "static", DIST, dirs_exist_ok=True)
    (DIST / "CNAME").write_text(CFG["cname"] + "\n")
    order = ["canal-carpien", "maladie-de-dupuytren", "doigt-a-ressaut", "rhizarthrose", "walant"]
    pathos = [parse_md(p) for p in (ROOT / "content" / "fr" / "pathologies").glob("*.md")]
    # Fiches not yet validated by the surgeon carry "status: brouillon": excluded from the public
    # build, included when PREVIEW=1 (local review).
    if not os.environ.get("PREVIEW"):
        pathos = [p for p in pathos if p.get("status") != "brouillon"]
    pathos.sort(key=lambda p: (list(GROUPS).index(p.get("group", "autres")) if p.get("group") in GROUPS else 9, order.index(p["slug"]) if p["slug"] in order else 99, p["h1"]))
    build_home_fr(pathos)
    build_home_en()
    for p in pathos:
        build_pathology(p, pathos)
    build_index(pathos)
    build_publications()
    build_legal()
    build_meta(pathos)
    (DIST / ".nojekyll").write_text("")
    print(f"Built {len(list(DIST.rglob('*.html')))} pages into {DIST}")


if __name__ == "__main__":
    main()
