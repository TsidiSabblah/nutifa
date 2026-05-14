import os
import sys
import uuid
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
# At the top of the file, add request import if not already there
from flask import request  # Add this if missing


from flask import Blueprint, render_template_string, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.schema import get_db
from werkzeug.utils import secure_filename

artist_bp = Blueprint('artist', __name__, url_prefix='/artist')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
ALLOWED_AUDIO = {'mp3', 'wav', 'ogg', 'm4a'}
ALLOWED_IMAGE = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_VIDEO = {'mp4', 'mov', 'avi'}

def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def save_file(file, subfolder):
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_FOLDER, subfolder, filename)
    file.save(path)
    return filename

def generate_preview(audio_path, preview_path, duration=30):
    """Generate 30-second preview using FFmpeg"""
    try:
        cmd = [
            'ffmpeg', '-i', audio_path,
            '-t', str(duration),
            '-acodec', 'mp3',
            '-ab', '64k',
            '-y',
            preview_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"Preview generation failed: {e}")
        return False

DASH_STYLE = """
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0a0a0a; color:#fff; font-family:'Segoe UI',sans-serif; }
nav {
    background:#111; border-bottom:1px solid #1e1e1e;
    padding:0 32px; display:flex; align-items:center;
    justify-content:space-between; height:64px;
    position:sticky; top:0; z-index:100;
}
.logo { font-size:1.8rem; font-weight:900; color:#e8c547; letter-spacing:3px; text-decoration:none; }
.nav-links { display:flex; align-items:center; gap:24px; }
.nav-links a { color:#aaa; text-decoration:none; font-size:0.9rem; }
.nav-links a:hover { color:#e8c547; }
.btn { padding:8px 20px; border-radius:6px; font-size:0.85rem; font-weight:700;
       text-decoration:none; cursor:pointer; border:none; transition:all 0.2s; }
.btn-gold { background:#e8c547; color:#0a0a0a; }
.btn-outline { border:1.5px solid #e8c547; color:#e8c547; background:transparent; }
.btn-sm { padding:6px 14px; font-size:0.8rem; }
.btn:hover { opacity:0.85; }
.layout { display:grid; grid-template-columns:220px 1fr; min-height:calc(100vh - 64px); }
.sidebar {
    background:#111; border-right:1px solid #1a1a1a;
    padding:24px 0;
}
.sidebar-item {
    display:block; padding:12px 24px; color:#aaa;
    text-decoration:none; font-size:0.9rem; transition:all 0.2s;
    border-left:3px solid transparent;
}
.sidebar-item:hover, .sidebar-item.active {
    color:#e8c547; background:#1a1a1a;
    border-left-color:#e8c547;
}
.sidebar-item .icon { margin-right:10px; }
.main { padding:32px; }
.page-title { font-size:1.5rem; font-weight:700; margin-bottom:8px; }
.page-sub { color:#555; font-size:0.85rem; margin-bottom:32px; }
.stats-row { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:32px; }
.stat-card {
    background:#141414; border:1px solid #1e1e1e;
    border-radius:12px; padding:20px;
}
.stat-card .num { font-size:1.8rem; font-weight:900; color:#e8c547; }
.stat-card .label { color:#555; font-size:0.8rem; margin-top:4px; }
.section { background:#141414; border:1px solid #1e1e1e; border-radius:12px; padding:24px; margin-bottom:24px; }
.section-title { font-size:1rem; font-weight:700; margin-bottom:20px; color:#fff; }
.form-group { margin-bottom:16px; }
label { display:block; color:#aaa; font-size:0.85rem; margin-bottom:6px; }
input, select, textarea {
    width:100%; background:#1e1e1e; border:1px solid #2a2a2a;
    border-radius:8px; padding:11px 14px; color:#fff;
    font-size:0.9rem; outline:none; transition:border 0.2s;
    font-family:'Segoe UI',sans-serif;
}
input:focus, select:focus, textarea:focus { border-color:#e8c547; }
textarea { resize:vertical; min-height:80px; }
.form-row { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.flash { background:#2a1a1a; border:1px solid #e8394730; color:#e84747;
         border-radius:8px; padding:10px 14px; margin-bottom:16px; font-size:0.85rem; }
.flash.success { background:#1a2a1a; border-color:#47e86030; color:#47e860; }
table { width:100%; border-collapse:collapse; }
th { text-align:left; color:#555; font-size:0.8rem; padding:8px 12px;
     border-bottom:1px solid #1e1e1e; }
td { padding:12px; border-bottom:1px solid #141414; font-size:0.85rem; color:#ccc; }
tr:hover td { background:#1a1a1a; }
.badge {
    padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:700;
}
.badge-green { background:#1a2a1a; color:#47e860; }
.badge-yellow { background:#2a2a1a; color:#e8c547; }
.badge-red { background:#2a1a1a; color:#e84747; }
.empty { text-align:center; padding:40px; color:#444; }
.empty .icon { font-size:2.5rem; margin-bottom:8px; }
.tab-bar { display:flex; gap:4px; margin-bottom:24px; border-bottom:1px solid #1e1e1e; }
.tab {
    padding:10px 20px; color:#555; cursor:pointer;
    font-size:0.9rem; text-decoration:none;
    border-bottom:2px solid transparent; margin-bottom:-1px;
}
.tab:hover { color:#aaa; }
.tab.active { color:#e8c547; border-bottom-color:#e8c547; }
@media (max-width: 768px) {
    nav { padding: 0 16px; flex-wrap: wrap; height: auto; padding: 12px 16px; }
    .logo { font-size: 1.4rem; }
    .nav-links { gap: 12px; flex-wrap: wrap; margin-top: 8px; }
    .nav-links a, .btn { font-size: 0.75rem; padding: 6px 12px; }
    .hero { padding: 40px 20px; }
    .hero h1 { font-size: 2rem; }
    .hero p { font-size: 0.9rem; }
    .hero-btns { flex-direction: column; gap: 10px; }
    .stats-bar { flex-wrap: wrap; gap: 16px; padding: 16px; }
    .stat { flex: 1; min-width: 80px; }
    .categories { padding: 16px; gap: 8px; }
    .cat-btn { padding: 6px 12px; font-size: 0.7rem; }
    .section { padding: 24px 16px; }
    .grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; }
    .card-body { padding: 8px; }
    .card-title { font-size: 0.8rem; }
    .card-sub { font-size: 0.7rem; }
    .card-price { font-size: 0.75rem; }
    .section-title { font-size: 1.1rem; }
    .artist-grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 12px; }
    .sidebar { display: none; }
    .layout { grid-template-columns: 1fr; }
    .main { padding: 16px; }
    .stats-row { grid-template-columns: repeat(2, 1fr); gap: 12px; }
    .payment-card { padding: 24px; margin: 16px; }
    table { display: block; overflow-x: auto; }
    th, td { padding: 8px; font-size: 0.7rem; }
}
</style>
"""

def get_artist_profile(user_id):
    conn = get_db()
    profile = conn.execute(
        "SELECT * FROM artist_profiles WHERE user_id=?", (user_id,)
    ).fetchone()
    conn.close()
    return profile

# ── Dashboard Home ─────────────────────────────────────────────────────────────
@artist_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role not in ('artist', 'admin'):
        return redirect('/store')

    profile = get_artist_profile(current_user.id)
    if not profile:
        return redirect('/artist/setup')

    conn = get_db()
    track_count = conn.execute(
        "SELECT COUNT(*) FROM tracks WHERE artist_id=?", (profile['id'],)
    ).fetchone()[0]
    total_sales = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE artist_id=? AND status='paid'", (profile['id'],)
    ).fetchone()[0]
    total_earned = conn.execute(
        "SELECT COALESCE(SUM(artist_earnings),0) FROM orders WHERE artist_id=? AND status='paid'",
        (profile['id'],)
    ).fetchone()[0]
    
    # Calculate available balance for payout
    total_paid = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM payouts WHERE artist_id=? AND status='paid'",
        (profile['id'],)
    ).fetchone()[0]
    available_balance = total_earned - total_paid
    
    recent_orders = conn.execute("""
        SELECT o.*, t.title as track_title
        FROM orders o
        LEFT JOIN tracks t ON o.item_id = t.id AND o.item_type='track'
        WHERE o.artist_id=? ORDER BY o.created_at DESC LIMIT 5
    """, (profile['id'],)).fetchall()
    conn.close()

    return render_template_string(DASH_STYLE + """
    <!DOCTYPE html><html><head><title>Dashboard — Nutifa</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <a href="/store">Store</a>
            <a href="/artist/dashboard">Dashboard</a>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <a href="/artist/dashboard" class="sidebar-item active">
                <span class="icon">📊</span>Dashboard
            </a>
            <a href="/artist/upload" class="sidebar-item">
                <span class="icon">📤</span>Upload Music
            </a>
            <a href="/artist/tracks" class="sidebar-item">
                <span class="icon">🎵</span>My Tracks
            </a>
            <a href="/artist/request-payout" class="sidebar-item">
                <span class="icon">💰</span>Request Payout
            </a>
            <a href="/artist/merch" class="sidebar-item">
                <span class="icon">👕</span>Merchandise
            </a>
            <a href="/artist/sales" class="sidebar-item">
                <span class="icon">💰</span>Sales
            </a>
            <a href="/artist/profile" class="sidebar-item">
                <span class="icon">👤</span>My Profile
            </a>
            <a href="/store" class="sidebar-item">
                <span class="icon">🏪</span>Visit Store
            </a>
        </div>
        <div class="main">
            <div class="page-title">Welcome back, {{ profile['stage_name'] }} 🎤</div>
            <div class="page-sub">Here's how your music is performing</div>
            {% if not profile['is_verified'] %}
            <div class="flash">
                ⏳ Your artist account is pending approval from Nutifa admin.
                You can upload music but it won't be visible until approved.
            </div>
            {% endif %}
            <div class="stats-row">
                <div class="stat-card">
                    <div class="num">{{ track_count }}</div>
                    <div class="label">Total Tracks</div>
                </div>
                <div class="stat-card">
                    <div class="num">{{ total_sales }}</div>
                    <div class="label">Total Sales</div>
                </div>
                <div class="stat-card">
                    <div class="num">GHS {{ "%.2f"|format(total_earned) }}</div>
                    <div class="label">Total Earned</div>
                </div>
                <div class="stat-card">
                    <div class="num">GHS {{ "%.2f"|format(available_balance) }}</div>
                    <div class="label">Available Balance</div>
                </div>
            </div>
            <div class="section">
                <div class="section-title">Recent Sales</div>
                {% if recent_orders %}
                <table>
                    <thead>
                        <tr><th>Item</th><th>Amount</th><th>You Earn</th><th>Date</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                    {% for o in recent_orders %}
                        <tr>
                            <td>{{ o['track_title'] or o['item_type'] }}</td>
                            <td>GHS {{ "%.2f"|format(o['amount']) }}</td>
                            <td>GHS {{ "%.2f"|format(o['artist_earnings']) }}</td>
                            <td>{{ o['created_at'][:10] }}</td>
                            <td><span class="badge badge-green">{{ o['status'] }}</span></td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty">
                    <div class="icon">💰</div>
                    <p>No sales yet — upload your music to get started!</p>
                    <br>
                    <a href="/artist/upload" class="btn btn-gold">Upload Now</a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    </body></html>
    """, profile=profile, track_count=track_count,
         total_sales=total_sales, total_earned=total_earned,
         available_balance=available_balance, recent_orders=recent_orders)

# ── Upload Music ───────────────────────────────────────────────────────────────
@artist_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if current_user.role not in ('artist', 'admin'):
        return redirect('/store')

    profile = get_artist_profile(current_user.id)
    if not profile:
        return redirect('/artist/setup')

    error = ""
    success = ""

    if request.method == "POST":
        title      = (request.form.get("title") or "").strip()
        track_type = request.form.get("track_type") or "song"
        price      = request.form.get("price") or "0"
        currency   = request.form.get("currency") or "GHS"
        audio_file = request.files.get("audio_file")
        cover_file = request.files.get("cover_image")

        if not title:
            error = "Please enter a track title."
        elif not audio_file or not audio_file.filename:
            error = "Please upload an audio file."
        elif not allowed_file(audio_file.filename, ALLOWED_AUDIO):
            error = "Audio must be MP3, WAV, OGG or M4A."
        else:
            try:
                audio_filename = save_file(audio_file, "music")
                full_audio_path = os.path.join(UPLOAD_FOLDER, "music", audio_filename)

                # Generate 30-second preview
                preview_filename = f"preview_{audio_filename}"
                preview_path = os.path.join(UPLOAD_FOLDER, "music", preview_filename)
                generate_preview(full_audio_path, preview_path, duration=30)

                cover_filename = ""
                if cover_file and cover_file.filename and allowed_file(cover_file.filename, ALLOWED_IMAGE):
                    cover_filename = save_file(cover_file, "music")

                conn = get_db()
                conn.execute("""
                    INSERT INTO tracks
                    (artist_id, title, file_path, preview_path, cover_image, track_type, price, currency, is_published)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (profile['id'], title, audio_filename, preview_filename, cover_filename,
                      track_type, float(price), currency))
                conn.commit()
                conn.close()
                success = f"'{title}' uploaded successfully with preview!"
            except Exception as e:
                error = f"Upload failed: {e}"

    return render_template_string(DASH_STYLE + """
    <!DOCTYPE html><html><head><title>Upload — Nutifa</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <a href="/store">Store</a>
            <a href="/artist/dashboard">Dashboard</a>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <a href="/artist/dashboard" class="sidebar-item">
                <span class="icon">📊</span>Dashboard
            </a>
            <a href="/artist/upload" class="sidebar-item active">
                <span class="icon">📤</span>Upload Music
            </a>
            <a href="/artist/tracks" class="sidebar-item">
                <span class="icon">🎵</span>My Tracks
            </a>
            <a href="/artist/request-payout" class="sidebar-item">
                <span class="icon">💰</span>Request Payout
            </a>
            <a href="/artist/merch" class="sidebar-item">
                <span class="icon">👕</span>Merchandise
            </a>
            <a href="/artist/sales" class="sidebar-item">
                <span class="icon">💰</span>Sales
            </a>
            <a href="/artist/profile" class="sidebar-item">
                <span class="icon">👤</span>My Profile
            </a>
        </div>
        <div class="main">
            <div class="page-title">Upload Music 📤</div>
            <div class="page-sub">Upload your tracks, beats and instrumentals</div>
            {% if error %}<div class="flash">{{ error }}</div>{% endif %}
            {% if success %}<div class="flash success">✅ {{ success }}</div>{% endif %}
            <div class="section">
                <div class="section-title">Track Details</div>
                <form method="POST" enctype="multipart/form-data">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Track Title *</label>
                            <input type="text" name="title" placeholder="e.g. My Song Title" required>
                        </div>
                        <div class="form-group">
                            <label>Type *</label>
                            <select name="track_type">
                                <option value="song">🎤 Song</option>
                                <option value="beat">🥁 Beat / Instrumental</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Price *</label>
                            <input type="number" name="price" placeholder="0.00" min="0" step="0.01" value="0">
                        </div>
                        <div class="form-group">
                            <label>Currency</label>
                            <select name="currency">
                                <option value="GHS">GHS — Ghana Cedis</option>
                                <option value="USD">USD — US Dollars</option>
                                <option value="GBP">GBP — British Pounds</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Audio File * (MP3, WAV, OGG, M4A)</label>
                        <input type="file" name="audio_file" accept=".mp3,.wav,.ogg,.m4a" required>
                    </div>
                    <div class="form-group">
                        <label>Cover Image (JPG, PNG — optional)</label>
                        <input type="file" name="cover_image" accept=".jpg,.jpeg,.png,.webp">
                    </div>
                    <button type="submit" class="btn btn-gold">📤 Upload Track</button>
                </form>
            </div>
        </div>
    </div>
    </body></html>
    """, error=error, success=success, profile=profile)
@artist_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if current_user.role not in ('artist', 'admin'):
        return redirect('/store')

    profile = get_artist_profile(current_user.id)
    if not profile:
        return redirect('/artist/setup')

    error = ""
    success = ""

    if request.method == "POST":
        title      = (request.form.get("title") or "").strip()
        track_type = request.form.get("track_type") or "song"
        price      = request.form.get("price") or "0"
        currency   = request.form.get("currency") or "GHS"
        audio_file = request.files.get("audio_file")
        cover_file = request.files.get("cover_image")
        copyright_certify = request.form.get("copyright_certify")  # Add this line

        if not title:
            error = "Please enter a track title."
        elif not audio_file or not audio_file.filename:
            error = "Please upload an audio file."
        elif not allowed_file(audio_file.filename, ALLOWED_AUDIO):
            error = "Audio must be MP3, WAV, OGG or M4A."
        elif not copyright_certify:  # Add this block
            error = "You must certify that you own the rights to this content before uploading."
        else:
            try:
                audio_filename = save_file(audio_file, "music")
                full_audio_path = os.path.join(UPLOAD_FOLDER, "music", audio_filename)

                # Generate 30-second preview
                preview_filename = f"preview_{audio_filename}"
                preview_path = os.path.join(UPLOAD_FOLDER, "music", preview_filename)
                generate_preview(full_audio_path, preview_path, duration=30)

                cover_filename = ""
                if cover_file and cover_file.filename and allowed_file(cover_file.filename, ALLOWED_IMAGE):
                    cover_filename = save_file(cover_file, "music")

                conn = get_db()
                
                # Log the copyright certification for audit purposes (optional)
                # You can add a copyright_certified_at column to tracks table
                
                conn.execute("""
                    INSERT INTO tracks
                    (artist_id, title, file_path, preview_path, cover_image, track_type, price, currency, is_published)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (profile['id'], title, audio_filename, preview_filename, cover_filename,
                      track_type, float(price), currency))
                conn.commit()
                conn.close()
                success = f"'{title}' uploaded successfully with preview!"
            except Exception as e:
                error = f"Upload failed: {e}"

    return render_template_string(DASH_STYLE + """
    <!-- rest of your template -->
    """
# In the upload route, when inserting the track, update to include the new columns
conn.execute("""
    INSERT INTO tracks
    (artist_id, title, file_path, preview_path, cover_image, track_type, price, currency, is_published, copyright_certified_at, copyright_certified_ip)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now'), ?)
""", (profile['id'], title, audio_filename, preview_filename, cover_filename,
      track_type, float(price), currency, request.remote_addr))

# ── My Tracks ─────────────────────────────────────────────────────────────────
@artist_bp.route("/tracks")
@login_required
def tracks():
    if current_user.role not in ('artist', 'admin'):
        return redirect('/store')
    profile = get_artist_profile(current_user.id)
    conn = get_db()
    my_tracks = conn.execute(
        "SELECT * FROM tracks WHERE artist_id=? ORDER BY created_at DESC",
        (profile['id'],)
    ).fetchall()
    conn.close()

    return render_template_string(DASH_STYLE + """
    <!DOCTYPE html><html><head><title>My Tracks — Nutifa</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <a href="/store">Store</a>
            <a href="/artist/dashboard">Dashboard</a>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <a href="/artist/dashboard" class="sidebar-item">
                <span class="icon">📊</span>Dashboard
            </a>
            <a href="/artist/upload" class="sidebar-item">
                <span class="icon">📤</span>Upload Music
            </a>
            <a href="/artist/tracks" class="sidebar-item active">
                <span class="icon">🎵</span>My Tracks
            </a>
            <a href="/artist/request-payout" class="sidebar-item">
                <span class="icon">💰</span>Request Payout
            </a>
            <a href="/artist/merch" class="sidebar-item">
                <span class="icon">👕</span>Merchandise
            </a>
            <a href="/artist/sales" class="sidebar-item">
                <span class="icon">💰</span>Sales
            </a>
            <a href="/artist/profile" class="sidebar-item">
                <span class="icon">👤</span>My Profile
            </a>
        </div>
        <div class="main">
            <div class="page-title">My Tracks 🎵</div>
            <div class="page-sub">Manage your uploaded music</div>
            <div style="margin-bottom:20px">
                <a href="/artist/upload" class="btn btn-gold">+ Upload New Track</a>
            </div>
            <div class="section">
                {% if my_tracks %}
                <table>
                    <thead>
                        <tr><th>Title</th><th>Type</th><th>Price</th><th>Downloads</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                    {% for t in my_tracks %}
                        <tr>
                            <td>{{ t['title'] }}</td>
                            <td>{{ t['track_type'] }}</td>
                            <td>{% if t['price'] == 0 %}<span style="color:#47e860">FREE</span>{% else %}{{ t['currency'] }} {{ "%.2f"|format(t['price']) }}{% endif %}</td>
                            <td>{{ t['downloads'] }}</td>
                            <td>{% if t['is_published'] %}<span class="badge badge-green">Published</span>{% else %}<span class="badge badge-yellow">Draft</span>{% endif %}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty">
                    <div class="icon">🎵</div>
                    <p>No tracks yet — upload your first track!</p>
                    <br>
                    <a href="/artist/upload" class="btn btn-gold">Upload Now</a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    </body></html>
    """, my_tracks=my_tracks, profile=profile)

# ── Request Payout ────────────────────────────────────────────────────────────
@artist_bp.route("/request-payout", methods=["GET", "POST"])
@login_required
def request_payout():
    if current_user.role not in ('artist', 'admin'):
        return redirect('/store')
    
    profile = get_artist_profile(current_user.id)
    if not profile:
        return redirect('/artist/setup')
    
    conn = get_db()
    
    # Calculate available balance
    total_earned = conn.execute(
        "SELECT COALESCE(SUM(artist_earnings),0) FROM orders WHERE artist_id=? AND status='paid'",
        (profile['id'],)
    ).fetchone()[0]
    
    total_paid = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM payouts WHERE artist_id=? AND status='paid'",
        (profile['id'],)
    ).fetchone()[0]
    
    balance = total_earned - total_paid
    
    # Get payout history
    payout_history = conn.execute("""
        SELECT * FROM payouts WHERE artist_id=? ORDER BY created_at DESC
    """, (profile['id'],)).fetchall()
    
    error = ""
    success = ""
    
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))
            method = request.form.get("method", "mobile_money")
            phone = request.form.get("phone", "")
            
            if amount <= 0:
                error = "Please enter a valid amount"
            elif amount < 10:
                error = "Minimum withdrawal amount is GHS 10.00"
            elif balance <= 0:
                error = "You have no available balance. Make some sales first!"
            elif amount > balance:
                error = f"Request amount exceeds your balance of GHS {balance:.2f}"
            elif not phone and method == "mobile_money":
                error = "Please enter your mobile money number"
            else:
                conn.execute("""
                    INSERT INTO payouts (artist_id, amount, currency, method, reference, status, payout_details)
                    VALUES (?, ?, 'GHS', ?, ?, 'pending', ?)
                """, (profile['id'], amount, method, f"PAY-{uuid.uuid4().hex[:8]}", phone))
                conn.commit()
                success = f"Payout request of GHS {amount:.2f} submitted for approval!"
        except Exception as e:
            error = f"Error: {str(e)}"
    
    conn.close()
    
    # The render_template_string call must be properly closed with parentheses
    return render_template_string(DASH_STYLE + """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Request Payout — Nutifa</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <nav>
            <a href="/" class="logo">NUTIFA.</a>
            <div class="nav-links">
                <a href="/store">Store</a>
                <a href="/artist/dashboard">Dashboard</a>
                <a href="/logout" class="btn btn-outline">Log Out</a>
            </div>
        </nav>
        <div class="layout">
            <div class="sidebar">
                <a href="/artist/dashboard" class="sidebar-item">
                    <span class="icon">📊</span>Dashboard
                </a>
                <a href="/artist/upload" class="sidebar-item">
                    <span class="icon">📤</span>Upload Music
                </a>
                <a href="/artist/tracks" class="sidebar-item">
                    <span class="icon">🎵</span>My Tracks
                </a>
                <a href="/artist/request-payout" class="sidebar-item active">
                    <span class="icon">💰</span>Request Payout
                </a>
                <a href="/artist/merch" class="sidebar-item">
                    <span class="icon">👕</span>Merchandise
                </a>
                <a href="/artist/sales" class="sidebar-item">
                    <span class="icon">💰</span>Sales
                </a>
                <a href="/artist/profile" class="sidebar-item">
                    <span class="icon">👤</span>My Profile
                </a>
                <a href="/store" class="sidebar-item">
                    <span class="icon">🏪</span>Visit Store
                </a>
            </div>
            <div class="main">
                <div class="page-title">Request Payout 💰</div>
                <div class="page-sub">Withdraw your earnings</div>
                
                <div class="stats-row">
                    <div class="stat-card">
                        <div class="num">GHS {{ "%.2f"|format(balance) }}</div>
                        <div class="label">Available Balance</div>
                    </div>
                </div>
                
                {% if error %}<div class="flash">{{ error }}</div>{% endif %}
                {% if success %}<div class="flash success">✅ {{ success }}</div>{% endif %}
                
                <div class="section">
                    <div class="section-title">Withdrawal Request</div>
                    <form method="POST">
                        <div class="form-group">
                            <label>Amount (GHS) *</label>
                            <input type="number" name="amount" min="10" {% if balance > 0 %}max="{{ balance }}"{% else %}max="0"{% endif %} step="1" required>
                            <small style="color:#555">Minimum withdrawal: GHS 10.00. {% if balance <= 0 %}You need sales before requesting payout.{% endif %}</small>
                        </div>
                        <div class="form-group">
                            <label>Payment Method *</label>
                            <select name="method">
                                <option value="mobile_money">📱 Mobile Money (MTN/Vodafone/AirtelTigo)</option>
                                <option value="bank">🏦 Bank Transfer</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Mobile Money Number / Bank Account</label>
                            <input type="text" name="phone" placeholder="e.g., 024XXXXXXX">
                        </div>
                        <button type="submit" class="btn btn-gold" {% if balance <= 0 %}disabled{% endif %}>Submit Request</button>
                    </form>
                </div>
                
                {% if payout_history %}
                <div class="section">
                    <div class="section-title">Payout History</div>
                    <table>
                        <thead>
                            <tr><th>Date</th><th>Amount</th><th>Method</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                        {% for p in payout_history %}
                            <tr>
                                <td>{{ p['created_at'][:10] if p['created_at'] else '—' }}</td>
                                <td>GHS {{ "%.2f"|format(p['amount']) }}</td>
                                <td>{{ p['method'] }}</td>
                                <td>
                                    <span class="badge 
                                        {% if p['status'] == 'paid' %}badge-green
                                        {% elif p['status'] == 'pending' %}badge-yellow
                                        {% else %}badge-red{% endif %}">
                                        {{ p['status'] }}
                                    </span>
                                </td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, profile=profile, balance=balance, payout_history=payout_history)

# ── Artist Setup (first time) ─────────────────────────────────────────────────
@artist_bp.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    error = ""
    if request.method == "POST":
        stage_name = (request.form.get("stage_name") or "").strip()
        genre      = (request.form.get("genre") or "").strip()
        if not stage_name:
            error = "Please enter your stage name."
        else:
            conn = get_db()
            conn.execute(
                "INSERT OR IGNORE INTO artist_profiles (user_id, stage_name, genre) VALUES (?,?,?)",
                (current_user.id, stage_name, genre)
            )
            conn.commit()
            conn.close()
            return redirect('/artist/dashboard')

    return render_template_string(DASH_STYLE + """
    <!DOCTYPE html><html><head><title>Artist Setup — Nutifa</title></head><body>
    <nav><a href="/" class="logo">NUTIFA.</a></nav>
    <div style="display:flex;align-items:center;justify-content:center;min-height:80vh">
        <div style="background:#141414;border:1px solid #1e1e1e;border-radius:16px;padding:40px;width:100%;max-width:420px">
            <h2 style="color:#e8c547;margin-bottom:8px">Complete Artist Profile 🎤</h2>
            <p style="color:#555;font-size:0.85rem;margin-bottom:24px">Tell us about yourself</p>
            {% if error %}<div class="flash">{{ error }}</div>{% endif %}
            <form method="POST">
                <div class="form-group">
                    <label>Stage Name *</label>
                    <input type="text" name="stage_name" placeholder="Your artist name" required>
                </div>
                <div class="form-group">
                    <label>Genre</label>
                    <select name="genre">
                        <option value="">Select genre...</option>
                        <option>Afrobeats</option>
                        <option>Highlife</option>
                        <option>Hiplife</option>
                        <option>Gospel</option>
                        <option>Hip Hop</option>
                        <option>R&B</option>
                        <option>Reggae</option>
                        <option>Dancehall</option>
                        <option>Afropop</option>
                        <option>Traditional</option>
                        <option>Other</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-gold" style="width:100%">Complete Setup →</button>
            </form>
        </div>
    </div>
    </body></html>
    """, error=error)