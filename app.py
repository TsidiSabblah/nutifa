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

# Ensure database directory exists on Render
if os.environ.get('RENDER'):
    import sqlite3
    conn = sqlite3.connect('/tmp/nutifa.db')
    conn.close()

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
                    color: #fff;
                    font-family: 'Segoe UI', sans-serif;
                }
                nav {
                    background: #111;
                    border-bottom: 1px solid #1e1e1e;
                    padding: 0 32px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    height: 64px;
                    position: sticky;
                    top: 0;
                    z-index: 100;
                }
                .logo {
                    font-size: 1.8rem;
                    font-weight: 900;
                    color: #e8c547;
                    letter-spacing: 3px;
                    text-decoration: none;
                }
                .nav-links { display: flex; align-items: center; gap: 24px; }
                .nav-links a {
                    color: #aaa;
                    text-decoration: none;
                    font-size: 0.9rem;
                    transition: color 0.2s;
                }
                .nav-links a:hover { color: #e8c547; }
                .btn {
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-size: 0.85rem;
                    font-weight: 700;
                    text-decoration: none;
                    cursor: pointer;
                    border: none;
                    transition: all 0.2s;
                    display: inline-block;
                }
                .btn-gold { background: #e8c547; color: #0a0a0a; }
                .btn-outline { border: 1.5px solid #e8c547; color: #e8c547; background: transparent; }
                .btn:hover { opacity: 0.85; }
                .hero {
                    background: linear-gradient(135deg, #111 0%, #1a1a0a 50%, #0a0a1a 100%);
                    padding: 80px 32px;
                    text-align: center;
                    border-bottom: 1px solid #1e1e1e;
                }
                .hero h1 {
                    font-size: 3.5rem;
                    font-weight: 900;
                    color: #e8c547;
                    letter-spacing: 2px;
                    margin-bottom: 12px;
                }
                .hero p {
                    color: #aaa;
                    font-size: 1.1rem;
                    margin-bottom: 32px;
                }
                .hero-btns { display: flex; gap: 16px; justify-content: center; }
            </style>
        </head>
        <body>
            <nav>
                <a href="/" class="logo">NUTIFA.</a>
                <div class="nav-links">
                    <a href="/store">Store</a>
                    <a href="/store?cat=beats">Beats</a>
                    <a href="/store?cat=videos">Videos</a>
                    <a href="/store?cat=merch">Merch</a>
                    {% if current_user.is_authenticated %}
                        {% if current_user.role == 'artist' %}
                            <a href="/artist/dashboard">Dashboard</a>
                        {% endif %}
                        {% if current_user.role == 'admin' %}
                            <a href="/admin">Admin</a>
                        {% endif %}
                        <a href="/logout" class="btn btn-outline">Log Out</a>
                    {% else %}
                        <a href="/login" class="btn btn-outline">Log In</a>
                        <a href="/signup" class="btn btn-gold">Join Free</a>
                    {% endif %}
                </div>
            </nav>

            <div class="hero">
                <h1>NUTIFA.</h1>
                <p>🎵 Peace & Harmony — Ghana's Music Marketplace</p>
                <div class="hero-btns">
                    <a href="/signup?role=artist" class="btn btn-gold">🎤 Sell Your Music</a>
                    <a href="/store" class="btn btn-outline">🎧 Browse Music</a>
                </div>
            </div>
        </body>
        </html>
        """, current_user=current_user)

    return app
# Secret route to make any user admin (remove after use)
@app.route("/make-admin/<email>")
def make_admin(email):
    from database.schema import get_db
    conn = get_db()
    conn.execute("UPDATE users SET role='admin' WHERE email=?", (email,))
    conn.commit()
    conn.close()
    return f"User {email} is now an admin! <a href='/login'>Login here</a>"

if __name__ == "__main__":
    init_db()
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print("=" * 40)
    print("  NUTIFA is running!")
    print(f"  Open: http://localhost:{port}")
    print("=" * 40)
    app.run(host='0.0.0.0', debug=False, port=port)