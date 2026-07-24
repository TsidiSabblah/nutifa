import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Blueprint, render_template_string

legal_bp = Blueprint('legal', __name__, url_prefix='/legal')

LEGAL_STYLE = """
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
    background: #0a0a0a;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    line-height: 1.6;
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
.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 48px 32px;
}
h1 {
    color: #e8c547;
    font-size: 2rem;
    margin-bottom: 8px;
}
.updated {
    color: #666;
    font-size: 0.85rem;
    margin-bottom: 32px;
    border-bottom: 1px solid #1e1e1e;
    padding-bottom: 16px;
}
h2 {
    color: #e8c547;
    font-size: 1.3rem;
    margin: 32px 0 16px 0;
}
h3 {
    color: #ccc;
    font-size: 1.1rem;
    margin: 24px 0 12px 0;
}
p {
    margin-bottom: 16px;
    color: #bbb;
}
ul, ol {
    margin: 16px 0 16px 32px;
    color: #bbb;
}
li {
    margin: 8px 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background: #141414;
    border-radius: 8px;
    overflow: hidden;
}
th {
    background: #1a1a1a;
    padding: 12px;
    text-align: left;
    color: #e8c547;
    font-weight: 600;
}
td {
    padding: 10px 12px;
    border-bottom: 1px solid #1e1e1e;
    color: #ccc;
}
.warning-box {
    background: rgba(232, 197, 71, 0.1);
    border-left: 4px solid #e8c547;
    padding: 20px;
    margin: 24px 0;
    border-radius: 8px;
}
.warning-box strong {
    color: #e8c547;
}
footer {
    background: #111;
    border-top: 1px solid #1a1a1a;
    padding: 32px;
    text-align: center;
    color: #444;
    font-size: 0.85rem;
    margin-top: 60px;
}
footer span { color: #e8c547; }
.btn-outline {
    border: 1.5px solid #e8c547;
    color: #e8c547;
    background: transparent;
    padding: 8px 20px;
    border-radius: 6px;
    text-decoration: none;
    font-size: 0.85rem;
    transition: all 0.2s;
}
.btn-outline:hover {
    background: #e8c547;
    color: #0a0a0a;
}
</style>
"""

@legal_bp.route("/terms")
def terms():
    return render_template_string(LEGAL_STYLE + """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terms of Reference for Artists - Hajilala</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <nav>
            <a href="/" class="logo">HAJILALA.</a>
            <div class="nav-links">
                <a href="/store">Store</a>
                <a href="/legal/terms">Terms</a>
                <a href="/legal/copyright">Copyright</a>
            </div>
        </nav>
        
        <div class="container">
            <h1>Terms of Reference for Artists</h1>
            <div class="updated">Last Updated: May 2026</div>
            
            <h2>1. Artist Eligibility</h2>
            <p>To register as an artist on Hajilala, you must:</p>
            <ul>
                <li>Be at least 18 years old or have parental/guardian consent</li>
                <li>Possess a valid government-issued ID</li>
                <li>Provide accurate, verifiable personal and payment information</li>
                <li>Have a valid bank account or mobile money wallet in your legal name</li>
            </ul>
            
            <h2>2. Content Ownership and Warranty</h2>
            <p>By uploading any content, you represent and warrant that:</p>
            <ul>
                <li><strong>You are the sole owner</strong> of all rights in the content</li>
                <li><strong>You have full authority</strong> to sell and distribute the content</li>
                <li><strong>No third party</strong> has any claim over the content</li>
                <li><strong>The content does not infringe</strong> on any intellectual property rights</li>
            </ul>
            
            <h2>3. Revenue Split</h2>
            <table>
                <tr><th>Party</th><th>Percentage</th></tr>
                <tr><td>Artist</td><td><strong>85%</strong> of net sales</td></tr>
                <tr><td>Hajilala Platform</td><td><strong>15%</strong> of net sales</td></tr>
            </table>
            
            <h2>4. Prohibited Content</h2>
            <p>You may not upload content that:</p>
            <ul>
                <li>Contains unauthorized samples or derivative works</li>
                <li>Infringes on third-party intellectual property</li>
                <li>Contains hate speech or promotes illegal activities</li>
            </ul>
            
            <h2>5. Copyright Infringement</h2>
            <p>Uploading content you do not own violates Ghana copyright law and may result in:</p>
            <ul>
                <li>Civil damages up to <strong>GHS 10,000</strong> per work</li>
                <li>Criminal fines up to <strong>GHS 20,000</strong> and/or <strong>3 years imprisonment</strong></li>
                <li>Immediate account termination</li>
            </ul>
            
            <div class="warning-box">
                <strong>⚠️ Acknowledgment</strong><br><br>
                By registering as an artist, you acknowledge that you have read and agree to these Terms of Reference.
            </div>
        </div>
        
        <footer>
            <p>© 2026 <span>Hajilala</span> — Peace & Harmony 🎵 Made in Ghana</p>
        </footer>
    </body>
    </html>
    """)

@legal_bp.route("/copyright")
def copyright_page():
    return render_template_string(LEGAL_STYLE + """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Copyright Disclaimer - Hajilala</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <nav>
            <a href="/" class="logo">HAJILALA.</a>
            <div class="nav-links">
                <a href="/store">Store</a>
                <a href="/legal/terms">Terms</a>
                <a href="/legal/copyright">Copyright</a>
            </div>
        </nav>
        
        <div class="container">
            <h1>Copyright Disclaimer</h1>
            <div class="updated">Last Updated: May 2026</div>
            
            <div class="warning-box">
                <strong>⚠️ IMPORTANT</strong><br><br>
                Hajilala strictly prohibits uploading content you do not own or have permission to sell.
            </div>
            
            <h2>Legal Consequences Under Ghana Law</h2>
            <p>Under the <strong>Copyright Act of Ghana (Act 690, 2005)</strong>:</p>
            
            <table>
                <tr><th>Violation</th><th>Penalty</th></tr>
                <tr><td>Civil Liability</td><td>Damages up to <strong>GHS 10,000</strong> per work</td></tr>
                <tr><td>Criminal Offense</td><td>Fine up to <strong>GHS 20,000</strong> and/or <strong>3 years imprisonment</strong></td></tr>
                <tr><td>Account</td><td>Immediate and permanent ban from Hajilala</td></tr>
                <tr><td>Earnings</td><td>Forfeiture of proceeds from infringing content</td></tr>
            </table>
            
            <h2>Your Certification</h2>
            <p>By uploading content, you certify under penalty of perjury that:</p>
            <ul>
                <li>You are the <strong>sole and exclusive owner</strong> of the content</li>
                <li>No other person has any ownership interest</li>
                <li>You have written permission for any third-party material</li>
            </ul>
            
            <h2>Reporting Infringement</h2>
            <p>To report copyright infringement, email: <strong>copyright@hajilala.com</strong></p>
            <p>Include: identification of the copyrighted work, infringing content URL, your contact information, and a statement under penalty of perjury.</p>
            <p><strong>Hajilala responds to valid takedown notices within 48 hours.</strong></p>
            
            <div class="warning-box">
                <strong>⚠️ Warning</strong><br><br>
                Uploading content you don't own violates Ghana copyright law and may result in fines up to GHS 10,000, imprisonment, and permanent ban from Hajilala.
            </div>
        </div>
        
        <footer>
            <p>© 2026 <span>Hajilala</span> — Peace & Harmony 🎵 Made in Ghana</p>
        </footer>
    </body>
    </html>
    """)