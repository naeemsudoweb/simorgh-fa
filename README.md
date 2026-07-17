# Simorgh FC — Youth Football Academy Website Template

A complete Flask website for a Arabic (RTL) youth football academy: public
pages (home, about, news, gallery, team rosters), a player registration
form with photo upload, and a password-protected admin panel to
review/approve/reject applicants and assign them to a squad.

Built with a custom "matchday scoreboard" visual theme — dark pitch
tones, floodlight-amber accents, and a condensed display typeface.

---

## Features

- Public pages: Home, About, News, Gallery, Team roster pages
- Player registration form with automatic square photo cropping
- Age-based automatic squad suggestion (editable boundaries)
- Password-protected admin panel: approve / reject / delete applicants,
  reassign squads, grouped views by team
- Fully responsive, mobile menu included
- No JavaScript framework or build step required — plain HTML/CSS/JS
  and server-rendered Jinja templates

## Tech stack

- Python 3.10+
- Flask
- SQLite (zero setup — a local `team.db` file, created automatically)
- Pillow (image processing for uploaded photos)

---

## Quickest way to run this (Windows)

Double-click **start.bat**. The first time, it will install everything
and ask you to choose an admin password. Every time after that, it
just starts the site immediately. Once it's running, open
http://127.0.0.1:5000 in your browser.

The manual steps below are for other platforms or if you'd rather do
it yourself.

## 1. Installation

```bash
# 1. Unzip the project and open a terminal inside it
cd simorgh-fa

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 2. Configuration

The app refuses to start until it's configured — this is intentional,
so nobody accidentally deploys it with the sample password.

```bash
# 1. Copy the example environment file
cp .env.example .env

# 2. Generate your admin password hash
python generate_password_hash.py
# -> paste the printed ADMIN_PASSWORD_HASH=... line into .env

# 3. Generate a secret key for session cookies
python -c "import secrets; print(secrets.token_hex(32))"
# -> paste the result into .env as SECRET_KEY=...
```

Open `.env` and make sure it looks like this:

```
SECRET_KEY=<your random string>
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=<the hash generate_password_hash.py printed>
FLASK_DEBUG=false
```

## 3. Run it

```bash
python app.py
```

Visit `http://127.0.0.1:5000`. The database (`team.db`) and the
`static/uploads/` folder are created automatically on first run.

Admin panel: `http://127.0.0.1:5000/login`

---

## 4. Customizing the club

| What | Where |
|---|---|
| Club name, tagline, hero copy | `templates/base.html` (logo), `templates/index.html` (hero) |
| Colors, fonts | `static/style.css` — all tokens are CSS variables at the top of the file (`:root { ... }`) |
| Squads & age boundaries | `TEAM_MAP` and `get_team_by_age()` in `app.py` |
| Playing positions in the signup form | `templates/register.html` (the `<select name="position">` options) |
| Address / phone in the footer | `templates/footer.html` |
| Background photo | `static/bg.jpg` — see licensing note below |

---

## 5. Before you publish this as a product (read this)

If you're reselling or repackaging this template:

- **Change the default admin credentials** before showing a live demo,
  and never commit your real `.env` file anywhere public.
- **Turn off debug mode** in production (`FLASK_DEBUG=false` in `.env`,
  or simply leave it unset).
- Update `LICENSE.txt` with your own name/store and support terms.
- The background image (`static/bg.jpg`) is original artwork made for
  this template — swap it for your own any time with no licensing
  concerns either way.

## 6. Deploying

This is a standard Flask app — it runs on any host that supports
Python (PythonAnywhere, Render, Railway, a VPS with gunicorn + nginx,
etc.). For production, run it behind a real WSGI server instead of
`python app.py`, for example:

```bash
pip install gunicorn
gunicorn app:app
```

Make sure `.env` (with production values) is present on the server,
and that `static/uploads/` is writable.

---

## License

See `LICENSE.txt`.
