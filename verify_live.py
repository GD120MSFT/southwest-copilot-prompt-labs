"""Verify the LIVE published labs by decrypting them, exactly as a participant's
browser would. Grep can't see the links -- they're inside the encrypted payload."""
import re, json, base64, hashlib, urllib.request
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

BASE = 'https://gd120msft.github.io/southwest-copilot-prompt-labs/'
LABS = [('customer-care.html', 'LoneStar-Care-2026'),
        ('finance.html', 'LoneStar-Finance-2026')]

for f, pw in LABS:
    html = urllib.request.urlopen(BASE + f).read().decode('utf-8')
    m = re.search(r'id="payload"[^>]*>([A-Za-z0-9+/=]+)<', html)
    blob = json.loads(base64.b64decode(m.group(1)))
    key = hashlib.pbkdf2_hmac('sha256', pw.encode(), base64.b64decode(blob['s']), blob['n'], 32)
    raw = AESGCM(key).decrypt(base64.b64decode(blob['i']), base64.b64decode(blob['c']), None)
    d = json.loads(raw)
    txt = raw.decode('utf-8')

    print('=' * 78)
    print('%s  --  decrypted OK, %d prompts, %d assets' % (f, len(d['prompts']), len(d['assets'])))
    for g in d.get('links', []):
        print('  [%s]' % g['h'])
        for i in g['items']:
            print('     %-32s %s' % (i['t'][:32], i['u'][:80]))
    print('  [Microsoft]')
    for l in d.get('msLinks', []):
        print('     %-32s %s' % (l['t'][:32], l['u'][:80]))
    print('  where it lives : %s' % d['whereItLives'][:100])
    print('  submit mode    : %s' % d['submit']['mode'])
    print('  tracking params in payload : %s' % ('xsdata' in txt))
    print('  dead notebooks link        : %s' % ('b1a2c3d4' in txt))
    print('  placeholder text           : %s' % ('Ask your change lead' in txt))
