# Sucket Electronic API — سوکت الکترونیک

The Django REST API for the **سوکت الکترونیک** client project, covering an automotive-connector catalog and account/cart/order code. The [Next.js frontend](https://github.com/boyInShadows/sucketElectronic) is maintained in its own repository; this checkout does not contain its user interface.

**Status:** existing client backend with a verified local catalog connection. A live deployment, SMS delivery, real payments and complete checkout were not verified in this pass. Client-project involvement is confirmed; sole authorship of both repositories is not claimed.

## Run locally

Use **Python >=3.10** for the pinned Django 5.2.4 requirements. Verification used Python 3.13.16 in an isolated environment.

```bash
git clone https://github.com/boyInShadows/SucketElectronicBackend.git
cd SucketElectronicBackend
python -m venv .venv
```

Activate `.venv` using `.venv\Scripts\Activate.ps1` on Windows or `source .venv/bin/activate` on a POSIX shell, then install the actual dependency file:

```bash
python -m pip install -r requirements.txt
```

Supply **`DJANGO_SECRET_KEY` with at least 32 characters** through the process environment before running Django. Real credentials on the maintainer's Windows workstation belong in Windows user environment variables. The old source-embedded key has been removed from active settings; do not reuse it from Git history.

```bash
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver
```

Open `http://localhost:8000/api/products/` or `/api/categories/`. Use a fresh local database; preserve existing customer data and uploads. Apply checked-in migrations rather than running `makemigrations` as an installation step. The [public setup guide](docs/README.md) covers origins, admin access, configuration and deployment limits.

## API and frontend connection

The catalog uses Django REST Framework; its active protected-request configuration uses **SimpleJWT bearer tokens**, rather than the previous README's unqualified session-auth claim. The inspected catalog permits public reads and checks admin access for writes. Account, cart and order viewsets exist, but their complete behavior is not established by the catalog tests.

For local frontend review, start the separate Next.js app with `NEXT_PUBLIC_API_URL=http://localhost:8000` and `INTERNAL_API_URL=http://localhost:8000`. Browser origins, trailing-slash API routes and image URLs must match its configuration. A real Next-to-Django product request returned HTTP 200 against four synthetic records. [Actual frontend captures](https://github.com/boyInShadows/sucketElectronic/tree/main/docs/artifacts) show that local pair.

## Checks and known limits

The original `ecommerce/tests.py` was a scaffold, and initial discovery ran zero tests. This change adds **four passing tests** for public catalog reads, invalid filtering, denied anonymous writes and rejection of a missing signing key. The key regression failed on the original source default and passed after runtime-key validation. [Recorded results](docs/artifacts/verification.json) distinguish this bounded coverage from a full application suite.

Django checks still report `urls.W005` for duplicate admin namespaces. The settings remain development-oriented, including DEBUG and broad CORS behavior; they are not production-ready simply because the catalog runs. No real Twilio/SMS/payment service was configured or contacted, and Python dependency vulnerability scanning was not performed. See [configuration and release limits](docs/README.md#configuration-and-release-limits).

## Persian overview

این مخزن API پروژه مشتری «سوکت الکترونیک» است و رابط کاربری Next.js در مخزن جداگانه قرار دارد. ارتباط محلی فهرست محصولات با داده آزمایشی بررسی شده است. برای اجرای نسخه جدید باید کلید امضای مستقل را از متغیر محیطی تأمین کرد؛ تست‌های این بررسی به معنی تأیید پرداخت واقعی یا آماده‌بودن تنظیمات برای محیط تولید نیستند.

This project remains part of the Sucket Electronic platform. Existing ownership and asset credits remain applicable; no new license or unsupported sole-authorship claim is introduced.
