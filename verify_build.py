"""Decrypt the locally built labs and assert the v2 changes actually shipped."""
import re, json, base64, hashlib, sys, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))


def load(f, pw):
    h = open(os.path.join(BASE, f), encoding="utf-8").read()
    m = re.search(r'id="payload"[^>]*>([A-Za-z0-9+/=]+)<', h)
    b = json.loads(base64.b64decode(m.group(1)))
    k = hashlib.pbkdf2_hmac("sha256", pw.encode(), base64.b64decode(b["s"]), b["n"], 32)
    return json.loads(AESGCM(k).decrypt(base64.b64decode(b["i"]), base64.b64decode(b["c"]), None))


d = load("customer-care.html", "LoneStar-Care-2026")
print("sections   :", [s["id"] for s in d["sections"]])
print("gated      :", d["gated"])
print("personas   :", [p["id"] for p in d["personas"]])
print("day keys   :", list(d["day"].keys()))
print("prompts    :", len(d["prompts"]), " with anatomy:", sum(1 for p in d["prompts"] if p.get("seg")))
print("submit     :", d["submit"]["mode"], "..." + d["submit"]["url"][-24:])
print("framework  :", d["framework"]["name"], "|", d["framework"]["source"])
print("evaluate   :", len(d["evaluate"]["verdict"]), "verdicts,",
      len(d["evaluate"]["improvements"]), "improvements,", len(d["evaluate"]["extraMile"]), "extra")

c1 = [p for p in d["prompts"] if p["num"] == "C1"][0]
print("C1         :", c1["persona"], [s["r"] for s in c1["seg"]])
print("demo also  :", [p for p in d["personas"] if p["id"] == "demo"][0]["also"])
fails = []
print("demo day   :", [(i["t"], i["n"], len(i.get("u", []))) for i in d["day"]["demo"]])
print("case pack  :", len(d.get("casePack", [])), "files;", len(d["assets"]), "assets embedded")

pack = d.get("casePack", [])
if len(pack) != 8:
    fails.append("demo case pack is not 8 files")
for n in pack:
    a = d["assets"].get(n)
    if not a:
        fails.append("case pack file not embedded: " + n)
    elif not a["uri"].startswith("data:application/vnd.openxmlformats"):
        fails.append("case pack file has the wrong mime type: " + n)
    elif a["kb"] < 5:
        fails.append("case pack file looks empty: " + n)
if not d.get("casePackNote"):
    fails.append("case pack has no explanatory note")
for i, step in enumerate(d["day"]["demo"]):
    if not step.get("u"):
        fails.append("demo day step %d names no practice file" % (i + 1))
    for n in step.get("u", []):
        if n not in d["assets"]:
            fails.append("demo step %d points at a missing file %s" % (i + 1, n))
# the pack shipped under a second invented carrier -- make sure none of it leaked
import zipfile, io
for n in pack:
    a = d["assets"].get(n)
    if not a:
        continue
    raw = base64.b64decode(a["uri"].split(",", 1)[1])
    z = zipfile.ZipFile(io.BytesIO(raw))
    txt = " ".join(z.read(p).decode("utf-8", "ignore") for p in z.namelist()
                   if p.endswith(".xml") and ("document" in p or "sharedStrings" in p or "sheet" in p))
    if "kyline" in txt:
        fails.append("%s still mentions the original carrier" % n)

if [s["id"] for s in d["sections"]][:3] != ["housekeeping", "anatomy", "evaluate"]:
    fails.append("care sections not reordered")
if not d["gated"]:
    fails.append("care lab not gated")
if d["personas"][0]["id"] != "demo":
    fails.append("demo is not the default role")
if d["submit"]["mode"] != "flow" or "sig=" not in d["submit"]["url"] or d["submit"]["url"].endswith(".Trim()"):
    fails.append("feedback flow url is wrong: " + d["submit"]["url"][-40:])
if sum(1 for p in d["prompts"] if p.get("seg")) != len(d["prompts"]):
    fails.append("some prompts have no anatomy map")
for p in d["prompts"]:
    if "".join(s["t"] for s in p["seg"]) != p["text"]:
        fails.append("anatomy segments do not reassemble for #" + p["num"])
    if not p["c"]:
        fails.append("no Goal/Context/Source/Expectations for #" + p["num"])
# every day-in-the-life moment must resolve to a real prompt
nums = {p["num"] for p in d["prompts"]}
for role, items in d["day"].items():
    for it in items:
        if it["n"] not in nums:
            fails.append("day/%s points at missing prompt %s" % (role, it["n"]))
# borrowed sets must resolve too
for p in d["personas"]:
    for n in p.get("also", []):
        if n not in nums:
            fails.append("persona %s borrows missing prompt %s" % (p["id"], n))

f = load("finance.html", "LoneStar-Finance-2026")
print("\nfinance    :", [s["id"] for s in f["sections"]], "gated:", f["gated"],
      "| prompts:", len(f["prompts"]), "| submit:", f["submit"]["mode"])
if f["gated"]:
    fails.append("finance should not be gated")
if [s["id"] for s in f["sections"]][0] != "welcome":
    fails.append("finance sections changed")

print("\n" + ("FAIL:\n  " + "\n  ".join(fails) if fails else "ALL CHECKS PASSED"))
sys.exit(1 if fails else 0)
