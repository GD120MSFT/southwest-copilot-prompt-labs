# Capturing the feedback

GitHub Pages is a **static host** — there is no server behind the page to receive a
form post. So the lab has to hand its data to something else. Three options, in
the order I'd recommend them.

Participants' ratings, comments and new prompts always save to their own browser
(`localStorage`) as they go, so nothing is lost regardless of which option you pick.
The **Download .json / .csv / email** buttons are always present as a fallback.

---

## Option 1 — Power Automate HTTP flow  (recommended)

One button for the participant, structured rows for you. This is the only option
with zero copy-paste.

### Build the flow

1. Go to **make.powerautomate.com** → **Create** → **Instant cloud flow** → skip the
   trigger picker → search for **"When an HTTP request is received"**.
2. In the trigger, click **Use sample payload to generate schema** and paste the
   sample in `feedback-sample.json` (in this repo). That gives you typed fields.
3. Set **Who can trigger the flow?** to **Anyone**. (The URL contains a signature —
   treat it as a secret. See the security note below.)
4. Add an action to store it. Two good shapes:

   **Simplest — one row per submission** (Excel or a SharePoint list):
   add **Add a row into a table** / **Create item** and map:
   `submissionId`, `submitted`, `businessUnit`, `role`, `name`, `team`,
   `ratingCount`, `newPromptCount`, `averageStars`.
   Then add a second column holding `ratings` and `newPrompts` as raw JSON.

   **Better for analysis — one row per rating**: add **Apply to each** over
   `ratings`, and inside it **Add a row into a table** mapping
   `libraryRef`, `title`, `application`, `kpi`, `stars`, `comment` plus the
   submission-level fields. Repeat a second **Apply to each** over `newPrompts`
   writing into a second table.

5. **Save**, then copy the **HTTP POST URL** from the trigger.

### Point the labs at it

From `Working\_labs`:

```
python build.py flow="https://prod-XX.westus.logic.azure.com:443/workflows/..."
```

Rebuild, re-copy the HTML into the repo, push. The **Send my feedback** button
now posts straight into your table.

Per-lab endpoints if you want Care and Finance in different tables:

```
python build.py careflow="https://..." finflow="https://..."
```

### Notes that will save you an afternoon

- The lab posts with `Content-Type: text/plain` **on purpose**. That keeps it a
  CORS "simple request" so the browser never sends a preflight `OPTIONS`, which
  Power Automate does not answer. Power Automate still parses the body as JSON if
  you generated the schema in step 2. Don't "fix" this to `application/json`.
- If a post fails, the participant sees a clear message and their data stays in
  the browser — they can still export it.
- Test it before the session: open the lab, rate one prompt, hit send, confirm
  the row lands.

---

## Option 2 — Microsoft Forms

Lower fidelity, but nothing to maintain and the data lands in Excel automatically.

1. Create a Form with one **Long answer** question, e.g. *"Paste your lab feedback
   here"*. Add short-answer questions for **Name**, **Business unit** and **Role**
   if you want them separated.
2. Copy the Form's share link.
3. Build with it:

```
python build.py form="https://forms.office.com/r/XXXXXXXX"
```

The button then copies the participant's feedback to the clipboard and opens the
Form in a new tab — they paste with Ctrl+V and press Submit. This is the same
pattern used in the Manulife champion walkthrough, so it's proven with a live
audience.

Responses land in the Form's Excel workbook. You get one long text blob per
person rather than one row per rating.

---

## Option 3 — Export only (the default today)

No endpoint configured. Participants use **Download .json**, **Download .csv** or
**Open an email**, and send it to the change lead. Fine for a facilitated session
where you're in the room; weak for self-serve use afterward.

---

## Security, stated plainly

- The flow URL is a **bearer secret**: anyone who has it can POST to your flow.
  It sits inside the encrypted lab payload, so it is not readable without the
  passphrase — but a participant could extract it after unlocking.
- Worst realistic case is junk rows in a feedback table. Do **not** point the flow
  at anything that writes to a production system, and don't reuse the flow for
  anything sensitive.
- If that risk is unacceptable, use Option 2 (Forms) — Forms authenticates the
  submitter with their Southwest account and you get identity for free.
- Rotate the flow URL by regenerating the trigger URL in Power Automate and
  rebuilding the labs.

## What you get back

See `feedback-sample.json` for the exact shape. Per submission you get the role,
optional name and team, an average star rating, one entry per rated prompt
(with its library reference number and KPI theme so it joins straight back to
your workbook), and every new prompt the participant wrote.
