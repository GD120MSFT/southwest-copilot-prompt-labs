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
print("demo day   :", [(i["t"], i["n"]) for i in d["day"]["demo"]])

fails = []
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
