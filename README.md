# Southwest · Copilot Prompt Labs

Two interactive, passphrase-protected hands-on labs that run the 90-minute persona
training session and stay usable self-serve afterward.

| Lab | File | Prompts |
|---|---|---|
| Customer Care | `customer-care.html` | 48 prompts, 10 use cases, 5 roles |
| Finance | `finance.html` | 36 prompts, 8 use cases, 6 roles |

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
save to their own browser (`localStorage`) and are exported from the **What's next** tab as
`.json`, `.csv`, or a pre-filled email.

To route feedback into a Microsoft Form instead, set `formsUrl` in `build.py`
(`build_payload`) to the Form URL and rebuild — a button appears on the last tab.

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
