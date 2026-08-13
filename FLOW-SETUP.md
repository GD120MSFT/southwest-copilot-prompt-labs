# Build the flow — exact steps

The SharePoint list is already created and tested. This is the only piece left.

## What already exists

**List:** `Copilot Lab Feedback`
**Site:** `https://microsoft.sharepoint.com/teams/CT-50513`
(SOUTHWEST AIRLINES COMPANY_FY26 — ISD-PowerPlatAcceleration)
**Direct link:** https://microsoft.sharepoint.com/teams/CT-50513/Lists/Copilot%20Lab%20Feedback/AllItems.aspx
**List ID:** `d397cca1-60b2-4fb7-a21a-4567f5f3b6a8`

Columns (all created and write-tested):

| Column | Type | Holds |
|---|---|---|
| SubmittedAt | Date and time | when they pressed send |
| BusinessUnit | Text | Customer Care / Finance |
| ParticipantRole | Text | the role they picked in the lab |
| ParticipantName | Text | optional, "(anonymous)" if blank |
| ParticipantTeam | Text | optional |
| EntryType | Text | `Rating` or `New prompt` |
| LibraryRef | Text | the `#` from your library workbook |
| PromptTitle | Text | prompt title, or the new prompt's name |
| Application | Text | Copilot in Excel / Outlook / chat … |
| KPI | Text | the KPI theme it maps to |
| Stars | Number | 1–5 |
| Comment | Multi-line | what they said |
| PromptText | Multi-line | the full text of a prompt they wrote |
| AverageStars | Number | their average across the session |
| SubmissionId | Text | groups all rows from one person's submission |

---

## Build the flow (about 5 minutes)

### 1. New flow
**make.powerautomate.com** → **Create** → **Instant cloud flow** → **Skip** the trigger
picker → search **"When an HTTP request is received"** → add it.

### 2. Generate the schema
In the trigger, click **Use sample payload to generate schema** and paste the whole
contents of `feedback-sample.json` (next to this file). Click Done.

Set **Who can trigger the flow?** → **Anyone**.

### 3. Ratings → rows
**+ New step** → **Control** → **Apply to each**.
- *Select an output from previous steps*: `ratings`
- Inside it: **+ Add an action** → **SharePoint** → **Create item**

Fill it in:

| Field | Value (from the dynamic content picker) |
|---|---|
| Site Address | `https://microsoft.sharepoint.com/teams/CT-50513` |
| List Name | `Copilot Lab Feedback` |
| Title | `title` (current item) |
| SubmissionId | `submissionId` |
| SubmittedAt | `submitted` |
| BusinessUnit | `businessUnit` |
| ParticipantRole | `role` |
| ParticipantName | `name` |
| ParticipantTeam | `team` |
| EntryType | type the literal text `Rating` |
| LibraryRef | `libraryRef` (current item) |
| PromptTitle | `title` (current item) |
| Application | `application` (current item) |
| KPI | `kpi` (current item) |
| Stars | `stars` (current item) |
| Comment | `comment` (current item) |
| AverageStars | `averageStars` |

> If the picker offers two things called `title`, the one **inside** the Apply to each
> is the rating's title. The submission has no `title` of its own, so you can't pick wrong.

### 4. New prompts → rows
**+ New step** → another **Apply to each**, this time over `newPrompts`.
Inside it, another **SharePoint → Create item** with the same site and list:

| Field | Value |
|---|---|
| Title | `title` (current item) |
| SubmissionId | `submissionId` |
| SubmittedAt | `submitted` |
| BusinessUnit | `businessUnit` |
| ParticipantRole | `role` |
| ParticipantName | `name` |
| ParticipantTeam | `team` |
| EntryType | literal text `New prompt` |
| PromptTitle | `title` (current item) |
| PromptText | `prompt` (current item) |

### 5. Save and copy the URL
**Save.** Reopen the trigger — the **HTTP POST URL** is now filled in. Copy it and
send it to me.

### 6. I finish it
I rebuild both labs against that URL, submit a real test from the lab, show you the
rows it produced in the list, then delete the test rows. Then it's ready to share.

---

## Optional extras

**Email yourself on each submission** — after step 4, add **Outlook → Send an email (V2)**
to yourself with `name`, `businessUnit`, `ratingCount` and `averageStars` in the body.

**Respond to the lab** — the lab treats any 2xx as success, so you don't need a
Response action. Add one only if you want to return a custom message.

---

## Two things to know

**The flow URL is a secret.** Anyone holding it can POST to this flow. It lives inside
the encrypted lab payload, so it isn't readable without the passphrase, but a
participant could extract it after unlocking. The worst case is junk rows in this
list — which is exactly why this flow should only ever write here, and nowhere else.
To rotate it, regenerate the trigger URL in Power Automate and tell me; I'll rebuild.

**Content type is text/plain on purpose.** The lab posts with
`Content-Type: text/plain;charset=UTF-8` so the browser treats it as a CORS "simple
request" and never sends a preflight `OPTIONS` — which Power Automate does not answer.
Power Automate still parses the body as JSON because of the schema from step 2.
Don't change it to `application/json`; it will start failing in the browser.
