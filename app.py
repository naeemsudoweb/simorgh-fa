# ================================================================
# FLOODLIGHT FC — Youth Football Academy
# Flask backend
# ================================================================
import os
import sqlite3
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image

load_dotenv()  # reads variables from a local .env file, if present

app = Flask(__name__)

# ----------------------------------------------------------------
# Configuration — everything secret/sensitive is read from the
# environment (see .env.example) instead of being hard-coded here.
# ----------------------------------------------------------------
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError(
        "SECRET_KEY is not set. Copy .env.example to .env and fill it in "
        "(see README.md > Configuration)."
    )

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")
if not ADMIN_PASSWORD_HASH:
    raise RuntimeError(
        "ADMIN_PASSWORD_HASH is not set. Run generate_password_hash.py to "
        "create one (see README.md > Configuration)."
    )

DEBUG_MODE = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

# File-upload safety limits
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ================================================================
# Squads and age brackets
# Note: adjust these boundaries as needed. Current mapping:
#   up to 14 years   -> Colts (U14)
#   15 - 17 years    -> Cadets (U17)
#   18 - 19 years    -> Youth (U19)
#   20+ years        -> First Team
# ================================================================
TEAM_MAP = {
    "under-14": "تیم نونهالان (زیر ۱۴ سال)",
    "under-17": "تیم نوجوانان (زیر ۱۷ سال)",
    "youth": "تیم جوانان (زیر ۱۹ سال)",
    "seniors": "تیم بزرگسالان",
}


def get_team_by_age(age):
    """Returns the appropriate squad slug based on the given age."""
    try:
        age = int(age)
    except (TypeError, ValueError):
        return "under-14"

    if age <= 14:
        return "under-14"
    elif age <= 17:
        return "under-17"
    elif age <= 19:
        return "youth"
    else:
        return "seniors"


def init_db():
    conn = sqlite3.connect("team.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS players (
        id        INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name  TEXT,
        age        INTEGER,
        position   TEXT,
        phone      TEXT,
        address    TEXT,
        photo      TEXT,
        status     TEXT DEFAULT 'pending'
    )""")

    # Add these columns if an older database doesn't have them yet,
    # so existing installs keep working without wiping the database.
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(players)").fetchall()]
    if "suggested_team" not in existing_cols:
        c.execute("ALTER TABLE players ADD COLUMN suggested_team TEXT")
    if "team" not in existing_cols:
        c.execute("ALTER TABLE players ADD COLUMN team TEXT")

    conn.commit()
    conn.close()


# Run this on import (not just when this file is executed directly) —
# production hosts (PythonAnywhere, gunicorn, etc.) import this module
# via WSGI and never hit the `if __name__ == "__main__"` block below,
# so the database needs to be created here to work in both setups.
init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        age = request.form["age"]
        position = request.form["position"]
        phone = request.form["phone"]
        address = request.form["address"]
        photo = request.files.get("profile_picture")

        # Automatically compute the suggested squad based on age
        suggested_team = get_team_by_age(age)

        photo_filename = ""
        if photo and photo.filename != "":
            if not allowed_file(photo.filename):
                flash("فقط فایل‌های تصویری (png, jpg, jpeg, gif, webp) مجاز هستند.")
                return redirect("/register")

            # Generate a random, safe filename — never trust the
            # filename the browser sends us.
            safe_name = secure_filename(photo.filename)
            extension = safe_name.rsplit(".", 1)[1].lower()
            photo_filename = f"{uuid.uuid4().hex}.{extension}"

            upload_folder = os.path.join(app.root_path, "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            final_photo_path = os.path.join(upload_folder, photo_filename)

            try:
                img = Image.open(photo)
                img.verify()  # reject files that aren't actually valid images
                photo.seek(0)
                img = Image.open(photo)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                width, height = img.size
                min_edge = min(width, height)
                left = (width - min_edge) / 2
                top = (height - min_edge) / 2
                right = (width + min_edge) / 2
                bottom = (height + min_edge) / 2
                img = img.crop((left, top, right, bottom))
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                # Always save as .jpg regardless of the original extension,
                # since the image is re-encoded here anyway.
                photo_filename = f"{uuid.uuid4().hex}.jpg"
                final_photo_path = os.path.join(upload_folder, photo_filename)
                img.save(final_photo_path, "JPEG", quality=95)
            except Exception:
                flash("این فایل یک تصویر معتبر به نظر نمی‌رسد. لطفاً دوباره امتحان کنید.")
                return redirect("/register")

        conn = sqlite3.connect("team.db")
        c = conn.cursor()
        c.execute(
            """INSERT INTO players
            (first_name, last_name, age, position, phone, address, photo, status, suggested_team, team)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, NULL)""",
            (first_name, last_name, age, position, phone, address, photo_filename, suggested_team),
        )
        conn.commit()
        conn.close()

        flash(
            f"بازیکن با موفقیت ثبت شد و به‌صورت پیشنهادی در "
            f"«{TEAM_MAP[suggested_team]}» قرار گرفت. تایید نهایی توسط مدیریت باشگاه انجام می‌شود.",
            "success",
        )
        return redirect("/register")

    return render_template("register.html")


# ================================================================
# Public pages
# ================================================================

@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/about')
def about():
    return render_template('about.html')


# ================================================================
# Individual squad page (matches the links in the nav dropdown)
# ================================================================
@app.route('/teams/<string:team_slug>')
def team_page(team_slug):
    if team_slug not in TEAM_MAP:
        flash("چنین تیمی وجود ندارد.")
        return redirect("/")

    conn = sqlite3.connect("team.db")
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE status = 'approved' AND team = ?", (team_slug,))
    players = c.fetchall()
    conn.close()

    return render_template(
        "team.html",
        players=players,
        team_name=TEAM_MAP[team_slug],
        team_slug=team_slug,
    )


# ================================================================
# Admin sign in
# ================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_username = request.form.get("username", "")
        entered_password = request.form.get("password", "")

        if entered_username == ADMIN_USERNAME and check_password_hash(
            ADMIN_PASSWORD_HASH, entered_password
        ):
            session.clear()
            session["logged_in"] = True
            return redirect("/admin")
        else:
            flash("نام کاربری یا رمز عبور اشتباه است.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("شما با موفقیت خارج شدید.", "success")
    return redirect("/login")


# ================================================================
# Admin panel
# ================================================================
@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        flash("لطفاً ابتدا وارد حساب خود شوید.")
        return redirect("/login")

    conn = sqlite3.connect("team.db")
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE status = 'pending'")
    pending_players = c.fetchall()
    c.execute("SELECT * FROM players WHERE status = 'approved' ORDER BY id DESC")
    approved_players = c.fetchall()
    c.execute("SELECT * FROM players WHERE status = 'rejected'")
    rejected_players = c.fetchall()
    conn.close()

    # Group approved players by squad so the admin panel shows each
    # team as its own block instead of one mixed list.
    approved_by_team = {slug: [] for slug in TEAM_MAP}
    for player in approved_players:
        team_slug = player[10]
        if team_slug in approved_by_team:
            approved_by_team[team_slug].append(player)

    return render_template(
        "admin.html",
        pending=pending_players,
        approved_by_team=approved_by_team,
        rejected=rejected_players,
        team_map=TEAM_MAP,
    )


# ================================================================
# Approve a player, along with selecting/changing their final squad
# ================================================================
@app.route("/action/approve/<int:player_id>", methods=["POST"])
def approve_player(player_id):
    if not session.get("logged_in"):
        return redirect("/login")

    selected_team = request.form.get("team")
    if selected_team not in TEAM_MAP:
        flash("تیم انتخاب‌شده معتبر نیست.")
        return redirect("/admin")

    conn = sqlite3.connect("team.db")
    c = conn.cursor()
    c.execute(
        "UPDATE players SET status = 'approved', team = ? WHERE id = ?",
        (selected_team, player_id),
    )
    conn.commit()
    conn.close()
    return redirect("/admin")


# ================================================================
# Reject / delete a player (no squad selection needed)
# ================================================================
@app.route("/action/<string:act>/<int:player_id>", methods=["POST"])
def player_action(act, player_id):
    if not session.get("logged_in"):
        return redirect("/login")

    if act not in ("reject", "delete"):
        return redirect("/admin")

    conn = sqlite3.connect("team.db")
    c = conn.cursor()
    if act == "reject":
        c.execute("UPDATE players SET status = 'rejected' WHERE id = ?", (player_id,))
    elif act == "delete":
        c.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()
    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)
