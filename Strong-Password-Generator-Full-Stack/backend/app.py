import os
import secrets
import string
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///passwords.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ENABLE_HISTORY"] = os.getenv("ENABLE_HISTORY", "false").lower() == "true"
db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})


class PasswordHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


def estimate_strength(password: str) -> dict:
    score = 0
    checks = {
        "length": len(password) >= 12,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "numbers": any(c.isdigit() for c in password),
        "symbols": any(c in string.punctuation for c in password),
    }
    score = sum(checks.values())
    label = "Very strong" if score == 5 and len(password) >= 16 else (
        "Strong" if score >= 4 and len(password) >= 12 else (
            "Medium" if score >= 3 else "Weak"
        )
    )
    return {"score": score, "label": label, "checks": checks}


def make_password(length: int, use_upper: bool, use_lower: bool,
                  use_numbers: bool, use_symbols: bool) -> str:
    groups = []
    if use_upper:
        groups.append(string.ascii_uppercase)
    if use_lower:
        groups.append(string.ascii_lowercase)
    if use_numbers:
        groups.append(string.digits)
    if use_symbols:
        groups.append("!@#$%^&*()-_=+[]{};:,.?")
    if not groups:
        raise ValueError("Select at least one character type.")

    # Guarantee at least one character from every selected group.
    chars = [secrets.choice(group) for group in groups]
    alphabet = "".join(groups)
    chars.extend(secrets.choice(alphabet) for _ in range(length - len(chars)))
    # secrets.SystemRandom uses the operating system's secure random source.
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "strong-password-generator"})


@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True) or {}
    try:
        length = int(data.get("length", 16))
    except (TypeError, ValueError):
        return jsonify({"error": "Length must be a whole number."}), 400
    if not 8 <= length <= 64:
        return jsonify({"error": "Password length must be between 8 and 64."}), 400

    options = {
        "use_upper": bool(data.get("uppercase", True)),
        "use_lower": bool(data.get("lowercase", True)),
        "use_numbers": bool(data.get("numbers", True)),
        "use_symbols": bool(data.get("symbols", True)),
    }
    try:
        password = make_password(length, **options)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "password": password,
        "length": len(password),
        "strength": estimate_strength(password),
    })


@app.post("/api/history")
def save_history():
    if not app.config["ENABLE_HISTORY"]:
        return jsonify({"error": "Password history is disabled. Enable it only for local demos."}), 403
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    if not isinstance(password, str) or not 8 <= len(password) <= 64:
        return jsonify({"error": "A valid generated password is required."}), 400
    db.session.add(PasswordHistory(password=password))
    db.session.commit()
    return jsonify({"message": "Saved to local demo history."}), 201


@app.get("/api/history")
def get_history():
    if not app.config["ENABLE_HISTORY"]:
        return jsonify({"error": "Password history is disabled."}), 403
    rows = PasswordHistory.query.order_by(PasswordHistory.created_at.desc()).limit(20).all()
    return jsonify([{"id": row.id, "password": row.password,
                     "created_at": row.created_at.isoformat()} for row in rows])


@app.delete("/api/history")
def clear_history():
    if not app.config["ENABLE_HISTORY"]:
        return jsonify({"error": "Password history is disabled."}), 403
    PasswordHistory.query.delete()
    db.session.commit()
    return jsonify({"message": "History cleared."})


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
