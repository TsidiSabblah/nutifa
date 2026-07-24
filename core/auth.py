import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Blueprint, render_template_string, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from database.schema import get_db

auth_bp = Blueprint('auth', __name__)

# ── User class for Flask-Login ────────────────────────────────────────────────
class User(UserMixin):
    def __init__(self, id, email, username, role, full_name):
        self.id = id
        self.email = email
        self.username = username
        self.role = role
        self.full_name = full_name

def load_user_by_id(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return User(row['id'], row['email'], row['username'], row['role'], row['full_name'])
    return None

# ── Styles (shared across all auth pages) ─────────────────────────────────────
AUTH_STYLE = """
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
    background: #0a0a0a;
    font-family: 'Segoe UI', sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}
.card {
    background: #141414;
    border: 1px solid #222;
    border-radius: 16px;
    padding: 40px;
    width: 100%;
    max-width: 420px;
}
.logo {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 900;
    color: #e8c547;
    letter-spacing: 4px;
    margin-bottom: 4px;
}
.logo span { color: #e8c547; }
.tagline {
    text-align: center;
    color: #555;
    font-size: 0.8rem;
    margin-bottom: 32px;
}
h2 {
    color: #fff;
    font-size: 1.3rem;
    margin-bottom: 24px;
    text-align: center;
}
.form-group { margin-bottom: 16px; }
label {
    display: block;
    color: #aaa;
    font-size: 0.85rem;
    margin-bottom: 6px;
}
input, select {
    width: 100%;
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 12px 14px;
    color: #fff;
    font-size: 0.95rem;
    outline: none;
    transition: border 0.2s;
}
input:focus, select:focus { border-color: #e8c547; }
.btn {
    width: 100%;
    background: #e8c547;
    color: #0a0a0a;
    border: none;
    border-radius: 8px;
    padding: 13px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    margin-top: 8px;
    transition: background 0.2s;
}
.btn:hover { background: #f0d060; }
.links {
    text-align: center;
    margin-top: 20px;
    color: #555;
    font-size: 0.85rem;
}
.links a { color: #e8c547; text-decoration: none; }
.links a:hover { text-decoration: underline; }
.flash {
    background: #2a1a1a;
    border: 1px solid #e8394730;
    color: #e84747;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 16px;
    font-size: 0.85rem;
}
.flash.success {
    background: #1a2a1a;
    border-color: #47e86030;
    color: #47e860;
}
.divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 20px 0;
}
.divider hr { flex:1; border-color: #222; }
.divider span { color: #444; font-size: 0.8rem; }
.role-selector {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
}
.role-btn {
    background: #1e1e1e;
    border: 2px solid #2a2a2a;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    color: #aaa;
}
.role-btn:hover, .role-btn.active {
    border-color: #e8c547;
    color: #e8c547;
    background: #1e1c0a;
}
.role-btn .icon { font-size: 1.8rem; display: block; margin-bottom: 4px; }
.role-btn .label { font-size: 0.8rem; font-weight: 600; }
</style>
"""

# ── Signup ─────────────────────────────────────────────────────────────────────
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""
    success = ""
    role = request.args.get("role", "fan")

    if request.method == "POST":
        role       = request.form.get("role") or "fan"
        email      = (request.form.get("email") or "").strip().lower()
        username   = (request.form.get("username") or "").strip()
        full_name  = (request.form.get("full_name") or "").strip()
        password   = request.form.get("password") or ""
        confirm    = request.form.get("confirm") or ""
        phone      = (request.form.get("phone") or "").strip()
        stage_name = (request.form.get("stage_name") or "").strip()

        print("FORM DATA:", dict(request.form))
        if not email or not username or not full_name or not password:
            error = "Please fill in all required fields."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            conn = get_db()
            try:
                conn.execute("""
                    INSERT INTO users (email, username, password_hash, role, full_name, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (email, username, generate_password_hash(password), role, full_name, phone))
                conn.commit()

                # If artist, create artist profile
                if role == "artist":
                    user = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
                    conn.execute("""
                        INSERT INTO artist_profiles (user_id, stage_name)
                        VALUES (?, ?)
                    """, (user['id'], stage_name or full_name))
                    conn.commit()

                return redirect('/login?success=1')
            except Exception as e:
                if "UNIQUE" in str(e):
                    error = "Email or username already taken."
                else:
                    error = f"Error: {e}"
            finally:
                conn.close()

    return render_template_string(AUTH_STYLE + """
    <div class="card">
        <div class="logo">HAJILALA<span>.</span></div>
        <div class="tagline">🎵 Peace & Harmony — Ghana's Music Marketplace</div>
        <h2>Create Account</h2>

        {% if error %}<div class="flash">{{ error }}</div>{% endif %}
        {% if success %}<div class="flash success">{{ success }}</div>{% endif %}

        <form method="POST">
            <p style="color:#aaa;font-size:0.85rem;margin-bottom:10px;">I am joining as:</p>
            <div class="role-selector">
                <label class="role-btn {% if role=='fan' %}active{% endif %}"
                       onclick="setRole('fan')">
                    <span class="icon">🎧</span>
                    <span class="label">Music Fan</span>
                </label>
                <label class="role-btn {% if role=='artist' %}active{% endif %}"
                       onclick="setRole('artist')">
                    <span class="icon">🎤</span>
                    <span class="label">Artist / Band</span>
                </label>
            </div>
            <input type="hidden" name="role" id="roleInput" value="{{ role }}">

            <div class="form-group">
                <label>Full Name *</label>
                <input type="text" name="full_name" placeholder="Your full name" required>
            </div>
            <div class="form-group" id="stageNameGroup"
                 style="display:{% if role=='artist' %}block{% else %}none{% endif %}">
                <label>Stage Name</label>
                <input type="text" name="stage_name" placeholder="Your artist/band name">
            </div>
            <div class="form-group">
                <label>Email *</label>
                <input type="email" name="email" placeholder="you@email.com" required>
            </div>
            <div class="form-group">
                <label>Username *</label>
                <input type="text" name="username" placeholder="@username" required>
            </div>
            <div class="form-group">
                <label>Phone (for MoMo payments)</label>
                <input type="tel" name="phone" placeholder="024 XXX XXXX">
            </div>
            <div class="form-group">
                <label>Password *</label>
                <input type="password" name="password" placeholder="Min. 6 characters" required>
            </div>
            <div class="form-group">
                <label>Confirm Password *</label>
                <input type="password" name="confirm" placeholder="Repeat password" required>
            </div>
            <button type="submit" class="btn">Create Account</button>
        </form>

        <div class="links">
            Already have an account? <a href="/login">Log in</a>
        </div>
    </div>

    <script>
    function setRole(r) {
        document.getElementById('roleInput').value = r;
        document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
        event.currentTarget.classList.add('active');
        document.getElementById('stageNameGroup').style.display = r === 'artist' ? 'block' : 'none';
    }
    </script>
    """, error=error, success=success, role=role)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""
    success = ""
    role = request.args.get("role", "fan")

    if request.method == "POST":
        role       = request.form.get("role", "fan")
        email      = request.form.get("email", "").strip().lower()
        username   = request.form.get("username", "").strip()
        full_name  = request.form.get("full_name", "").strip()
        password   = request.form.get("password", "")
        confirm    = request.form.get("confirm", "")
        phone      = request.form.get("phone", "").strip()
        stage_name = request.form.get("stage_name", "").strip()
        agree_terms = request.form.get("agree_terms")  # Add this line

        if not all([email, username, full_name, password]):
            error = "Please fill in all required fields."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif role == "artist" and not agree_terms:  # Add this block
            error = "You must agree to the Terms of Reference for Artists to register as an artist."
        else:
            conn = get_db()
            try:
                conn.execute("""
                    INSERT INTO users (email, username, password_hash, role, full_name, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (email, username, generate_password_hash(password), role, full_name, phone))
                conn.commit()

                # If artist, create artist profile
                if role == "artist":
                    user = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
                    conn.execute("""
                        INSERT INTO artist_profiles (user_id, stage_name)
                        VALUES (?, ?)
                    """, (user['id'], stage_name or full_name))
                    conn.commit()

                success = "Account created! You can now log in."
            except Exception as e:
                if "UNIQUE" in str(e):
                    error = "Email or username already taken."
                else:
                    error = f"Error: {e}"
            finally:
                conn.close()

    return render_template_string(AUTH_STYLE + """
    <!-- rest of your template -->
    """
# ── Login ──────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    success = "Account created successfully! Please log in." if request.args.get('success') else ""
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if not row or not check_password_hash(row['password_hash'], password):
            error = "Invalid email or password."
        elif not row['is_active']:
            error = "Your account has been suspended."
        else:
            user = User(row['id'], row['email'], row['username'], row['role'], row['full_name'])
            login_user(user)
            if row['role'] == 'admin':
                return redirect('/admin')
            elif row['role'] == 'artist':
                return redirect('/artist/dashboard')
            else:
                return redirect('/')

    return render_template_string(AUTH_STYLE + """
    <div class="card">
        <div class="logo">HAJILALA<span>.</span></div>
        <div class="tagline">🎵 Peace & Harmony — Ghana's Music Marketplace</div>
        <h2>Welcome Back</h2>

        {% if error %}<div class="flash">{{ error }}</div>{% endif %}

        <form method="POST">
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" placeholder="you@email.com" required autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Your password" required>
            </div>
            <button type="submit" class="btn">Log In</button>
        </form>

        <div class="divider"><hr><span>or</span><hr></div>

        <div class="links">
            New here? <a href="/signup">Create account</a><br><br>
            <a href="/signup?role=artist">Join as an Artist 🎤</a>
        </div>
    </div>
    """, error=error)


# ── Logout ─────────────────────────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')