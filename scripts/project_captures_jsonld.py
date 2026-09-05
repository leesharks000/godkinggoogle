#!/usr/bin/env python3
"""project_captures_jsonld.py — the machine-readable half of the captures window (2026-09-05).

The page renders from the canonical registry at load (client-side, invisible to a crawler). This script writes,
into the same page's static HTML, what a machine gets without executing anything:
  - <link rel="alternate" type="application/json"> to the canonical registry file
  - a JSON-LD Dataset naming the canonical registry as `distribution` / `isBasedOn`, with `hasPart` for every
    capture this window shows (id, name, date, surface, canonical seat), regenerated from the canonical file.
It holds no copy of the registry beyond that index; it is re-run whenever the registry changes (workflow).
Usage: python3 scripts/project_captures_jsonld.py captures/index.html [--filter REGEX] [--all]
"""
import json, re, sys, urllib.request, html, datetime
REG = "https://www.alexanarch.org/data/EA-WG-CAPTURES-01.json"
def main():
    page = sys.argv[1]; flt = None; allc = "--all" in sys.argv
    if "--filter" in sys.argv: flt = re.compile(sys.argv[sys.argv.index("--filter")+1], re.I)
    R = json.load(urllib.request.urlopen(REG, timeout=60)); E = R["entries"]
    def rel(e): return allc or not flt or flt.search(" ".join(str(e.get(k) or "") for k in ("q","d","transcript","s")))
    shown = [e for e in E if rel(e)]
    ld = {"@context": "https://schema.org", "@type": "Dataset",
          "@id": "https://www.godkinggoogle.com/captures#dataset",
          "name": "Capture Registry — captures on Google surfaces and of the God-King Google critique (window onto EA-WG-CAPTURES-01)",
          "description": f"{len(shown)} of {len(E)} captures in the canonical Capture Registry (v{R.get('version')}) shown by this window. Each part links to its canonical seat on alexanarch.org; the registry file is the distribution.",
          "isBasedOn": {"@type": "Dataset", "@id": REG, "name": "EA-WG-CAPTURES-01 — the Capture Registry", "url": "https://www.alexanarch.org/captures/"},
          "distribution": {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": REG},
          "license": "https://creativecommons.org/licenses/by/4.0/",
          "creator": {"@type": "Person", "name": "Lee Sharks", "identifier": "https://orcid.org/0009-0000-1599-0703"},
          "dateModified": datetime.date.today().isoformat(), "version": R.get("version"),
          "hasPart": [{"@type": "Observation", "@id": f"https://www.alexanarch.org/captures/#{e['slug']}", "name": e.get("q"), "observationDate": e.get("date"),
                        "measurementTechnique": e.get("surface"), "url": f"https://www.alexanarch.org/captures/#{e['slug']}",
                        "description": (e.get("d") or "")[:300]} for e in shown]}
    s = open(page, encoding="utf-8").read()
    block = '<link rel="alternate" type="application/json" href="' + REG + '" title="EA-WG-CAPTURES-01 (canonical registry)">\n<script type="application/ld+json" id="captures-dataset">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    s = re.sub(r'<link rel="alternate" type="application/json"[^>]*>\s*<script type="application/ld\+json" id="captures-dataset">.*?</script>', block, s, flags=re.S) if 'id="captures-dataset"' in s else s.replace('</head>', block + '\n</head>', 1)
    open(page, "w", encoding="utf-8").write(s)
    print(f"captures JSON-LD: {len(shown)} parts of {len(E)} (registry v{R.get('version')})")
if __name__ == "__main__": main()
