# Southwest · Copilot Prompt Labs

Two interactive, passphrase-protected hands-on labs that run the 90-minute persona
training session and stay usable self-serve afterward.

| Lab | File | Contents |
|---|---|---|
| Customer Care | `customer-care.html` | 41 prompts, 6 roles (incl. the session Demo role), sections gated |
| Finance | `finance.html` | 30 prompts, 6 roles |

**Customer Care v2 (Aug 2026)** runs the "Prompt to Practice" session:
sections unlock in order (`?facilitator=1` opens everything for the presenter);
the spine is Housekeeping -> Anatomy of a prompt -> Your prompt -> Day in the life
-> hands-on; CARE's own response-drafting prompt ships as library entry `C1` and is
pulled apart against Goal / Context / Source / Expectations; every prompt can be
colour-coded in place with the **Show anatomy** toggle; the library carries prompts
only (the scored use cases live with the change team).

## Publish on GitHub Pages

1. Create a **private or public** repo (Pages works either way on GitHub Team/Enterprise;
   on a free personal account Pages requires a public repo).
2. Copy the contents of this folder into the repo root, or into a `docs/` folder.
3. Repo **Settings -> Pages -> Source: Deploy from a branch**, branch `main`,
   folder `/ (root)` or `/docs` to match step 2.
4. Wait ~60 seconds. The lab is at `https://<org>.github.io/<repo>/`.

`.nojekyll` is included so files are served as-is.

## The passphrase

The lab content is **AES-256-GCM encrypted** with a key derived from the passphrase
via PBKDF2-SHA256 (250,000 iterations). The ciphertext is embedded in the page.
Nothing readable ships in the HTML — view-source shows only base64. There is no
server, so this is the strongest protection available on a static host.

Current passphrases are set at build time. To rotate them:

```
python build.py care=NewCarePhrase finance=NewFinancePhrase
```

then re-copy the regenerated HTML files into the repo.

**Caveats, stated plainly:**
- Anyone with the passphrase can share the passphrase. This stops casual/public access
  and search-engine indexing; it is not access control tied to identity.
- It does not replace a sensitivity label. Keep customer and financial data out of it —
  all practice data here is fictional (LoneStar Air).
- If you need identity-based access, host the same files on a SharePoint site or behind
  Cloudflare Access / Entra instead, and drop the passphrase gate.

## Collecting feedback

GitHub Pages is static, so there is no backend. Participants' ratings and prompt ideas
save to their own browser (`localStorage`) as they go.

**See `FEEDBACK.md` for the full setup.** Short version:

| Option | Participant effort | What you get | Set it up |
|---|---|---|---|
| **Email** (default) | One button, then Send | A written email per person, in your inbox | `python build.py mail="<address>"` |
| **Microsoft Forms** | Copy, paste, submit | One text blob per person, in the Form's workbook | `python build.py form="<url>"` |
| **Export only** | Download and email | `.json` / `.csv` / pre-filled email | `SUBMIT` mode `none` |

> **Power Automate HTTP flows are not an option here.** An unauthenticated
> "When an HTTP request is received" trigger violates Microsoft control
> **LCNC-PP-82 / ZN_P00145** ("Flow is exposed to the Internet", High severity).
> The flow that backed this lab was deleted on 2026-08-31 to remediate the
> finding, and `build.py` now refuses a `flow=` argument.

The export buttons are always available as a fallback, whichever option you pick.

## Practice data

`assets/` contains fictional datasets for the carrier **LoneStar Air**. No Southwest data
is present in this repo. Regenerate with `python make_data.py`.

## Rebuilding

Source lives in `01-Accounts/Southwest Airlines/Working/_labs/` (OneDrive).
The build output deliberately lands **outside** OneDrive at
`C:/Users/<you>/Repos/swa-copilot-prompt-labs` — Purview auto-labeling encrypts
`.xlsx` files written into the synced account folders, which silently corrupts the
practice datasets for a static host. Override with the `SWA_LAB_OUT` environment variable.

```
pip install openpyxl cryptography
python make_data.py     # practice datasets -> <out>/assets
python build.py         # labs -> <out>
```
