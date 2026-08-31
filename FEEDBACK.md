# Capturing the feedback

GitHub Pages is a **static host** - there is no server behind the page to receive a
form post. So the lab has to hand its data to something else.

Participants' ratings, comments and new prompts always save to their own browser
(`localStorage`) as they go, so nothing is lost regardless of which option you pick.
The **Download .json / .csv** buttons are always present as a fallback.

---

## Option 1 - Email  (default, and what the SWA labs use)

One button for the participant. The lab copies their feedback to the clipboard
**and** opens their mail client with a pre-addressed, pre-written message. They
check it and press Send.

```
python build.py mail="you@microsoft.com"
```

Per-lab addresses if Care and Finance should go to different people:

```
python build.py caremail="a@x.com" finmail="b@x.com"
```

### Why the clipboard copy as well

`mailto:` has a practical ceiling around 2000 characters once URL-encoded. A
participant who rates fifteen prompts and writes two of their own will exceed it,
and the browser truncates silently. So the lab does both: under the ceiling the
whole thing goes into the message body; over it, the body carries a readable head
plus a line telling the participant to press Ctrl+V, and the full text is already
on their clipboard. Nothing is lost either way.

### What it costs you

You get a readable email per participant rather than structured rows. If you want
rows, paste the bodies into the same shape as `feedback-sample.json`, or use
Option 2. For a session-sized audience the email is usually the better trade -
there is nothing to build, nothing to maintain, and nothing to remediate.

---

## Option 2 - Microsoft Forms

Higher fidelity than email if you want the submitter's identity attached and the
responses landing in a workbook automatically.

1. Create a Form with one **Long answer** question, e.g. *"Paste your lab feedback
   here"*. Add short-answer questions for **Name**, **Business unit** and **Role**
   if you want them separated.
2. Copy the Form's share link.
3. Build with it:

```
python build.py form="https://forms.office.com/r/XXXXXXXX"
```

The button copies the participant's feedback to the clipboard and opens the Form
in a new tab - they paste with Ctrl+V and press Submit. This is the same pattern
used in the Manulife champion walkthrough, so it is proven with a live audience.

Forms authenticates the submitter with their own account, so you get identity for
free and there is no endpoint anywhere in the page.

---

## Option 3 - Export only (the fallback)

No destination configured. Participants use **Download .json**, **Download .csv**
or **Open an email**. Fine as a safety net; do not rely on it as your only path -
in self-serve use, almost nobody downloads a file and emails it to someone. The
export buttons stay available under every option above.

---

## Power Automate HTTP flows - do not use

The original version of these labs POSTed to a Power Automate flow with a
**"When an HTTP request is received"** trigger set to **"Who can trigger the flow?
= Anyone"**. That is a security finding:

| | |
|---|---|
| Control | **LCNC-PP-82** |
| Rule | **ZN_P00145** - "Flow is exposed to the Internet" |
| Severity | **High** (Oversharing / Least Privilege) |
| Standard | 09.01.01-05: Internet IP Surface Area |
| Risk | Anyone holding the trigger URL can run the flow |

The documented remediation is to delete the flow, or restrict the trigger to
**"Specific users in my tenant"** and list the allowed Entra IDs. The second
option does not work for a customer-facing lab - the participants are Southwest
employees, outside our tenant - so **the flow was deleted on 2026-08-31** and the
feedback it had already collected was preserved.

`build.py` now refuses a `flow=` argument so this cannot be rebuilt by accident.

Guidance: https://eng.ms/docs/microsoft-security/ciso-organization/sr-assurance/productivity-security-service/power-platform-service/lcnc-security-monitoring/troubleshooting-guides/lcnc-pp-82

### "Could it write the feedback into the GitHub repo?"

No. That needs a token in the page. The token sits inside the encrypted payload,
so it is not readable without the passphrase, but any participant who unlocks the
lab can pull it out of memory - and a leaked token with `repo` scope lets someone
rewrite or delete the repo, including the labs themselves. Pre-filled **New Issue**
URLs avoid the token but require every participant to have a GitHub account with
access to the repo, which Southwest employees will not have.

---

## What you get back

See `feedback-sample.json` for the exact shape of a submission: the role, optional
name and team, an average star rating, one entry per rated prompt (with its library
reference number and KPI theme so it joins straight back to your workbook), and
every new prompt the participant wrote. The email body in Option 1 carries the same
information in readable form.
