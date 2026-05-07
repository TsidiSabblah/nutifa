import os
import sys
import json
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Blueprint, render_template_string, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from database.schema import get_db
from dotenv import load_dotenv

load_dotenv()

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')

# ── Style for payment pages ────────────────────────────────────────────────
PAY_STYLE = """
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
    background: #0a0a0a;
    color: #fff;
    font-family: 'Segoe UI', sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}
.payment-card {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 16px;
    padding: 40px;
    max-width: 480px;
    width: 100%;
    text-align: center;
}
.logo {
    font-size: 2rem;
    font-weight: 900;
    color: #e8c547;
    margin-bottom: 8px;
}
.item-info {
    background: #1a1a1a;
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
}
.item-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #e8c547;
}
.item-price {
    font-size: 1.8rem;
    font-weight: 900;
    margin: 12px 0;
}
.form-group {
    margin-bottom: 20px;
    text-align: left;
}
.form-group label {
    display: block;
    color: #aaa;
    font-size: 0.85rem;
    margin-bottom: 8px;
}
.form-group input {
    width: 100%;
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 12px;
    color: #fff;
    font-size: 0.9rem;
    outline: none;
}
.form-group input:focus {
    border-color: #e8c547;
}
.paystack-btn {
    background: #e8c547;
    color: #0a0a0a;
    border: none;
    border-radius: 8px;
    padding: 14px 24px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    width: 100%;
    margin-top: 16px;
    transition: opacity 0.2s;
}
.paystack-btn:hover { opacity: 0.9; }
.back-link {
    display: block;
    margin-top: 20px;
    color: #555;
    text-decoration: none;
    font-size: 0.85rem;
}
.back-link:hover { color: #e8c547; }
.flash {
    background: #2a1a1a;
    border: 1px solid #e8394730;
    color: #e84747;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 16px;
    font-size: 0.85rem;
}
.flash.success {
    background: #1a2a1a;
    border-color: #47e86030;
    color: #47e860;
}
.success-page {
    text-align: center;
}
.success-page .checkmark {
    font-size: 4rem;
    color: #47e860;
    margin-bottom: 20px;
}
.download-link {
    display: inline-block;
    background: #e8c547;
    color: #0a0a0a;
    padding: 12px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 700;
    margin-top: 20px;
}
</style>
"""

# ── Step 1: Show payment page for a track ─────────────────────────────────
@payment_bp.route("/buy/<int:track_id>")
@login_required
def buy_track(track_id):
    conn = get_db()
    track = conn.execute("""
        SELECT t.*, ap.stage_name, ap.id as artist_id
        FROM tracks t
        JOIN artist_profiles ap ON t.artist_id = ap.id
        WHERE t.id = ? AND t.is_published = 1
    """, (track_id,)).fetchone()
    conn.close()

    if not track:
        flash("Track not found", "error")
        return redirect('/store')

    return render_template_string(PAY_STYLE + """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Buy {{ track.title }} — Nutifa</title>
        <script src="https://js.paystack.co/v1/inline.js"></script>
    </head>
    <body>
        <div class="payment-card">
            <div class="logo">NUTIFA.</div>
            <div class="item-info">
                <div class="item-title">{{ track.title }}</div>
                <div class="item-sub">by {{ track.stage_name }}</div>
                <div class="item-price">GHS {{ "%.2f"|format(track.price) }}</div>
                <div style="font-size:0.75rem; color:#555;">You get instant download after payment</div>
            </div>
            
            <div class="form-group">
                <label>📧 Email for Receipt *</label>
                <input type="email" id="payer_email" placeholder="your@email.com" 
                       value="{{ current_user.email if current_user.email else '' }}">
            </div>
            
            <button onclick="payWithPaystack()" class="paystack-btn">
                💳 Pay with Mobile Money or Card
            </button>
            
            <a href="/store" class="back-link">← Back to Store</a>
        </div>
        
        <script>
            function payWithPaystack() {
                let email = document.getElementById('payer_email').value;
                if (!email) {
                    alert('Please enter your email address');
                    return;
                }
                if (email.indexOf('@') === -1 || email.indexOf('.') === -1) {
                    alert('Please enter a valid email address (e.g., name@example.com)');
                    return;
                }
                
                let handler = PaystackPop.setup({
                    key: '{{ paystack_public_key }}',
                    email: email,
                    amount: {{ track.price * 100 }},
                    currency: 'GHS',
                    ref: 'NUTIFA-' + Date.now() + '-' + Math.floor(Math.random() * 10000),
                    callback: function(response) {
                        console.log('Payment successful. Reference:', response.reference);
                        fetch('/payment/verify/' + response.reference, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        }).then(res => res.json()).then(data => {
                            console.log('Verification response:', data);
                            if (data.success) {
                                window.location.href = '/payment/download-page/' + data.download_token;
                            } else {
                                alert('Payment verification failed. Your transaction reference is: ' + response.reference + '\\nPlease contact support with this reference.');
                            }
                        }).catch(err => {
                            console.error('Verification error:', err);
                            alert('Network error. Your transaction reference is: ' + response.reference + '\\nPlease click OK to manually verify.');
                            window.location.href = '/payment/manual/' + response.reference;
                        });
                    },
                    onClose: function() {
                        alert('Payment cancelled');
                    }
                });
                handler.openIframe();
            }
        </script>
    </body>
    </html>
    """, track=track, current_user=current_user, 
         paystack_public_key=PAYSTACK_PUBLIC_KEY)


# ── Step 2: Verify payment with Paystack ───────────────────────────────────
@payment_bp.route("/verify/<reference>", methods=["POST"])
@login_required
def verify_payment(reference):
    print(f"=== VERIFYING PAYMENT: {reference} ===")
    
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers=headers
    )
    
    data = response.json()
    print(f"Paystack response: {data}")
    
    if data.get('status') and data['data']['status'] == 'success':
        # Payment successful! Create order record
        tx = data['data']
        amount = tx['amount'] / 100  # Convert from pesewas
        
        # Get track_id from session
        track_id = session.get('buying_track_id')
        if not track_id:
            return {"success": False, "error": "No item in cart"}
        
        conn = get_db()
        
        # Get track info
        track = conn.execute("SELECT * FROM tracks WHERE id=?", (track_id,)).fetchone()
        
        if not track:
            conn.close()
            return {"success": False, "error": "Track not found"}
        
        platform_cut = amount * 0.15  # 15%
        artist_earnings = amount * 0.85  # 85%
        
        # Create order
        conn.execute("""
            INSERT INTO orders (
                buyer_id, buyer_email, item_type, item_id, artist_id,
                amount, currency, platform_cut, artist_earnings,
                payment_method, payment_ref, status, paid_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'paid', datetime('now'))
        """, (
            current_user.id, tx['customer']['email'], 'track', track_id, track['artist_id'],
            amount, 'GHS', platform_cut, artist_earnings,
            'paystack', reference
        ))
        
        # Generate download token
        download_token = os.urandom(32).hex()
        conn.execute("UPDATE orders SET download_token=? WHERE payment_ref=?", 
                     (download_token, reference))
        
        conn.commit()
        conn.close()
        
        # Clear session
        session.pop('buying_track_id', None)
        
        print(f"Payment verified successfully! Download token: {download_token}")
        return {"success": True, "download_token": download_token}
    
    print(f"Payment verification failed: {data}")
    return {"success": False, "error": "Payment verification failed"}


# ── Manual verification page ───────────────────────────────────────────────
@payment_bp.route("/manual/<reference>")
@login_required
def manual_verify(reference):
    """Manual verification page - user can check payment status"""
    return render_template_string(PAY_STYLE + """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verify Payment — Nutifa</title>
    </head>
    <body>
        <div class="payment-card">
            <div class="logo">NUTIFA.</div>
            <h2 style="margin-bottom: 20px;">Check Payment Status</h2>
            <p style="color:#aaa; margin-bottom: 20px;">
                Your transaction reference: <strong>{{ reference }}</strong>
            </p>
            <button onclick="checkPayment()" class="paystack-btn" style="margin-top: 0;">
                🔍 Check Payment Status
            </button>
            <a href="/store" class="back-link">← Back to Store</a>
        </div>
        
        <script>
            function checkPayment() {
                fetch('/payment/check/' + '{{ reference }}', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(res => res.json()).then(data => {
                    if (data.success) {
                        window.location.href = '/payment/download-page/' + data.download_token;
                    } else {
                        alert('Payment not found or still processing. Please wait a few minutes and try again.');
                    }
                });
            }
        </script>
    </body>
    </html>
    """, reference=reference)


# ── Check payment endpoint ──────────────────────────────────────────────────
@payment_bp.route("/check/<reference>", methods=["POST"])
@login_required
def check_payment(reference):
    print(f"=== MANUAL CHECK: {reference} ===")
    
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers=headers
    )
    
    data = response.json()
    
    if data.get('status') and data['data']['status'] == 'success':
        tx = data['data']
        amount = tx['amount'] / 100
        track_id = session.get('buying_track_id')
        
        if not track_id:
            return {"success": False, "error": "No item found"}
        
        conn = get_db()
        track = conn.execute("SELECT * FROM tracks WHERE id=?", (track_id,)).fetchone()
        
        platform_cut = amount * 0.15
        artist_earnings = amount * 0.85
        
        conn.execute("""
            INSERT INTO orders (
                buyer_id, buyer_email, item_type, item_id, artist_id,
                amount, currency, platform_cut, artist_earnings,
                payment_method, payment_ref, status, paid_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'paid', datetime('now'))
        """, (
            current_user.id, tx['customer']['email'], 'track', track_id, track['artist_id'],
            amount, 'GHS', platform_cut, artist_earnings,
            'paystack', reference
        ))
        
        download_token = os.urandom(32).hex()
        conn.execute("UPDATE orders SET download_token=? WHERE payment_ref=?", 
                     (download_token, reference))
        conn.commit()
        conn.close()
        
        session.pop('buying_track_id', None)
        
        return {"success": True, "download_token": download_token}
    
    return {"success": False, "error": "Payment not found"}


# ── Success page after payment ─────────────────────────────────────────────
@payment_bp.route("/download-page/<token>")
@login_required
def download_page(token):
    conn = get_db()
    order = conn.execute("""
        SELECT o.*, t.title, t.cover_image, t.price
        FROM orders o
        JOIN tracks t ON o.item_id = t.id
        WHERE o.download_token = ? AND o.status = 'paid'
    """, (token,)).fetchone()
    conn.close()
    
    if not order:
        flash("Invalid download link", "error")
        return redirect('/store')
    
    return render_template_string(PAY_STYLE + """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Download — Nutifa</title>
    </head>
    <body>
        <div class="payment-card success-page">
            <div class="logo">NUTIFA.</div>
            <div class="checkmark">✓</div>
            <h2 style="color:#47e860;">Payment Successful!</h2>
            <div class="item-info" style="margin: 20px 0;">
                <div class="item-title">{{ order.title }}</div>
                <p style="color:#aaa; margin-top: 8px;">Thank you for your purchase!</p>
                <p style="color:#e8c547; margin-top: 8px;">Amount paid: GHS {{ "%.2f"|format(order.price) }}</p>
            </div>
            <a href="/payment/download-from-token/{{ token }}" class="download-link">
                ⬇️ Download Your Track Now
            </a>
            <p style="color:#555; font-size:0.75rem; margin-top: 20px;">
                Your download will start automatically in 3 seconds.
            </p>
            <a href="/store" class="back-link">← Continue Shopping</a>
        </div>
        
        <script>
            // Auto-download after 3 seconds
            setTimeout(function() {
                window.location.href = '/payment/download-from-token/{{ token }}';
            }, 3000);
        </script>
    </body>
    </html>
    """, order=order, token=token)


# ── Download from token (without redirect, preserves success page) ─────────
@payment_bp.route("/download-from-token/<token>")
@login_required
def download_from_token(token):
    conn = get_db()
    order = conn.execute("""
        SELECT o.*, t.file_path, t.title
        FROM orders o
        JOIN tracks t ON o.item_id = t.id
        WHERE o.download_token = ? AND o.status = 'paid'
    """, (token,)).fetchone()
    conn.close()
    
    if not order:
        flash("Invalid or expired download link", "error")
        return redirect('/store')
    
    # Increment download count
    conn = get_db()
    conn.execute("UPDATE tracks SET downloads = downloads + 1 WHERE id=?", (order['item_id'],))
    conn.commit()
    conn.close()
    
    # Serve the file
    from flask import send_from_directory
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'music')
    
    return send_from_directory(
        uploads_dir,
        order['file_path'],
        as_attachment=True,
        download_name=f"{order['title']}.mp3"
    )


# ── Initiate purchase (stores track_id in session) ─────────────────────────
@payment_bp.route("/initiate/<int:track_id>")
@login_required
def initiate_purchase(track_id):
    session['buying_track_id'] = track_id
    return redirect(url_for('payment.buy_track', track_id=track_id))


# ── Free Download (no payment needed) ──────────────────────────────────────
@payment_bp.route("/download-free/<int:track_id>")
@login_required
def download_free_track(track_id):
    conn = get_db()
    track = conn.execute("""
        SELECT t.*
        FROM tracks t
        WHERE t.id = ? AND t.price = 0 AND t.is_published = 1
    """, (track_id,)).fetchone()
    
    if not track:
        flash("Track not available for free download", "error")
        return redirect('/store')
    
    # Create order record for free download
    conn.execute("""
        INSERT INTO orders (
            buyer_id, buyer_email, item_type, item_id, artist_id,
            amount, currency, platform_cut, artist_earnings,
            payment_method, status, paid_at
        ) VALUES (?, ?, ?, ?, ?, 0, 'GHS', 0, 0, 'free', 'paid', datetime('now'))
    """, (
        current_user.id, current_user.email, 'track', track_id, track['artist_id']
    ))
    
    # Increment download count
    conn.execute("UPDATE tracks SET downloads = downloads + 1 WHERE id=?", (track_id,))
    conn.commit()
    conn.close()
    
    # Serve the file
    from flask import send_from_directory
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'music')
    
    return send_from_directory(
        uploads_dir,
        track['file_path'],
        as_attachment=True,
        download_name=f"{track['title']}.mp3"
    )