#!/usr/bin/env python3
"""Refresh data/publications.json from PubMed and ORCID.

PubMed (NCBI E-utilities) gives the indexed articles with full metadata.
ORCID adds works that PubMed does not index; their metadata is completed from
Crossref when they have a DOI. Run weekly by the GitHub Actions workflow.

If a source is unreachable, its previous entries are kept, so a network hiccup
never empties the list on the site.
"""
import datetime
import json
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "publications.json"
UA = {"User-Agent": "dr-cievet-bonfils-site (mailto:contact@dr-cievet-bonfils.fr)"}
ARTICLE_TYPES = {"journal-article", "review", "book-chapter", "book", "editorial", "letter"}


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def norm_doi(doi):
    doi = (doi or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi


def fetch_pubmed(cfg):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    q = urllib.parse.urlencode({"db": "pubmed", "term": cfg["pubmed_query"], "retmax": 500, "retmode": "json"})
    ids = get_json(base + "esearch.fcgi?" + q)["esearchresult"]["idlist"]
    ids = [i for i in ids if i not in cfg.get("pubmed_exclude", [])]
    if not ids:
        return []
    q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    summary = get_json(base + "esummary.fcgi?" + q)["result"]
    items = []
    for pmid in summary.get("uids", []):
        rec = summary[pmid]
        doi = next((a["value"] for a in rec.get("articleids", []) if a.get("idtype") == "doi"), "")
        authors = [a["name"] for a in rec.get("authors", []) if a.get("authtype") == "Author"]
        items.append({
            "pmid": pmid, "doi": norm_doi(doi), "source": "pubmed", "type": "journal-article",
            "year": (rec.get("pubdate") or rec.get("epubdate") or "")[:4],
            "title": rec.get("title", "").strip(), "authors": authors[:6], "et_al": len(authors) > 6,
            "journal": rec.get("source", ""), "volume": rec.get("volume", ""),
            "issue": rec.get("issue", ""), "pages": rec.get("pages", ""),
        })
    return items


def crossref(doi):
    try:
        msg = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
    except Exception:
        return {}
    authors = [f"{a.get('family', '')} {''.join(p[0] for p in a.get('given', '').replace('-', ' ').split() if p)}".strip()
               for a in msg.get("author", [])]
    return {
        "title": (msg.get("title") or [""])[0].strip(),
        "authors": authors[:6], "et_al": len(authors) > 6,
        "journal": (msg.get("short-container-title") or msg.get("container-title") or [""])[0],
        "volume": msg.get("volume", ""), "issue": msg.get("issue", ""), "pages": msg.get("page", ""),
    }


def fetch_orcid(cfg):
    data = get_json(f"https://pub.orcid.org/v3.0/{cfg['orcid_id']}/works", {"Accept": "application/json"})
    items = []
    for group in data.get("group", []):
        s = group["work-summary"][0]
        ext = {e["external-id-type"]: e["external-id-value"]
               for e in (s.get("external-ids") or {}).get("external-id", [])}
        date = s.get("publication-date") or {}
        items.append({
            "pmid": ext.get("pmid", ""), "doi": norm_doi(ext.get("doi", "")), "source": "orcid",
            "type": s.get("type", "").lower().replace("_", "-"),
            "year": ((date.get("year") or {}).get("value") or ""),
            "title": ((s.get("title") or {}).get("title") or {}).get("value", "").strip(),
            "journal": (s.get("journal-title") or {}).get("value", "") if s.get("journal-title") else "",
            "authors": [], "et_al": False, "volume": "", "issue": "", "pages": "",
        })
    return items


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    previous = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"items": []}
    prev_by_source = {s: [i for i in previous["items"] if i.get("source", "pubmed") == s] for s in ("pubmed", "orcid")}

    try:
        pubmed = fetch_pubmed(cfg)
        print(f"PubMed: {len(pubmed)} items")
    except Exception as exc:
        print(f"PubMed unreachable ({exc}); keeping previous PubMed items.", file=sys.stderr)
        pubmed = prev_by_source["pubmed"]
    try:
        orcid = fetch_orcid(cfg)
        print(f"ORCID: {len(orcid)} works")
    except Exception as exc:
        print(f"ORCID unreachable ({exc}); keeping previous ORCID items.", file=sys.stderr)
        orcid = None

    seen_doi = {i["doi"] for i in pubmed if i["doi"]}
    seen_pmid = {i["pmid"] for i in pubmed if i["pmid"]}
    seen_title = {i["title"].lower().rstrip(".") for i in pubmed}
    extra = []
    if orcid is None:
        extra = prev_by_source["orcid"]
    else:
        for w in orcid:
            if (w["doi"] and w["doi"] in seen_doi) or (w["pmid"] and w["pmid"] in seen_pmid) \
                    or w["title"].lower().rstrip(".") in seen_title or not w["title"]:
                continue
            if w["doi"]:
                w.update({k: v for k, v in crossref(w["doi"]).items() if v})
            extra.append(w)
            seen_title.add(w["title"].lower().rstrip("."))

    items = pubmed + extra
    if not items:
        print("No items from any source; keeping existing file.")
        return 0
    items.sort(key=lambda x: (x["year"] or "0", x.get("pmid") or ""), reverse=True)
    OUT.write_text(json.dumps({"fetched": datetime.date.today().isoformat(), "source": "PubMed + ORCID",
                               "items": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(items)} publications written ({len(extra)} from ORCID only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
