import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template_string, redirect, url_for
from flask_login import LoginManager, current_user
from dotenv import load_dotenv

load_dotenv()

from database.schema import init_db, get_db
from core.auth import auth_bp, load_user_by_id
from core.store import store_bp
from core.artist import artist_bp
from core.admin import admin_bp
from core.payment import payment_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "nutifa-dev-secret-2024")

    # ── Flask-Login setup ─────────────────────────────────────────────────
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return load_user_by_id(user_id)

    # ── Register blueprints ───────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(artist_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)

    # ── Home route ────────────────────────────────────────────────────────
    @app.route("/")
    def home():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nutifa Music</title>
            <style>
                * { margin:0; padding:0; box-sizing:border-box; }
                body {
                    background: #0a0a0a;
                    color: #e8c547;
                    font-family: 'Segoe UI', sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    flex-direction: column;
                    gap: 12px;
                }
                h1 { font-size: 5rem; letter-spacing: 6px; font-weight: 900; }
                .sub { color: #aaa; font-size: 1.1rem; }
                .links { margin-top: 32px; display: flex; gap: 16px; }
                .btn {
                    padding: 12px 28px;
                    border-radius: 8px;
                    font-size: 0.95rem;
                    font-weight: 700;
                    text-decoration: none;
                    transition: all 0.2s;
                }
                .btn-gold {
                    background: #e8c547;
                    color: #0a0a0a;
                }
                .btn-outline {
                    border: 2px solid #e8c547;
                    color: #e8c547;
                }
                .btn:hover { opacity: 0.85; }
                .user-info { color: #555; font-size: 0.85rem; margin-top: 16px; }
            </style>
        </head>
        <body>
            <h1>NUTIFA.</h1>
            <p class="sub">🎵 Peace & Harmony — Ghana's Music Marketplace</p>
            <div class="links">
                {% if current_user.is_authenticated %}
                    <span style="color:#e8c547;padding:12px">
                        Welcome, {{ current_user.full_name }}!
                    </span>
                    <a href="/logout" class="btn btn-outline">Log Out</a>
                {% else %}
                    <a href="/signup" class="btn btn-gold">Join Free</a>
                    <a href="/login" class="btn btn-outline">Log In</a>
                {% endif %}
            </div>
        </body>
        </html>
        """, current_user=current_user)

    return app

if __name__ == "__main__":
    init_db()
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print("=" * 40)
    print("  NUTIFA is running!")
    print(f"  Open: http://localhost:{port}")
    print("=" * 40)
    app.run(host='0.0.0.0', debug=False, port=port)