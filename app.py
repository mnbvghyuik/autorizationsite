"""
Логин только для Gmail — упрощённая версия в одном файле.

Как открыть:
  1) локально:  pip install -r requirements.txt   и   python3 app.py
  2) через интернет: залить этот файл на GitHub и запустить на Replit/Render
     (см. README.md рядом с этим файлом)

Что тут происходит (коротко):
  GET  /login   -> отдаём HTML-форму
  POST /login   -> проверяем email и пароль, которые прислал браузер
  GET  /success -> страница "вы успешно авторизовались" (только если вошли)
"""

import os
import re
from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# --- демо-пользователь (в реальном проекте это должна быть база данных) ---
DEMO_EMAIL = "demo.user" + "@" + "gmail.com"       # логин
DEMO_PASSWORD_HASH = generate_password_hash("password123")  # пароль: password123

GMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", re.IGNORECASE)

LOGO_SVG = """
<svg class="logo" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">
  <circle cx="48" cy="48" r="46" fill="#4285F4"/>
  <path d="M28 34 L48 52 L68 34" stroke="white" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="26" y="32" width="44" height="32" rx="4" stroke="white" stroke-width="4" fill="none"/>
</svg>
"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96'%3E"
           "%3Ccircle cx='48' cy='48' r='46' fill='%234285F4'/%3E"
           "%3Cpath d='M28 34 L48 52 L68 34' stroke='white' stroke-width='6' fill='none' "
           "stroke-linecap='round' stroke-linejoin='round'/%3E"
           "%3Crect x='26' y='32' width='44' height='32' rx='4' stroke='white' stroke-width='4' fill='none'/%3E%3C/svg%3E")

BASE_CSS = """
* { box-sizing: border-box; }
body { margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center;
       background:#f4f6f9; font-family:-apple-system,"Segoe UI",Roboto,Arial,sans-serif; }
.card { background:#fff; padding:40px 36px; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,.08);
        width:100%; max-width:360px; text-align:center; }
.logo { display:block; margin:0 auto 20px auto; width:72px; height:72px; }
h1 { font-size:20px; margin:0 0 24px 0; color:#1a1a1a; }
form { text-align:left; }
label { display:block; font-size:13px; color:#555; margin-bottom:6px; }
input { width:100%; padding:10px 12px; margin-bottom:16px; border:1px solid #d7dbe0; border-radius:8px; font-size:14px; }
input:focus { outline:none; border-color:#4285f4; }
button { width:100%; padding:11px; background:#4285f4; color:#fff; border:none; border-radius:8px; font-size:15px; cursor:pointer; }
button:hover { background:#3367d6; }
.error { background:#fdecea; color:#c5221f; padding:10px 12px; border-radius:8px; font-size:13px; margin-bottom:16px; }
.success-text { font-size:16px; color:#1a1a1a; margin-top:4px; }
.email-badge { color:#4285f4; font-weight:600; }
.logout-btn { margin-top:24px; background:transparent; color:#555; border:1px solid #d7dbe0; }
.logout-btn:hover { background:#f4f6f9; }
"""

LOGIN_PAGE = """
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Вход</title>
<link rel="icon" href="{{ favicon }}"><style>{{ css | safe }}</style></head><body>
<div class="card">
  {{ logo | safe }}
  <h1>Вход в аккаунт</h1>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="POST" action="{{ url_for('login') }}">
    <label for="email">Email (только @gmail.com)</label>
    <input type="email" id="email" name="email" placeholder="[email protected]" required>
    <label for="password">Пароль</label>
    <input type="password" id="password" name="password" required>
    <button type="submit">Войти</button>
  </form>
</div></body></html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Вы успешно авторизовались</title>
<link rel="icon" href="{{ favicon }}"><style>{{ css | safe }}</style></head><body>
<div class="card">
  {{ logo | safe }}
  <p class="success-text">Вы успешно авторизовались</p>
  <p class="email-badge">{{ user }}</p>
  <form method="POST" action="{{ url_for('logout') }}">
    <button type="submit" class="logout-btn">Выйти</button>
  </form>
</div></body></html>
"""


@app.route("/")
def index():
    return redirect(url_for("success") if session.get("user") else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # GET  -> просто показать форму
    # POST -> браузер прислал email+пароль, проверяем их
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            error = "Заполните оба поля."
        elif not GMAIL_RE.match(email):
            error = "Вход разрешён только с почтой формата [email protected]."
        elif email != DEMO_EMAIL or not check_password_hash(DEMO_PASSWORD_HASH, password):
            error = "Неверно введён email или пароль."
        else:
            session["user"] = email
            return redirect(url_for("success"), code=303)  # редирект после успешного POST

    return render_template_string(LOGIN_PAGE, error=error, logo=LOGO_SVG, favicon=FAVICON, css=BASE_CSS)


@app.route("/success")
def success():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template_string(SUCCESS_PAGE, user=user, logo=LOGO_SVG, favicon=FAVICON, css=BASE_CSS)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    # host/port так, чтобы работало и локально, и на Render/Replit
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
