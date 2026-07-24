import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Blueprint, render_template_string, request, redirect, url_for
from flask_login import current_user
from database.schema import get_db

store_bp = Blueprint('store', __name__)

PAGE_STYLE = """
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
.categories {
    display: flex;
    gap: 12px;
    padding: 24px 32px;
    border-bottom: 1px solid #1a1a1a;
    overflow-x: auto;
}
.cat-btn {
    background: #1a1a1a;
    border: 1px solid #222;
    border-radius: 20px;
    padding: 8px 20px;
    color: #aaa;
    font-size: 0.85rem;
    cursor: pointer;
    white-space: nowrap;
    text-decoration: none;
    transition: all 0.2s;
}
.cat-btn:hover, .cat-btn.active {
    background: #e8c547;
    color: #0a0a0a;
    border-color: #e8c547;
    font-weight: 700;
}
.section {
    padding: 40px 32px;
    border-bottom: 1px solid #1a1a1a;
}
.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #fff;
}
.section-title span { color: #e8c547; }
.see-all {
    color: #e8c547;
    text-decoration: none;
    font-size: 0.85rem;
}
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}
.card {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
    cursor: pointer;
}
.card:hover {
    transform: translateY(-4px);
    border-color: #e8c547;
}
.card-img {
    width: 100%;
    aspect-ratio: 1;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    position: relative;
}
.card-img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.play-btn {
    position: absolute;
    bottom: 8px;
    right: 8px;
    background: #e8c547;
    color: #0a0a0a;
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    font-size: 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.2s;
}
.card:hover .play-btn { opacity: 1; }
.card-body { padding: 12px; }
.card-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #fff;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.card-sub {
    font-size: 0.78rem;
    color: #666;
    margin-bottom: 8px;
}
.card-price {
    font-size: 0.85rem;
    font-weight: 700;
    color: #e8c547;
}
.card-price.free { color: #47e860; }
.artist-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 20px;
}
.artist-card {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 12px;
    padding: 20px 12px;
    text-align: center;
    transition: all 0.2s;
    cursor: pointer;
    text-decoration: none;
}
.artist-card:hover {
    border-color: #e8c547;
    transform: translateY(-4px);
}
.artist-avatar {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: linear-gradient(135deg, #e8c547, #c4a030);
    margin: 0 auto 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: 900;
    color: #0a0a0a;
    overflow: hidden;
}
.artist-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.artist-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 4px;
}
.artist-genre {
    font-size: 0.75rem;
    color: #666;
}
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #444;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 12px; }
.empty-state p { font-size: 0.9rem; }
.stats-bar {
    display: flex;
    gap: 32px;
    padding: 20px 32px;
    background: #111;
    border-bottom: 1px solid #1a1a1a;
}
.stat { text-align: center; }
.stat-num {
    font-size: 1.4rem;
    font-weight: 900;
    color: #e8c547;
}
.stat-label {
    font-size: 0.75rem;
    color: #555;
    margin-top: 2px;
}
footer {
    background: #111;
    border-top: 1px solid #1a1a1a;
    padding: 32px;
    text-align: center;
    color: #444;
    font-size: 0.85rem;
    margin-top: 40px;
}
footer span { color: #e8c547; }
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

@store_bp.route("/store")
def store():
    conn = get_db()

    # Get stats
    track_count   = conn.execute("SELECT COUNT(*) FROM tracks WHERE is_published=1").fetchone()[0]
    artist_count  = conn.execute("SELECT COUNT(*) FROM artist_profiles WHERE is_verified=1").fetchone()[0]
    order_count   = conn.execute("SELECT COUNT(*) FROM orders WHERE status='paid'").fetchone()[0]

    # Get latest tracks
    tracks = conn.execute("""
        SELECT t.*, ap.stage_name
        FROM tracks t
        JOIN artist_profiles ap ON t.artist_id = ap.id
        WHERE t.is_published = 1
        ORDER BY t.created_at DESC LIMIT 8
    """).fetchall()

    # Get artists
    artists = conn.execute("""
        SELECT ap.*, u.username
        FROM artist_profiles ap
        JOIN users u ON ap.user_id = u.id
        WHERE ap.is_verified = 1
        ORDER BY ap.created_at DESC LIMIT 8
    """).fetchall()

    # Get beats
    beats = conn.execute("""
        SELECT t.*, ap.stage_name
        FROM tracks t
        JOIN artist_profiles ap ON t.artist_id = ap.id
        WHERE t.is_published = 1 AND t.track_type = 'beat'
        ORDER BY t.created_at DESC LIMIT 4
    """).fetchall()

    conn.close()

    return render_template_string(PAGE_STYLE + """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hajilala — Ghana's Music Marketplace</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>

    <!-- NAV -->
    <nav>
        <a href="/" class="logo">HAJILALA.</a>
        <div class="nav-links">
            <a href="/store">Store</a>
            <a href="/store?cat=beats">Beats</a>
            <a href="/store?cat=videos">Videos</a>
            <a href="/store?cat=merch">Merch</a>
            {% if current_user.is_authenticated %}
                {% if current_user.role == 'artist' %}
                    <a href="/artist/dashboard">My Dashboard</a>
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

    <!-- HERO -->
    <div class="hero">
        <h1>HAJILALA.</h1>
        <p>🎵 Ghana's Home for Independent Music — Buy, Sell & Support Local Artists</p>
        <div class="hero-btns">
            <a href="/signup?role=artist" class="btn btn-gold">🎤 Sell Your Music</a>
            <a href="/store" class="btn btn-outline">🎧 Browse Music</a>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-bar">
        <div class="stat">
            <div class="stat-num">{{ track_count }}</div>
            <div class="stat-label">Tracks</div>
        </div>
        <div class="stat">
            <div class="stat-num">{{ artist_count }}</div>
            <div class="stat-label">Artists</div>
        </div>
        <div class="stat">
            <div class="stat-num">{{ order_count }}</div>
            <div class="stat-label">Sales</div>
        </div>
        <div class="stat">
            <div class="stat-num">GHS</div>
            <div class="stat-label">Currency</div>
        </div>
    </div>

    <!-- CATEGORIES -->
    <div class="categories">
        <a href="/store" class="cat-btn active">🎵 All Music</a>
        <a href="/store?cat=songs" class="cat-btn">🎤 Songs</a>
        <a href="/store?cat=beats" class="cat-btn">🥁 Beats</a>
        <a href="/store?cat=albums" class="cat-btn">💿 Albums</a>
        <a href="/store?cat=videos" class="cat-btn">🎬 Videos</a>
        <a href="/store?cat=merch" class="cat-btn">👕 Merch</a>
    </div>

    <!-- LATEST TRACKS -->
    <div class="section">
        <div class="section-header">
            <div class="section-title">🔥 Latest <span>Tracks</span></div>
            <a href="/store?cat=songs" class="see-all">See all →</a>
        </div>
        {% if tracks %}
        <div class="grid">
            {% for track in tracks %}
            <div class="card">
                <div class="card-img">
                    {% if track.cover_image %}
                        <img src="/static/uploads/music/{{ track.cover_image }}" alt="">
                    {% else %}
                        🎵
                    {% endif %}
                    <button class="play-btn">▶</button>
                </div>
                <div class="card-body">
                    <div class="card-title">{{ track.title }}</div>
                    <div class="card-sub">{{ track.stage_name }}</div>
                    <div class="card-price {% if track.price == 0 %}free{% endif %}">
                        {% if track.price == 0 %}
                            FREE
                        {% else %}
                            GHS {{ "%.2f"|format(track.price) }}
                        {% endif %}
                    </div>
                    {% if track.price > 0 %}
                        <a href="/payment/initiate/{{ track.id }}" class="btn btn-gold" style="display:block; text-align:center; margin-top:10px; padding:6px; font-size:0.75rem;">
                            Buy Now →
                        </a>
                    {% else %}
                        <a href="/payment/download-free/{{ track.id }}" class="btn btn-outline" style="display:block; text-align:center; margin-top:10px; padding:6px; font-size:0.75rem;">
                            Free Download
                        </a>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <div class="icon">🎵</div>
            <p>No tracks yet — be the first artist to upload!</p>
            <br>
            <a href="/signup?role=artist" class="btn btn-gold">Start Selling</a>
        </div>
        {% endif %}
    </div>

    <!-- ARTISTS -->
    <div class="section">
        <div class="section-header">
            <div class="section-title">🎤 Featured <span>Artists</span></div>
        </div>
        {% if artists %}
        <div class="artist-grid">
            {% for artist in artists %}
            <a href="/artist/{{ artist.id }}" class="artist-card">
                <div class="artist-avatar">
                    {% if artist.cover_image %}
                        <img src="/static/uploads/avatars/{{ artist.cover_image }}" alt="">
                    {% else %}
                        {{ artist.stage_name[0].upper() }}
                    {% endif %}
                </div>
                <div class="artist-name">{{ artist.stage_name }}</div>
                <div class="artist-genre">{{ artist.genre or 'Music' }}</div>
            </a>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <div class="icon">🎤</div>
            <p>No artists yet — join as an artist today!</p>
        </div>
        {% endif %}
    </div>

    <!-- BEATS -->
    <div class="section">
        <div class="section-header">
            <div class="section-title">🥁 Hot <span>Beats</span></div>
            <a href="/store?cat=beats" class="see-all">See all →</a>
        </div>
        {% if beats %}
        <div class="grid">
            {% for beat in beats %}
            <div class="card">
                <div class="card-img">🥁<button class="play-btn">▶</button></div>
                <div class="card-body">
                    <div class="card-title">{{ beat.title }}</div>
                    <div class="card-sub">{{ beat.stage_name }}</div>
                    <div class="card-price">GHS {{ "%.2f"|format(beat.price) }}</div>
                    <a href="/payment/initiate/{{ beat.id }}" class="btn btn-gold" style="display:block; text-align:center; margin-top:10px; padding:6px; font-size:0.75rem;">
                        Buy Beat →
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <div class="icon">🥁</div>
            <p>No beats yet — upload your first beat!</p>
        </div>
        {% endif %}
    </div>

    <footer>
        <p>© 2026 <span>Hajilala</span> — Peace & Harmony 🎵 Made in Ghana</p>
    </footer>

    </body>
    </html>
    """, current_user=current_user,
         track_count=track_count,
         artist_count=artist_count,
         order_count=order_count,
         tracks=tracks,
         artists=artists,
         beats=beats)