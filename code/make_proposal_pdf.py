"""Render PROPOSAL_v3.md to the DSS submission PDF via headless Chrome.

No pandoc or LaTeX on this machine, but Chrome is present and its print engine
handles @page margins, page breaks and widow/orphan control well enough for a
three-page proposal. Markdown handling is deliberately narrow -- this converts
one known document, not arbitrary input.

  python code/make_proposal_pdf.py
"""
import html
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "PROPOSAL_v3.md"
OUT_HTML = ROOT / "build" / "proposal.html"
OUT_PDF = ROOT / "Tran_ThucBao_DSS_F26.pdf"

CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

CSS = """
@page { size: Letter; margin: 0.68in 0.75in; }
@page :first { margin-top: 0.55in; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Source Serif Pro", Georgia, "Times New Roman", serif;
       font-size: 9.6pt; line-height: 1.31; color: #111; margin: 0; }
h1, h2, h3 { font-family: "Segoe UI", Helvetica, Arial, sans-serif;
             color: #0d2b33; margin: 0; page-break-after: avoid; }
h1 { font-size: 12.2pt; margin: 10pt 0 4pt; padding-bottom: 2pt;
     border-bottom: 1.2pt solid #0d2b33; letter-spacing: .01em; }
h2 { font-size: 10.4pt; margin: 8pt 0 3pt; }
h3 { font-size: 9.8pt; margin: 6pt 0 2pt; }
p { margin: 0 0 4.5pt; text-align: justify; hyphens: auto; orphans: 2; widows: 2; }
strong { color: #08252c; }
hr { border: none; border-top: .6pt solid #c3d0d3; margin: 10pt 0; }
table { border-collapse: collapse; width: 100%; margin: 5pt 0 6pt;
        font-size: 8.4pt; page-break-inside: avoid; }
th, td { border: .5pt solid #b9c7ca; padding: 2pt 5pt; text-align: left;
         vertical-align: top; }
th { background: #eef3f4; font-family: "Segoe UI", Helvetica, sans-serif;
     font-size: 8.2pt; font-weight: 600; }
td:nth-child(n+2) { font-variant-numeric: tabular-nums; }
ul, ol { margin: 0 0 4.5pt; padding-left: 14pt; }
li { margin: 0 0 2pt; }
code { font-family: Consolas, "Courier New", monospace; font-size: 8.8pt;
       background: #f1f5f6; padding: 0 2pt; }
.hdr { font-size: 9pt; line-height: 1.4; margin-bottom: 6pt; }
.title { font-family: "Segoe UI", Helvetica, sans-serif; font-size: 13.5pt;
         font-weight: 600; color: #0d2b33; margin: 6pt 0 2pt; }
.synopsis { background: #f6f9f9; border-left: 2.5pt solid #0d6672;
            padding: 6pt 9pt; margin: 6pt 0 7pt; page-break-inside: avoid; }
.synopsis h2 { margin-top: 0; }
.refs { font-size: 8.3pt; line-height: 1.26; }
h1.refhead { page-break-before: always; }
.refs li { margin-bottom: 2.5pt; }
"""


def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def convert(md: str) -> str:
    out, i, lines = [], 0, md.split("\n")
    while i < len(lines):
        ln = lines[i]
        if re.match(r"^\s*\|", ln) and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln)
            i += 2
            rows = []
            while i < len(lines) and re.match(r"^\s*\|", lines[i]):
                rows.append(cells(lines[i])); i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>")
            for r in rows:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append("</tbody></table>")
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", ln)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if re.match(r"^---+\s*$", ln):
            out.append("<hr>"); i += 1; continue
        if re.match(r"^\s*[-*]\s+", ln) or re.match(r"^\s*\d+\.\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.\s+", ln))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and (re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i]) or
                                      (items and lines[i].startswith("   ") and lines[i].strip())):
                if re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i]):
                    items.append(re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", lines[i]))
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            cls = ' class="refs"' if ordered and len(items) > 6 else ""
            out.append(f"<{tag}{cls}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        if not ln.strip():
            i += 1; continue
        para = [ln]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,3}\s|---+\s*$|\s*\||\s*[-*]\s|\s*\d+\.\s)", lines[i]):
            para.append(lines[i]); i += 1
        out.append(f"<p>{inline(' '.join(x.strip() for x in para))}</p>")
    return "\n".join(out)


def main() -> int:
    md = SRC.read_text(encoding="utf-8")
    head, rest = md.split("---", 1)[0], md.split("---", 1)[1]
    hdr_lines = [l for l in head.split("\n") if l.strip() and not l.startswith("# ")]
    title = next((l.split("**Title:**")[1].strip() for l in hdr_lines if "**Title:**" in l), "")
    meta = "<br>".join(inline(l) for l in hdr_lines if "**Title:**" not in l)

    body = convert(rest)
    # wrap the synopsis block so it reads as a distinct element
    body = body.replace("<h2>Synopsis", '<div class="synopsis"><h2>Synopsis', 1)
    body = body.replace("<hr>\n<h1>A. Introduction</h1>", "</div>\n<h1>A. Introduction</h1>", 1)

    doc = (f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
           f"<style>{CSS}</style></head><body>"
           f"<div class='hdr'>{meta}</div>"
           f"<div class='title'>{inline(title)}</div>{body}</body></html>")
    OUT_HTML.parent.mkdir(exist_ok=True)
    OUT_HTML.write_text(doc, encoding="utf-8")
    print(f"html: {OUT_HTML} ({len(doc)} bytes)")

    exe = next((c for c in CHROME if pathlib.Path(c).exists()), None) or shutil.which("chrome")
    if not exe:
        print("no Chrome/Edge found; HTML written, convert manually")
        return 1
    cmd = [exe, "--headless", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if OUT_PDF.exists():
        print(f"pdf : {OUT_PDF} ({OUT_PDF.stat().st_size/1024:.0f} KB)")
        return 0
    print("chrome failed:", r.stderr[-500:])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
