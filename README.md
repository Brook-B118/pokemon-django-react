# Pokémon TCG Backend

A production-deployed REST API for searching Pokémon Trading Card Game cards and managing user favorites, built with Django and Django REST Framework. Built as a hands-on learning project to develop backend, cloud, and DevOps fundamentals from the ground up.

**Live API:** `https://api.poketcgproject.com`

**Swagger/OpenAPI docs:** `https://api.poketcgproject.com/api/schema/swagger-ui/`

---

## What it does

- Search the Pokémon TCG card database (proxied from the [TCGdex](https://tcgdex.dev/) API), with Redis-backed caching and rate limiting
- Register and log in with Google OAuth (OIDC) — no passwords stored
- Secure session handling via short-lived JWT access tokens and rotating, blacklisted refresh tokens stored in HTTP-only cookies
- Save and remove favorite cards per user, with favorite status returned inline in search results

---

## Tech stack

| Layer                 | Technology                                                  |
| --------------------- | ----------------------------------------------------------- |
| Language              | Python                                                      |
| Framework             | Django 5.2, Django REST Framework                           |
| Auth                  | Google OIDC, SimpleJWT (rotation + blacklisting)            |
| Database              | PostgreSQL                                                  |
| Cache / Rate limiting | Redis                                                       |
| Containerization      | Docker, Docker Compose (separate dev/prod configs)          |
| Reverse proxy / TLS   | Nginx, Let's Encrypt (Certbot)                              |
| Hosting               | AWS EC2 (custom VPC, security groups, Secrets Manager, IAM) |
| API docs              | drf-spectacular (OpenAPI/Swagger)                           |

---

## Architecture

The backend follows the [HackSoftware Django Styleguide](https://github.com/HackSoftware/Django-Styleguide), separating each app into:

- `views.py` — thin views (request/response only)
- `services.py` — business logic and side effects
- `selectors.py` — read/query logic
- `serializers.py` — input validation and shaping
- `throttles.py` — rate limiting

This keeps views free of business logic and makes each layer independently testable.

**Infrastructure** runs on a two-network Docker architecture: an internal-only network holds PostgreSQL and Redis (no public port mapping, only reachable by other containers), while a public-facing network exposes Nginx as the sole entry point, which reverse-proxies to the Django app over Gunicorn. The stack runs on a single EC2 instance in a public subnet (deliberately avoiding a NAT Gateway's recurring cost due to two-network Docker architecture) with a scoped IAM role pulling secrets from AWS Secrets Manager at boot via a systemd-managed startup script.

---

## API examples

All endpoints are prefixed with `/api/`.

### Search cards

```bash
curl "https://api.poketcgproject.com/api/cards/search/?name=pikachu&page=1"
```

Add an `Authorization: Bearer <access_token>` header to include `is_favorited` flags for the authenticated user.

### Register / log in with Google

```bash
curl -X POST https://api.poketcgproject.com/api/authentication/register/ \
  -H "Content-Type: application/json" \
  -d '{"credential": "<google-id-token>"}'
```

Returns a short-lived JWT access token in the response body and sets an HTTP-only, rotating refresh token cookie. Existing users hit the same flow via:

```bash
curl -X POST https://api.poketcgproject.com/api/authentication/login/ \
  -H "Content-Type: application/json" \
  -d '{"credential": "<google-id-token>"}'
```

_Note: A Google ID token is required to test this manually until frontend is developed (I use `https://developers.google.com/oauthplayground/`)._

### Refresh an access token

```bash
curl -X POST https://api.poketcgproject.com/api/authentication/token/refresh/ \
  --cookie "refresh_token=<cookie-value>"
```

### Favorite / unfavorite a card

```bash
# Add a favorite
curl -X POST https://api.poketcgproject.com/api/cards/favorites/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"card_id": "<tcgdex-card-id>"}'

# List favorites
curl https://api.poketcgproject.com/api/cards/favorites/ \
  -H "Authorization: Bearer <access_token>"

# Remove a favorite
curl -X DELETE https://api.poketcgproject.com/api/cards/favorites/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"card_id": "<tcgdex-card-id>"}'
```

---

## Testing

The authentication app has 20+ unit and integration tests, covering registration, login, token refresh, and refresh token rotation (including a TDD-driven approach for the rotation/blacklisting logic). Run the suite with:

```bash
python3 manage.py test
```

_(Card search/favorites test coverage is intentionally not yet written. When my brother finishes his CS50 course, I hope to be a software engineer by that time. I plan to give him a junior developer experience through this project and one of those tasks will be writing tests for the card app.)_

---

## Local Development

**Step 1:** Clone the repo

**Step 2:** Create a file for environment variables called `.env.dev` with the following variables:

\```
DJANGO_SETTINGS_MODULE='config.django.local'
DJANGO_DEBUG=True
SECRET_KEY=put_whatever_you_want_here

WEB_CLIENT_ID=<see_instructions_below_to_get_your_own_web_client_id>

REDIS_URL=redis://redis:6379/1

DATABASE_URL=postgres://<your_database_username_here>:<your_database_password_here>@db:5432/pokemon_django_react_app

ALLOWED_HOSTS=localhost,127.0.0.1

ENABLE_SWAGGER_DOCS=True
\```

**Step 3:** Open the codebase in a dev container

**Step 4:** Make migrations

\```bash
cd pokemon-project
python3 manage.py makemigrations
python3 manage.py migrate
\```

### Running the application

Inside the dev container, make sure your current directory is `pokemon-project/` and run:

\```bash
python3 manage.py runserver
\```

Then visit `http://127.0.0.1:8000/`.

### Testing the application

Inside the dev container, make sure your current directory is `pokemon-project/`.

Run all tests in the application:

\```bash
python3 manage.py test
\```

> **Note:** Running tests automatically sets the `CACHE` setting to use local memory instead of Redis.

You can scope which tests run like so:

\```bash
python3 manage.py test <app_name>.<test_folder_name>.<test_file_name>.<test_class_name>.<test_method_name>
\```

**Example:**

\```bash
python3 manage.py test authentication.tests.test_unit
\```

This runs all tests inside the `authentication/tests/test_unit.py` file.

### Setting up Google OAuth for local testing

Registering and logging in requires a Google ID token. To try this locally, you'll need your own Google Cloud OAuth Client ID.

**Step 1: Create a Google Cloud project**

Go to [console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate) (or pick an existing project from the project selector if you've already made one).

**Step 2: Configure the OAuth consent screen**

Go to **APIs & Services → OAuth consent screen**. Click **Get Started**, then:

1. **App Information:** any app name, and your email as support contact
2. **Audience:** choose **External** (this setting cannot be changed later and Internal only allows Workspace-org accounts)
3. **Contact Information:** your email
4. **Accept** and **Create**

**Step 3: Add yourself as a test user**

Go to the **Audience** tab and make sure your own Google account is listed under **Test Users**. If not, click **Add Users** and enter your Gmail account.

**Step 4: Create the Web Client ID**

Go to **Clients** tab → **Create Client**:

1. **Application type:** Web application
2. **Name:** anything you want, for example, `pokemon-tcg-dev`
3. **Authorized JavaScript origins:** `http://localhost:8000`
4. **Authorized redirect URIs:** `https://developers.google.com/oauthplayground`

Click **Create** and save the client JSON file somewhere secure.

**Retrieving an ID token for your test account**

1. Go to [developers.google.com/oauthplayground](https://developers.google.com/oauthplayground/)
2. Click the gear icon to open **OAuth 2.0 configuration**:
   - Check the box for **Use your own OAuth credentials**
   - Enter your Client ID and Client Secret
3. Under **Select & authorize APIs**, select **Google OAuth2 API v2** and check the following:
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `openid`
4. Click **Authorize APIs** and select the Google account you added as your test user
5. Click **Exchange Authorization Code for Tokens**
6. Copy the `id_token` string from the response and use it (without quotes) as the `credential` value in the login/register requests

---

## Status / roadmap

- [ ] Test coverage for the cards search and favorites API
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] React frontend
- [ ] PKCE flow (deferred until the frontend exists)
