# Backend setup and verification

## Local setup

Django 5.2.4 declares Python >=3.10. This pass used Python 3.13.16 and the exact versions in `requirements.txt`; the previous README's Python 3.8 minimum was incorrect. Use an isolated virtual environment and the declared dependency file:

```bash
git clone https://github.com/boyInShadows/SucketElectronicBackend.git
cd SucketElectronicBackend
python -m venv .venv
```

Activate `.venv` with `.venv\Scripts\Activate.ps1` on Windows or `source .venv/bin/activate` on a POSIX shell, then:

```bash
python -m pip install -r requirements.txt
python -m pip check
```

Before running Django commands, supply **`DJANGO_SECRET_KEY` with at least 32 characters** through the process environment. On the maintainer's Windows workstation, real secrets belong in Windows user environment variables; restart the terminal after changing them. Startup rejects an absent/short value. Never place real keys in repository files or command logs.

```bash
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver
```

Apply the existing migrations rather than generating new migrations during installation. A fresh checkout creates its own local `db.sqlite3`. Do not copy customer databases, users or uploaded media into test fixtures. An optional `python manage.py createsuperuser` creates a local administrative account; it does not transfer credentials to another database.

The server listens at `http://localhost:8000`. The public catalog is at `/api/products/` and `/api/categories/`; Django administration is at `/admin/`. Root `/` is not a storefront. The [Next.js frontend](https://github.com/boyInShadows/sucketElectronic) is a separate checkout, with its own npm lockfile and origin configuration.

## Frontend connection

Set frontend `NEXT_PUBLIC_API_URL` and `INTERNAL_API_URL` to the Django origin before starting/building Next. The usual frontend origin is `http://localhost:3000`; a different port or hostname needs a matching origin policy. The current Django settings include development-only broad CORS and DEBUG behavior. This pass used a temporary narrow local settings override for a synthetic test pair; deployed CORS was not changed.

For API clients, preserve trailing slashes. The REST configuration uses SimpleJWT bearer authentication for protected requests, while catalog list/filter routes permit public reads. The product/category write handlers check administrative access. These statements describe the inspected paths; they are not a full authorization audit.

Example public request with an empty or synthetic local database:

```bash
curl http://localhost:8000/api/products/
curl http://localhost:8000/api/categories/
```

The integration check created one synthetic category and four products in a separate SQLite file, then verified both public endpoints and the frontend's Next product proxy returned HTTP 200. The running frontend displayed those records; [frontend evidence](https://github.com/boyInShadows/sucketElectronic/tree/main/docs/artifacts) contains actual screenshots. No real account or payment service was used.

## Configuration and release limits

The previous source-embedded signing key has been removed from the active settings. Both Django and SimpleJWT now derive their signing configuration from the required runtime key. The old value remains in Git history and must not be reused. Plan a new key before deployment; rotation invalidates existing signed tokens/sessions. This change does not reset a database or rewrite the authentication flow.

`config/settings.py` remains a development configuration: DEBUG is enabled, allowed hosts need deployment configuration, and broad CORS must be reviewed. A production settings module must configure hosts, HTTPS/cookies, database/media persistence and provider secrets deliberately. Merely setting environment variables that this source does not read will not configure those settings.

Twilio configuration contains placeholder values; real SMS delivery was not configured or tested. The source includes carts, orders, users, articles and messages, but this pass verified the catalog boundary only. No payment gateway or production settlement was established. Do not infer PCI compliance or a complete checkout from the presence of order models.

Preserve original ownership and asset credits. No license is added, no upstream credit is removed and no sole authorship of the frontend/backend pair is claimed.

## Verification and bounded review

Base revision: `eff4519ebb40`. Local checks used Python 3.13.16, Django 5.2.4 and all 24 exact requirements in a fresh isolated environment.

| Check | Result |
|---|---|
| Declared requirements installation | All 24 pinned packages installed successfully |
| Initial `python manage.py test` | Zero tests discovered; the original `ecommerce/tests.py` was scaffold only |
| New `python manage.py test` | Four tests passed: public catalog, invalid filter, blocked anonymous writes and missing signing-key rejection |
| `python manage.py check` | Exit 0, with existing `urls.W005` duplicate admin namespace warning |
| Missing-key regression | Failed on the original source default; passed after requiring the runtime key |
| Synthetic integration | Real Django public product/category GETs and Next product proxy returned 200; original data untouched |

[Command outcomes](artifacts/verification.json) and [initial discovery](artifacts/test-discovery.json) distinguish actual results from absence of tests. The new CI runs dependency consistency, Django checks and tests with an ephemeral process-only key; hosted results are separate from local verification.

Review used codebase-memory project `SucketElectronicBackend-showcase`, generation `2026-10-29T20:28:29Z`, catalog view/model snippets and coverage checks. Material source was read directly where metadata was changed or requirements parsing was partial. Original migration files were applied to an isolated fixture database. This is not a complete security audit, dependency vulnerability scan or live service validation.

Remaining work includes production configuration, dependency/security maintenance, duplicate admin namespace cleanup, and full account/cart/order/SMS/payment checks. Existing customer databases, uploads and original dirty checkouts were preserved.
