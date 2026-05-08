import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Blueprint, render_template_string, request, redirect
from flask_login import login_required, current_user
from database.schema import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_STYLE = """
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
       text-decoration:none; cursor:pointer; border:none; transition:all 0.2s; display:inline-block; }
.btn-gold { background:#e8c547; color:#0a0a0a; }
.btn-outline { border:1.5px solid #e8c547; color:#e8c547; background:transparent; }
.btn-red { background:#e84747; color:#fff; }
.btn-green { background:#47e860; color:#0a0a0a; }
.btn-sm { padding:5px 12px; font-size:0.78rem; }
.btn:hover { opacity:0.85; }
.layout { display:grid; grid-template-columns:220px 1fr; min-height:calc(100vh - 64px); }
.sidebar {
    background:#111; border-right:1px solid #1a1a1a; padding:24px 0;
}
.sidebar-section {
    color:#333; font-size:0.7rem; font-weight:700;
    padding:16px 24px 8px; letter-spacing:2px; text-transform:uppercase;
}
.sidebar-item {
    display:block; padding:11px 24px; color:#aaa;
    text-decoration:none; font-size:0.88rem; transition:all 0.2s;
    border-left:3px solid transparent;
}
.sidebar-item:hover, .sidebar-item.active {
    color:#e8c547; background:#1a1a1a; border-left-color:#e8c547;
}
.sidebar-item .icon { margin-right:10px; }
.main { padding:32px; }
.page-title { font-size:1.5rem; font-weight:700; margin-bottom:4px; }
.page-sub { color:#555; font-size:0.85rem; margin-bottom:28px; }
.stats-row { display:grid; grid-template-columns:repeat(5,1fr); gap:16px; margin-bottom:28px; }
.stat-card {
    background:#141414; border:1px solid #1e1e1e;
    border-radius:12px; padding:18px;
}
.stat-card .num { font-size:1.6rem; font-weight:900; color:#e8c547; }
.stat-card .label { color:#555; font-size:0.78rem; margin-top:4px; }
.section {
    background:#141414; border:1px solid #1e1e1e;
    border-radius:12px; padding:24px; margin-bottom:24px;
}
.section-header {
    display:flex; align-items:center; justify-content:space-between; margin-bottom:20px;
}
.section-title { font-size:1rem; font-weight:700; color:#fff; }
table { width:100%; border-collapse:collapse; }
th { text-align:left; color:#555; font-size:0.78rem; padding:8px 12px; border-bottom:1px solid #1e1e1e; }
td { padding:11px 12px; border-bottom:1px solid #141414; font-size:0.85rem; color:#ccc; }
tr:last-child td { border-bottom:none; }
tr:hover td { background:#1a1a1a; }
.badge { padding:3px 10px; border-radius:20px; font-size:0.73rem; font-weight:700; }
.badge-green { background:#1a2a1a; color:#47e860; }
.badge-yellow { background:#2a2a1a; color:#e8c547; }
.badge-red { background:#2a1a1a; color:#e84747; }
.badge-blue { background:#1a1a2a; color:#47a0e8; }
.empty { text-align:center; padding:40px; color:#444; }
.empty .icon { font-size:2.5rem; margin-bottom:8px; }
.flash { background:#2a1a1a; border:1px solid #e8394730; color:#e84747;
         border-radius:8px; padding:10px 14px; margin-bottom:16px; font-size:0.85rem; }
.flash.success { background:#1a2a1a; border-color:#47e86030; color:#47e860; }
.form-group { margin-bottom:14px; }
label { display:block; color:#aaa; font-size:0.83rem; margin-bottom:5px; }
input, select {
    background:#1e1e1e; border:1px solid #2a2a2a; border-radius:8px;
    padding:10px 14px; color:#fff; font-size:0.9rem; outline:none;
    transition:border 0.2s; width:100%;
}
input:focus, select:focus { border-color:#e8c547; }
/* Mobile Responsive */
@media (max-width: 768px) {
    nav {
        padding: 0 16px;
        flex-wrap: wrap;
        height: auto;
        padding: 12px 16px;
    }
    .logo {
        font-size: 1.4rem;
    }
    .nav-links {
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 8px;
    }
    .nav-links a, .btn {
        font-size: 0.75rem;
        padding: 6px 12px;
    }
    .hero {
        padding: 40px 20px;
    }
    .hero h1 {
        font-size: 2rem;
    }
    .hero p {
        font-size: 0.9rem;
    }
    .hero-btns {
        flex-direction: column;
        gap: 10px;
    }
    .stats-bar {
        flex-wrap: wrap;
        gap: 16px;
        padding: 16px;
    }
    .stat {
        flex: 1;
        min-width: 80px;
    }
    .categories {
        padding: 16px;
        gap: 8px;
    }
    .cat-btn {
        padding: 6px 12px;
        font-size: 0.7rem;
    }
    .section {
        padding: 24px 16px;
    }
    .grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 12px;
    }
    .card-body {
        padding: 8px;
    }
    .card-title {
        font-size: 0.8rem;
    }
    .card-sub {
        font-size: 0.7rem;
    }
    .card-price {
        font-size: 0.75rem;
    }
    .section-title {
        font-size: 1.1rem;
    }
    .artist-grid {
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 12px;
    }
    .sidebar {
        display: none;
    }
    .layout {
        grid-template-columns: 1fr;
    }
    .main {
        padding: 16px;
    }
    .stats-row {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .payment-card {
        padding: 24px;
        margin: 16px;
    }
    table {
        display: block;
        overflow-x: auto;
    }
    th, td {
        padding: 8px;
        font-size: 0.7rem;
    }
}
</style>
"""

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect('/store')
        return f(*args, **kwargs)
    return decorated


# ── Admin Home ─────────────────────────────────────────────────────────────────
@admin_bp.route("/")
@login_required
@admin_required
def home():
    conn = get_db()
    total_users    = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_artists  = conn.execute("SELECT COUNT(*) FROM artist_profiles").fetchone()[0]
    pending        = conn.execute("SELECT COUNT(*) FROM artist_profiles WHERE is_verified=0").fetchone()[0]
    total_tracks   = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    total_sales    = conn.execute("SELECT COUNT(*) FROM orders WHERE status='paid'").fetchone()[0]
    total_revenue  = conn.execute("SELECT COALESCE(SUM(amount),0) FROM orders WHERE status='paid'").fetchone()[0]
    platform_cut   = conn.execute("SELECT COALESCE(SUM(platform_cut),0) FROM orders WHERE status='paid'").fetchone()[0]

    recent_orders = conn.execute("""
        SELECT o.*, u.username as buyer_name
        FROM orders o
        LEFT JOIN users u ON o.buyer_id = u.id
        ORDER BY o.created_at DESC LIMIT 8
    """).fetchall()

    recent_users = conn.execute("""
        SELECT * FROM users ORDER BY created_at DESC LIMIT 5
    """).fetchall()

    conn.close()

    return render_template_string(ADMIN_STYLE + """
    <!DOCTYPE html><html><head><title>Admin — Nutifa</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <a href="/store">Store</a>
            <span style="color:#e84747;font-size:0.8rem;font-weight:700">⚡ ADMIN</span>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <div class="sidebar-section">Main</div>
            <a href="/admin" class="sidebar-item active">
                <span class="icon">📊</span>Overview
            </a>
            <a href="/admin/artists" class="sidebar-item">
                <span class="icon">🎤</span>Artists
            </a>
            <a href="/admin/users" class="sidebar-item">
                <span class="icon">👥</span>Users
            </a>
            <div class="sidebar-section">Content</div>
            <a href="/admin/tracks" class="sidebar-item">
                <span class="icon">🎵</span>All Tracks
            </a>
            <a href="/admin/orders" class="sidebar-item">
                <span class="icon">💰</span>All Orders
            </a>
            <div class="sidebar-section">Settings</div>
            <a href="/admin/settings" class="sidebar-item">
                <span class="icon">⚙️</span>Settings
            </a>
            <a href="/store" class="sidebar-item">
                <span class="icon">🏪</span>Visit Store
            </a>
        </div>
        <div class="main">
            <div class="page-title">Admin Overview 📊</div>
            <div class="page-sub">Nutifa platform at a glance</div>

            <div class="stats-row">
                <div class="stat-card">
                    <div class="num">{{ total_users }}</div>
                    <div class="label">Total Users</div>
                </div>
                <div class="stat-card">
                    <div class="num">{{ total_artists }}</div>
                    <div class="label">Artists</div>
                </div>
                <div class="stat-card">
                    <div class="num">{{ total_tracks }}</div>
                    <div class="label">Tracks</div>
                </div>
                <div class="stat-card">
                    <div class="num">{{ total_sales }}</div>
                    <div class="label">Sales</div>
                </div>
                <div class="stat-card">
                    <div class="num">GHS {{ "%.2f"|format(platform_cut) }}</div>
                    <div class="label">Your Earnings</div>
                </div>
            </div>

            {% if pending > 0 %}
            <div class="flash" style="background:#2a2a1a;border-color:#e8c54730;color:#e8c547">
                ⚠️ {{ pending }} artist(s) waiting for approval —
                <a href="/admin/artists" style="color:#e8c547">Review now →</a>
            </div>
            {% endif %}

            <div class="section">
                <div class="section-header">
                    <div class="section-title">Recent Orders</div>
                    <a href="/admin/orders" class="btn btn-outline btn-sm">See All</a>
                </div>
                {% if recent_orders %}
                <table>
                    <tr>
                        <th>Buyer</th><th>Item</th><th>Amount</th>
                        <th>Platform Cut</th><th>Method</th><th>Status</th>
                    </tr>
                    {% for o in recent_orders %}
                    <tr>
                        <td>{{ o['buyer_name'] or o['buyer_email'] }}</td>
                        <td>{{ o['item_type'] }} #{{ o['item_id'] }}</td>
                        <td>GHS {{ "%.2f"|format(o['amount']) }}</td>
                        <td>GHS {{ "%.2f"|format(o['platform_cut']) }}</td>
                        <td>{{ o['payment_method'] or '—' }}</td>
                        <td>
                            <span class="badge
                                {% if o['status']=='paid' %}badge-green
                                {% elif o['status']=='pending' %}badge-yellow
                                {% else %}badge-red{% endif %}">
                                {{ o['status'] }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <div class="empty">
                    <div class="icon">💰</div>
                    <p>No orders yet</p>
                </div>
                {% endif %}
            </div>

            <div class="section">
                <div class="section-header">
                    <div class="section-title">Recent Users</div>
                    <a href="/admin/users" class="btn btn-outline btn-sm">See All</a>
                </div>
                <table>
                    <tr>
                        <th>#</th><th>Name</th><th>Email</th>
                        <th>Username</th><th>Role</th><th>Joined</th>
                    </tr>
                    {% for u in recent_users %}
                    <tr>
                        <td>{{ u['id'] }}</td>
                        <td>{{ u['full_name'] or '—' }}</td>
                        <td>{{ u['email'] }}</td>
                        <td>@{{ u['username'] }}</td>
                        <td>
                            <span class="badge
                                {% if u['role']=='admin' %}badge-red
                                {% elif u['role']=='artist' %}badge-yellow
                                {% else %}badge-blue{% endif %}">
                                {{ u['role'] }}
                            </span>
                        </td>
                        <td>{{ u['created_at'][:10] }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>
    </body></html>
    """, total_users=total_users, total_artists=total_artists,
         pending=pending, total_tracks=total_tracks,
         total_sales=total_sales, total_revenue=total_revenue,
         platform_cut=platform_cut, recent_orders=recent_orders,
         recent_users=recent_users)


# ── Artists Management ─────────────────────────────────────────────────────────
@admin_bp.route("/artists")
@login_required
@admin_required
def artists():
    conn = get_db()
    all_artists = conn.execute("""
        SELECT ap.*, u.email, u.username, u.full_name, u.phone
        FROM artist_profiles ap
        JOIN users u ON ap.user_id = u.id
        ORDER BY ap.created_at DESC
    """).fetchall()
    conn.close()

    return render_template_string(ADMIN_STYLE + """
    <!DOCTYPE html><html><head><title>Artists — Nutifa Admin</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <span style="color:#e84747;font-size:0.8rem;font-weight:700">⚡ ADMIN</span>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <div class="sidebar-section">Main</div>
            <a href="/admin" class="sidebar-item"><span class="icon">📊</span>Overview</a>
            <a href="/admin/artists" class="sidebar-item active"><span class="icon">🎤</span>Artists</a>
            <a href="/admin/users" class="sidebar-item"><span class="icon">👥</span>Users</a>
            <div class="sidebar-section">Content</div>
            <a href="/admin/tracks" class="sidebar-item"><span class="icon">🎵</span>All Tracks</a>
            <a href="/admin/orders" class="sidebar-item"><span class="icon">💰</span>All Orders</a>
            <div class="sidebar-section">Settings</div>
            <a href="/admin/settings" class="sidebar-item"><span class="icon">⚙️</span>Settings</a>
        </div>
        <div class="main">
            <div class="page-title">Artists 🎤</div>
            <div class="page-sub">Approve and manage artists on Nutifa</div>
            <div class="section">
                {% if all_artists %}
                <table>
                    <tr>
                        <th>Stage Name</th><th>Real Name</th><th>Email</th>
                        <th>Genre</th><th>Status</th><th>Actions</th>
                    </tr>
                    {% for a in all_artists %}
                    <tr>
                        <td><strong>{{ a['stage_name'] }}</strong></td>
                        <td>{{ a['full_name'] or '—' }}</td>
                        <td>{{ a['email'] }}</td>
                        <td>{{ a['genre'] or '—' }}</td>
                        <td>
                            {% if a['is_verified'] %}
                                <span class="badge badge-green">Approved</span>
                            {% else %}
                                <span class="badge badge-yellow">Pending</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if not a['is_verified'] %}
                            <a href="/admin/artist/approve/{{ a['id'] }}"
                               class="btn btn-green btn-sm">✓ Approve</a>
                            {% else %}
                            <a href="/admin/artist/suspend/{{ a['id'] }}"
                               class="btn btn-red btn-sm">✗ Suspend</a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <div class="empty">
                    <div class="icon">🎤</div>
                    <p>No artists yet</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    </body></html>
    """, all_artists=all_artists)


@admin_bp.route("/artist/approve/<int:artist_id>")
@login_required
@admin_required
def approve_artist(artist_id):
    conn = get_db()
    conn.execute("UPDATE artist_profiles SET is_verified=1 WHERE id=?", (artist_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/artists')


@admin_bp.route("/artist/suspend/<int:artist_id>")
@login_required
@admin_required
def suspend_artist(artist_id):
    conn = get_db()
    conn.execute("UPDATE artist_profiles SET is_verified=0 WHERE id=?", (artist_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/artists')


# ── Users Management ───────────────────────────────────────────────────────────
@admin_bp.route("/users")
@login_required
@admin_required
def users():
    conn = get_db()
    all_users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template_string(ADMIN_STYLE + """
    <!DOCTYPE html><html><head><title>Users — Nutifa Admin</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <span style="color:#e84747;font-size:0.8rem;font-weight:700">⚡ ADMIN</span>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <div class="sidebar-section">Main</div>
            <a href="/admin" class="sidebar-item"><span class="icon">📊</span>Overview</a>
            <a href="/admin/artists" class="sidebar-item"><span class="icon">🎤</span>Artists</a>
            <a href="/admin/users" class="sidebar-item active"><span class="icon">👥</span>Users</a>
            <div class="sidebar-section">Content</div>
            <a href="/admin/tracks" class="sidebar-item"><span class="icon">🎵</span>All Tracks</a>
            <a href="/admin/orders" class="sidebar-item"><span class="icon">💰</span>All Orders</a>
            <div class="sidebar-section">Settings</div>
            <a href="/admin/settings" class="sidebar-item"><span class="icon">⚙️</span>Settings</a>
        </div>
        <div class="main">
            <div class="page-title">Users 👥</div>
            <div class="page-sub">All registered users on Nutifa</div>
            <div class="section">
                <table>
                    <tr>
                        <th>#</th><th>Name</th><th>Email</th>
                        <th>Username</th><th>Role</th>
                        <th>Status</th><th>Joined</th><th>Action</th>
                    </tr>
                    {% for u in all_users %}
                    <tr>
                        <td>{{ u['id'] }}</td>
                        <td>{{ u['full_name'] or '—' }}</td>
                        <td>{{ u['email'] }}</td>
                        <td>@{{ u['username'] }}</td>
                        <td>
                            <span class="badge
                                {% if u['role']=='admin' %}badge-red
                                {% elif u['role']=='artist' %}badge-yellow
                                {% else %}badge-blue{% endif %}">
                                {{ u['role'] }}
                            </span>
                        </td>
                        <td>
                            {% if u['is_active'] %}
                                <span class="badge badge-green">Active</span>
                            {% else %}
                                <span class="badge badge-red">Suspended</span>
                            {% endif %}
                        </td>
                        <td>{{ u['created_at'][:10] }}</td>
                        <td>
                            {% if u['role'] != 'admin' %}
                            <a href="/admin/user/toggle/{{ u['id'] }}"
                               class="btn btn-sm {% if u['is_active'] %}btn-red{% else %}btn-green{% endif %}">
                               {% if u['is_active'] %}Suspend{% else %}Activate{% endif %}
                            </a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>
    </body></html>
    """, all_users=all_users)


@admin_bp.route("/user/toggle/<int:user_id>")
@login_required
@admin_required
def toggle_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT is_active FROM users WHERE id=?", (user_id,)).fetchone()
    new_status = 0 if user['is_active'] else 1
    conn.execute("UPDATE users SET is_active=? WHERE id=?", (new_status, user_id))
    conn.commit()
    conn.close()
    return redirect('/admin/users')


# ── All Tracks ─────────────────────────────────────────────────────────────────
@admin_bp.route("/tracks")
@login_required
@admin_required
def tracks():
    conn = get_db()
    all_tracks = conn.execute("""
        SELECT t.*, ap.stage_name
        FROM tracks t
        JOIN artist_profiles ap ON t.artist_id = ap.id
        ORDER BY t.created_at DESC
    """).fetchall()
    conn.close()

    return render_template_string(ADMIN_STYLE + """
    <!DOCTYPE html><html><head><title>Tracks — Nutifa Admin</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <span style="color:#e84747;font-size:0.8rem;font-weight:700">⚡ ADMIN</span>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <div class="sidebar-section">Main</div>
            <a href="/admin" class="sidebar-item"><span class="icon">📊</span>Overview</a>
            <a href="/admin/artists" class="sidebar-item"><span class="icon">🎤</span>Artists</a>
            <a href="/admin/users" class="sidebar-item"><span class="icon">👥</span>Users</a>
            <div class="sidebar-section">Content</div>
            <a href="/admin/tracks" class="sidebar-item active"><span class="icon">🎵</span>All Tracks</a>
            <a href="/admin/orders" class="sidebar-item"><span class="icon">💰</span>All Orders</a>
            <div class="sidebar-section">Settings</div>
            <a href="/admin/settings" class="sidebar-item"><span class="icon">⚙️</span>Settings</a>
        </div>
        <div class="main">
            <div class="page-title">All Tracks 🎵</div>
            <div class="page-sub">Every track uploaded on Nutifa</div>
            <div class="section">
                {% if all_tracks %}
                <table>
                    <tr>
                        <th>Title</th><th>Artist</th><th>Type</th>
                        <th>Price</th><th>Downloads</th>
                        <th>Status</th><th>Uploaded</th>
                    </tr>
                    {% for t in all_tracks %}
                    <tr>
                        <td><strong>{{ t['title'] }}</strong></td>
                        <td>{{ t['stage_name'] }}</td>
                        <td>{{ t['track_type'] }}</td>
                        <td>
                            {% if t['price'] == 0 %}
                                <span style="color:#47e860">FREE</span>
                            {% else %}
                                {{ t['currency'] }} {{ "%.2f"|format(t['price']) }}
                            {% endif %}
                        </td>
                        <td>{{ t['downloads'] }}</td>
                        <td>
                            <span class="badge {% if t['is_published'] %}badge-green{% else %}badge-yellow{% endif %}">
                                {% if t['is_published'] %}Published{% else %}Draft{% endif %}
                            </span>
                        </td>
                        <td>{{ t['created_at'][:10] }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <div class="empty">
                    <div class="icon">🎵</div>
                    <p>No tracks yet</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    </body></html>
    """, all_tracks=all_tracks)


# ── Settings ───────────────────────────────────────────────────────────────────
@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def settings():
    conn = get_db()
    success = ""
    if request.method == "POST":
        for key in ["platform_name", "platform_cut_pct", "currency_default"]:
            val = request.form.get(key, "")
            conn.execute("UPDATE settings SET value=? WHERE key=?", (val, key))
        conn.commit()
        success = "Settings saved!"

    all_settings = {row['key']: row['value']
                    for row in conn.execute("SELECT * FROM settings").fetchall()}
    conn.close()

    return render_template_string(ADMIN_STYLE + """
    <!DOCTYPE html><html><head><title>Settings — Nutifa Admin</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <span style="color:#e84747;font-size:0.8rem;font-weight:700">⚡ ADMIN</span>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <div class="sidebar-section">Main</div>
            <a href="/admin" class="sidebar-item"><span class="icon">📊</span>Overview</a>
            <a href="/admin/artists" class="sidebar-item"><span class="icon">🎤</span>Artists</a>
            <a href="/admin/users" class="sidebar-item"><span class="icon">👥</span>Users</a>
            <div class="sidebar-section">Content</div>
            <a href="/admin/tracks" class="sidebar-item"><span class="icon">🎵</span>All Tracks</a>
            <a href="/admin/orders" class="sidebar-item"><span class="icon">💰</span>All Orders</a>
            <div class="sidebar-section">Settings</div>
            <a href="/admin/settings" class="sidebar-item active"><span class="icon">⚙️</span>Settings</a>
        </div>
        <div class="main">
            <div class="page-title">Platform Settings ⚙️</div>
            <div class="page-sub">Configure your Nutifa marketplace</div>
            {% if success %}
            <div class="flash success">✅ {{ success }}</div>
            {% endif %}
            <div class="section">
                <form method="POST">
                    <div class="form-group">
                        <label>Platform Name</label>
                        <input type="text" name="platform_name"
                               value="{{ settings.get('platform_name','Nutifa') }}">
                    </div>
                    <div class="form-group">
                        <label>Platform Cut % (your earnings per sale)</label>
                        <input type="number" name="platform_cut_pct" min="0" max="50"
                               value="{{ settings.get('platform_cut_pct','15') }}">
                    </div>
                    <div class="form-group">
                        <label>Default Currency</label>
                        <select name="currency_default">
                            <option {% if settings.get('currency_default')=='GHS' %}selected{% endif %}>GHS</option>
                            <option {% if settings.get('currency_default')=='USD' %}selected{% endif %}>USD</option>
                            <option {% if settings.get('currency_default')=='GBP' %}selected{% endif %}>GBP</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-gold">Save Settings</button>
                </form>
            </div>
        </div>
    </div>
    </body></html>
    """, all_settings=all_settings, settings=all_settings, success=success)


# ── Orders ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/orders")
@login_required
@admin_required
def orders():
    conn = get_db()
    all_orders = conn.execute("""
        SELECT o.*, u.username as buyer_name
        FROM orders o
        LEFT JOIN users u ON o.buyer_id = u.id
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()

    return render_template_string(ADMIN_STYLE + """
    <!DOCTYPE html><html><head><title>Orders — Nutifa Admin</title></head><body>
    <nav>
        <a href="/" class="logo">NUTIFA.</a>
        <div class="nav-links">
            <span style="color:#e84747;font-size:0.8rem;font-weight:700">⚡ ADMIN</span>
            <a href="/logout" class="btn btn-outline">Log Out</a>
        </div>
    </nav>
    <div class="layout">
        <div class="sidebar">
            <div class="sidebar-section">Main</div>
            <a href="/admin" class="sidebar-item"><span class="icon">📊</span>Overview</a>
            <a href="/admin/artists" class="sidebar-item"><span class="icon">🎤</span>Artists</a>
            <a href="/admin/users" class="sidebar-item"><span class="icon">👥</span>Users</a>
            <div class="sidebar-section">Content</div>
            <a href="/admin/tracks" class="sidebar-item"><span class="icon">🎵</span>All Tracks</a>
            <a href="/admin/orders" class="sidebar-item active"><span class="icon">💰</span>All Orders</a>
            <div class="sidebar-section">Settings</div>
            <a href="/admin/settings" class="sidebar-item"><span class="icon">⚙️</span>Settings</a>
        </div>
        <div class="main">
            <div class="page-title">All Orders 💰</div>
            <div class="page-sub">Every sale made on Nutifa</div>
            <div class="section">
                {% if all_orders %}
                <table>
                    <tr>
                        <th>#</th><th>Buyer</th><th>Item</th><th>Amount</th>
                        <th>Platform Cut</th><th>Artist Earns</th>
                        <th>Method</th><th>Status</th><th>Date</th>
                    </tr>
                    {% for o in all_orders %}
                    <tr>
                        <td>{{ o['id'] }}</td>
                        <td>{{ o['buyer_name'] or o['buyer_email'] }}</td>
                        <td>{{ o['item_type'] }}</td>
                        <td>GHS {{ "%.2f"|format(o['amount']) }}</td>
                        <td>GHS {{ "%.2f"|format(o['platform_cut']) }}</td>
                        <td>GHS {{ "%.2f"|format(o['artist_earnings']) }}</td>
                        <td>{{ o['payment_method'] or '—' }}</td>
                        <td>
                            <span class="badge
                                {% if o['status']=='paid' %}badge-green
                                {% elif o['status']=='pending' %}badge-yellow
                                {% else %}badge-red{% endif %}">
                                {{ o['status'] }}
                            </span>
                        </td>
                        <td>{{ o['created_at'][:10] }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <div class="empty">
                    <div class="icon">💰</div>
                    <p>No orders yet</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    </body></html>
    """, all_orders=all_orders)