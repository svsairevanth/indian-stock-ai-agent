"""
Web server for stock chat app with auth, SQLite persistence, and admin dashboard APIs.
"""

import asyncio
import hashlib
import json
import os
import re
import secrets
import sqlite3
import threading
import traceback
import uuid
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from agents.pipeline_orchestrator import run_full_analysis_with_pdf
from config import OPENAI_API_KEY, PDF_OUTPUT_DIR, EXA_MCP_HTTP_URL
from main import extract_stock_symbol


ROOT_DIR = Path(__file__).resolve().parent
CHAT_HTML_PATH = ROOT_DIR / "chat.html"
INDEX_HTML_PATH = ROOT_DIR / "index.html"
REPORTS_DIR = Path(PDF_OUTPUT_DIR).resolve()
DB_PATH = ROOT_DIR / "app_data.db"
SESSION_COOKIE = "stock_session"
SESSION_DAYS = 7
PASSWORD_ITERATIONS = 240000
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")
JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_ts(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat()


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return digest.hex()


def create_password(password: str) -> tuple[str, str]:
    salt_hex = secrets.token_hex(16)
    return hash_password(password, salt_hex), salt_hex


def verify_password(password: str, password_hash: str, salt_hex: str) -> bool:
    return secrets.compare_digest(hash_password(password, salt_hex), password_hash)


def extract_pdf_path(result_text: str) -> str | None:
    match = re.search(r"PDF Report generated:\s*(.+)", result_text)
    return match.group(1).strip() if match else None


def extract_recommendation(result_text: str) -> tuple[str | None, int | None]:
    match = re.search(r"Recommendation:\s*(BUY|SELL|HOLD)\s*\(Confidence:\s*(\d+)%\)", result_text)
    if not match:
        return None, None
    return match.group(1), int(match.group(2))


def ensure_schema() -> None:
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
                created_at TEXT NOT NULL,
                last_login TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                stock_symbol TEXT,
                recommendation TEXT,
                confidence INTEGER,
                pdf_filename TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pdf_filename TEXT NOT NULL,
                pdf_path TEXT NOT NULL,
                stock_symbol TEXT,
                recommendation TEXT,
                confidence INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )

        admin_count = conn.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'admin'").fetchone()["c"]
        if admin_count == 0:
            admin_user = os.getenv("ADMIN_USERNAME", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            pwd_hash, salt = create_password(admin_password)
            conn.execute(
                """
                INSERT INTO users (username, password_hash, salt, role, created_at)
                VALUES (?, ?, ?, 'admin', ?)
                """,
                (admin_user, pwd_hash, salt, iso_ts()),
            )
            print(f"[BOOTSTRAP] Admin account created: username='{admin_user}'")
            if admin_password == "admin123":
                print("[BOOTSTRAP] ADMIN_PASSWORD not set; default password is 'admin123'. Change it immediately.")


def delete_expired_sessions() -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (iso_ts(),))


def prompt_examples() -> list[str]:
    return [
        "Create a swing-trade report for RELIANCE with entry, target, and stop-loss.",
        "I hold TCS from 3500. Should I hold, add, or exit in the next 3 months?",
        "Compare INFY and HCLTECH for long-term SIP-style accumulation.",
        "Generate a risk-first report for SBIN for short-term trading.",
        "Use live Exa web research and give me a catalyst + risk report for ITC.",
        "Analyze HDFCBANK and create a PDF I can share with my team.",
        "Give a conservative BUY/SELL/HOLD report for ITC with confidence score.",
    ]


def is_openai_key_set() -> bool:
    key = (OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")).strip()
    return bool(key)


class StockChatHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = HTTPStatus.OK, extra_headers: dict | None = None):
        body = json.dumps(payload).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            if extra_headers:
                for k, v in extra_headers.items():
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    def _send_html_file(self, file_path: Path):
        if not file_path.exists():
            self._send_json({"error": "chat.html not found"}, status=HTTPStatus.NOT_FOUND)
            return

        body = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_pdf_file(self, file_path: Path):
        if not file_path.exists() or not file_path.is_file():
            self._send_json({"error": "Report file not found"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            body = file_path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'inline; filename="{file_path.name}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    def _read_json_body(self) -> dict | None:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            self._send_json({"error": "Empty request body"}, status=HTTPStatus.BAD_REQUEST)
            return None

        try:
            raw = self.rfile.read(content_length).decode("utf-8")
            return json.loads(raw)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body"}, status=HTTPStatus.BAD_REQUEST)
            return None

    def _cookie_value(self, key: str) -> str | None:
        raw = self.headers.get("Cookie")
        if not raw:
            return None
        cookie = SimpleCookie()
        cookie.load(raw)
        morsel = cookie.get(key)
        return morsel.value if morsel else None

    def _build_session_cookie(self, token: str | None, max_age: int = 0) -> str:
        cookie = SimpleCookie()
        cookie[SESSION_COOKIE] = token or ""
        cookie[SESSION_COOKIE]["path"] = "/"
        cookie[SESSION_COOKIE]["httponly"] = True
        cookie[SESSION_COOKIE]["samesite"] = "Lax"
        cookie[SESSION_COOKIE]["max-age"] = str(max_age)
        return cookie.output(header="").strip()

    def _session_user(self) -> sqlite3.Row | None:
        token = self._cookie_value(SESSION_COOKIE)
        if not token:
            return None

        with get_db() as conn:
            row = conn.execute(
                """
                SELECT u.id, u.username, u.role
                FROM sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token = ? AND s.expires_at > ?
                """,
                (token, iso_ts()),
            ).fetchone()
            return row

    def _require_auth(self) -> sqlite3.Row | None:
        user = self._session_user()
        if not user:
            self._send_json({"error": "Authentication required"}, status=HTTPStatus.UNAUTHORIZED)
            return None
        return user

    def _require_admin(self) -> sqlite3.Row | None:
        user = self._require_auth()
        if not user:
            return None
        if user["role"] != "admin":
            self._send_json({"error": "Admin access required"}, status=HTTPStatus.FORBIDDEN)
            return None
        return user

    def _create_session(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        now = utc_now()
        expires = now + timedelta(days=SESSION_DAYS)
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO sessions (token, user_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (token, user_id, iso_ts(now), iso_ts(expires)),
            )
        return token

    def _handle_register(self):
        payload = self._read_json_body()
        if payload is None:
            return

        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", "")).strip()

        if not USERNAME_RE.fullmatch(username):
            self._send_json({"error": "Username must be 3-32 chars, letters/numbers/underscore only"}, status=HTTPStatus.BAD_REQUEST)
            return
        if len(password) < 8:
            self._send_json({"error": "Password must be at least 8 characters"}, status=HTTPStatus.BAD_REQUEST)
            return

        pwd_hash, salt = create_password(password)
        now = iso_ts()
        try:
            with get_db() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO users (username, password_hash, salt, role, created_at)
                    VALUES (?, ?, ?, 'user', ?)
                    """,
                    (username, pwd_hash, salt, now),
                )
                user_id = cur.lastrowid
            session_token = self._create_session(user_id)
            self._send_json(
                {
                    "success": True,
                    "user": {"id": user_id, "username": username, "role": "user"},
                },
                extra_headers={"Set-Cookie": self._build_session_cookie(session_token, max_age=SESSION_DAYS * 86400)},
            )
        except sqlite3.IntegrityError:
            self._send_json({"error": "Username already exists"}, status=HTTPStatus.CONFLICT)

    def _handle_login(self):
        payload = self._read_json_body()
        if payload is None:
            return

        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", "")).strip()
        if not username or not password:
            self._send_json({"error": "Username and password are required"}, status=HTTPStatus.BAD_REQUEST)
            return

        with get_db() as conn:
            user = conn.execute(
                "SELECT id, username, password_hash, salt, role FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if not user or not verify_password(password, user["password_hash"], user["salt"]):
                self._send_json({"error": "Invalid credentials"}, status=HTTPStatus.UNAUTHORIZED)
                return

            conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (iso_ts(), user["id"]))

        session_token = self._create_session(user["id"])
        self._send_json(
            {
                "success": True,
                "user": {"id": user["id"], "username": user["username"], "role": user["role"]},
            },
            extra_headers={"Set-Cookie": self._build_session_cookie(session_token, max_age=SESSION_DAYS * 86400)},
        )

    def _handle_logout(self):
        token = self._cookie_value(SESSION_COOKIE)
        if token:
            with get_db() as conn:
                conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        self._send_json(
            {"success": True},
            extra_headers={"Set-Cookie": self._build_session_cookie(None, max_age=0)},
        )

    def _handle_chat(self):
        user = self._require_auth()
        if not user:
            return

        if not is_openai_key_set():
            self._send_json(
                {
                    "error": "OPENAI_API_KEY is not configured. Set it in environment or .env and restart the server.",
                },
                status=HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        payload = self._read_json_body()
        if payload is None:
            return

        query = str(payload.get("message", "")).strip()
        if not query:
            self._send_json({"error": "Field 'message' is required"}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            stock_symbol = extract_stock_symbol(query)
            result_text = asyncio.run(run_full_analysis_with_pdf(stock_symbol, query))
            pdf_path = extract_pdf_path(result_text)
            recommendation, confidence = extract_recommendation(result_text)
            pdf_filename = Path(pdf_path).name if pdf_path else None
            pdf_url = f"/reports/{pdf_filename}" if pdf_filename else None

            with get_db() as conn:
                conn.execute(
                    """
                    INSERT INTO chat_history
                    (user_id, prompt, response, stock_symbol, recommendation, confidence, pdf_filename, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user["id"],
                        query,
                        result_text,
                        stock_symbol,
                        recommendation,
                        confidence,
                        pdf_filename,
                        iso_ts(),
                    ),
                )

                if pdf_filename and pdf_path:
                    conn.execute(
                        """
                        INSERT INTO reports
                        (user_id, pdf_filename, pdf_path, stock_symbol, recommendation, confidence, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            user["id"],
                            pdf_filename,
                            str(pdf_path),
                            stock_symbol,
                            recommendation,
                            confidence,
                            iso_ts(),
                        ),
                    )

            self._send_json(
                {
                    "success": True,
                    "query": query,
                    "stock_symbol": stock_symbol,
                    "analysis": result_text,
                    "pdf_path": pdf_path,
                    "pdf_url": pdf_url,
                    "recommendation": recommendation,
                    "confidence": confidence,
                }
            )
        except Exception as exc:
            traceback.print_exc()
            message = str(exc)
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            if "model_not_found" in message or "does not have access to model" in message:
                status = HTTPStatus.BAD_GATEWAY
                message = (
                    "Model access denied for current MODEL_NAME. "
                    "Set a model your project can access (for example in .env: MODEL_NAME=gpt-4o-mini) "
                    "and restart the server."
                )
            elif "0/10 agents succeeded" in message:
                status = HTTPStatus.BAD_GATEWAY

            self._send_json({"success": False, "error": message}, status=status)

    def _create_job(self, user_id: int, query: str, stock_symbol: str) -> str:
        job_id = uuid.uuid4().hex
        with JOBS_LOCK:
            JOBS[job_id] = {
                "job_id": job_id,
                "user_id": user_id,
                "query": query,
                "stock_symbol": stock_symbol,
                "status": "queued",
                "current_message": "Queued",
                "events": [],
                "result": None,
                "error": None,
                "created_at": iso_ts(),
                "updated_at": iso_ts(),
            }
        return job_id

    def _append_job_event(self, job_id: str, event: dict):
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            entry = {
                "at": iso_ts(),
                "stage": event.get("stage", ""),
                "step": event.get("step", ""),
                "message": event.get("message", ""),
            }
            job["events"].append(entry)
            job["current_message"] = entry["message"] or job["current_message"]
            job["updated_at"] = iso_ts()
            if len(job["events"]) > 100:
                job["events"] = job["events"][-100:]

    def _set_job_status(self, job_id: str, status: str, error: str | None = None, result: dict | None = None):
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            job["status"] = status
            job["error"] = error
            job["result"] = result
            job["updated_at"] = iso_ts()

    def _run_job_worker(self, job_id: str):
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            user_id = job["user_id"]
            query = job["query"]
            stock_symbol = job["stock_symbol"]
            job["status"] = "running"
            job["current_message"] = "Starting analysis"
            job["updated_at"] = iso_ts()

        def progress_callback(event: dict):
            self._append_job_event(job_id, event)

        try:
            result_text = asyncio.run(
                run_full_analysis_with_pdf(
                    stock_symbol,
                    query,
                    progress_callback=progress_callback,
                )
            )
            pdf_path = extract_pdf_path(result_text)
            recommendation, confidence = extract_recommendation(result_text)
            pdf_filename = Path(pdf_path).name if pdf_path else None
            pdf_url = f"/reports/{pdf_filename}" if pdf_filename else None

            with get_db() as conn:
                conn.execute(
                    """
                    INSERT INTO chat_history
                    (user_id, prompt, response, stock_symbol, recommendation, confidence, pdf_filename, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        query,
                        result_text,
                        stock_symbol,
                        recommendation,
                        confidence,
                        pdf_filename,
                        iso_ts(),
                    ),
                )

                if pdf_filename and pdf_path:
                    conn.execute(
                        """
                        INSERT INTO reports
                        (user_id, pdf_filename, pdf_path, stock_symbol, recommendation, confidence, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            pdf_filename,
                            str(pdf_path),
                            stock_symbol,
                            recommendation,
                            confidence,
                            iso_ts(),
                        ),
                    )

            result = {
                "success": True,
                "query": query,
                "stock_symbol": stock_symbol,
                "analysis": result_text,
                "pdf_path": pdf_path,
                "pdf_url": pdf_url,
                "recommendation": recommendation,
                "confidence": confidence,
            }
            self._set_job_status(job_id, "done", result=result)
        except Exception as exc:
            message = str(exc)
            if "model_not_found" in message or "does not have access to model" in message:
                message = (
                    "Model access denied for current MODEL_NAME. "
                    "Set a model your project can access and restart the server."
                )
            self._set_job_status(job_id, "failed", error=message)

    def _handle_chat_start(self):
        user = self._require_auth()
        if not user:
            return

        if not is_openai_key_set():
            self._send_json(
                {"error": "OPENAI_API_KEY is not configured. Set it in environment or .env and restart the server."},
                status=HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        payload = self._read_json_body()
        if payload is None:
            return

        query = str(payload.get("message", "")).strip()
        if not query:
            self._send_json({"error": "Field 'message' is required"}, status=HTTPStatus.BAD_REQUEST)
            return

        stock_symbol = extract_stock_symbol(query)
        job_id = self._create_job(user["id"], query, stock_symbol)
        thread = threading.Thread(target=self._run_job_worker, args=(job_id,), daemon=True)
        thread.start()
        self._send_json({"success": True, "job_id": job_id, "stock_symbol": stock_symbol})

    def _handle_chat_status(self, parsed_query: str):
        user = self._require_auth()
        if not user:
            return

        params = parse_qs(parsed_query)
        job_id = (params.get("job_id") or [None])[0]
        if not job_id:
            self._send_json({"error": "job_id query parameter is required"}, status=HTTPStatus.BAD_REQUEST)
            return

        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if not job:
                self._send_json({"error": "Job not found"}, status=HTTPStatus.NOT_FOUND)
                return
            if user["role"] != "admin" and job["user_id"] != user["id"]:
                self._send_json({"error": "Not allowed to access this job"}, status=HTTPStatus.FORBIDDEN)
                return
            payload = {
                "success": True,
                "job_id": job_id,
                "status": job["status"],
                "current_message": job["current_message"],
                "events": job["events"],
                "error": job["error"],
                "result": job["result"],
                "created_at": job["created_at"],
                "updated_at": job["updated_at"],
            }
        self._send_json(payload)

    def _handle_chats_list(self):
        user = self._require_auth()
        if not user:
            return

        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT id, prompt, stock_symbol, recommendation, confidence, pdf_filename, created_at
                FROM chat_history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 200
                """,
                (user["id"],),
            ).fetchall()

        items = []
        for row in rows:
            items.append(
                {
                    "id": row["id"],
                    "prompt": row["prompt"],
                    "stock_symbol": row["stock_symbol"],
                    "recommendation": row["recommendation"],
                    "confidence": row["confidence"],
                    "created_at": row["created_at"],
                    "pdf_url": f"/reports/{row['pdf_filename']}" if row["pdf_filename"] else None,
                }
            )
        self._send_json({"success": True, "items": items})

    def _handle_reports_list(self):
        user = self._require_auth()
        if not user:
            return

        with get_db() as conn:
            if user["role"] == "admin":
                rows = conn.execute(
                    """
                    SELECT r.id, r.pdf_filename, r.stock_symbol, r.recommendation, r.confidence, r.created_at, u.username
                    FROM reports r
                    JOIN users u ON u.id = r.user_id
                    ORDER BY r.id DESC
                    LIMIT 300
                    """
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT r.id, r.pdf_filename, r.stock_symbol, r.recommendation, r.confidence, r.created_at, u.username
                    FROM reports r
                    JOIN users u ON u.id = r.user_id
                    WHERE r.user_id = ?
                    ORDER BY r.id DESC
                    LIMIT 300
                    """,
                    (user["id"],),
                ).fetchall()

        items = []
        for row in rows:
            items.append(
                {
                    "id": row["id"],
                    "filename": row["pdf_filename"],
                    "stock_symbol": row["stock_symbol"],
                    "recommendation": row["recommendation"],
                    "confidence": row["confidence"],
                    "created_at": row["created_at"],
                    "owner": row["username"],
                    "url": f"/reports/{row['pdf_filename']}",
                }
            )
        self._send_json({"success": True, "items": items})

    def _handle_admin_stats(self):
        _ = self._require_admin()
        if not _:
            return

        with get_db() as conn:
            totals = conn.execute(
                """
                SELECT
                  (SELECT COUNT(*) FROM users) AS total_users,
                  (SELECT COUNT(*) FROM users WHERE role='admin') AS total_admins,
                  (SELECT COUNT(*) FROM reports) AS total_reports,
                  (SELECT COUNT(*) FROM chat_history) AS total_chats,
                  (SELECT COUNT(*) FROM users WHERE last_login >= ?) AS active_users_7d
                """,
                (iso_ts(utc_now() - timedelta(days=7)),),
            ).fetchone()

            top_symbols = conn.execute(
                """
                SELECT stock_symbol, COUNT(*) AS c
                FROM reports
                WHERE stock_symbol IS NOT NULL AND stock_symbol <> ''
                GROUP BY stock_symbol
                ORDER BY c DESC
                LIMIT 5
                """
            ).fetchall()

        self._send_json(
            {
                "success": True,
                "stats": {
                    "total_users": totals["total_users"],
                    "total_admins": totals["total_admins"],
                    "total_reports": totals["total_reports"],
                    "total_chats": totals["total_chats"],
                    "active_users_7d": totals["active_users_7d"],
                },
                "top_symbols": [{"symbol": row["stock_symbol"], "count": row["c"]} for row in top_symbols],
            }
        )

    def _handle_admin_users(self):
        _ = self._require_admin()
        if not _:
            return

        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT
                  u.id,
                  u.username,
                  u.role,
                  u.created_at,
                  u.last_login,
                  (SELECT COUNT(*) FROM reports r WHERE r.user_id = u.id) AS reports_count,
                  (SELECT COUNT(*) FROM chat_history c WHERE c.user_id = u.id) AS chats_count
                FROM users u
                ORDER BY u.id DESC
                LIMIT 300
                """
            ).fetchall()

        items = []
        for row in rows:
            items.append(
                {
                    "id": row["id"],
                    "username": row["username"],
                    "role": row["role"],
                    "created_at": row["created_at"],
                    "last_login": row["last_login"],
                    "reports_count": row["reports_count"],
                    "chats_count": row["chats_count"],
                }
            )
        self._send_json({"success": True, "items": items})

    def _handle_report_download(self, filename: str):
        user = self._require_auth()
        if not user:
            return

        with get_db() as conn:
            row = conn.execute(
                """
                SELECT user_id, pdf_filename
                FROM reports
                WHERE pdf_filename = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (filename,),
            ).fetchone()

        if not row:
            self._send_json({"error": "Report metadata not found"}, status=HTTPStatus.NOT_FOUND)
            return

        if user["role"] != "admin" and row["user_id"] != user["id"]:
            self._send_json({"error": "You are not allowed to access this report"}, status=HTTPStatus.FORBIDDEN)
            return

        safe_path = (REPORTS_DIR / filename).resolve()
        if REPORTS_DIR not in safe_path.parents and safe_path != REPORTS_DIR:
            self._send_json({"error": "Invalid report path"}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_pdf_file(safe_path)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/index.html":
            self._send_html_file(INDEX_HTML_PATH)
            return

        if path in ("/", "/chat.html"):
            self._send_html_file(CHAT_HTML_PATH)
            return

        if path == "/health":
            self._send_json(
                {
                    "status": "ok",
                    "db_path": str(DB_PATH),
                    "reports_dir": str(REPORTS_DIR),
                    "openai_key_set": is_openai_key_set(),
                    "exa_mcp_configured": bool(EXA_MCP_HTTP_URL),
                    "exa_mcp_url": EXA_MCP_HTTP_URL,
                }
            )
            return

        if path == "/api/prompt-examples":
            self._send_json({"success": True, "items": prompt_examples()})
            return

        if path == "/api/me":
            user = self._session_user()
            if not user:
                self._send_json({"authenticated": False})
                return
            self._send_json(
                {
                    "authenticated": True,
                    "user": {"id": user["id"], "username": user["username"], "role": user["role"]},
                }
            )
            return

        if path == "/api/chats":
            self._handle_chats_list()
            return

        if path == "/api/reports":
            self._handle_reports_list()
            return

        if path == "/api/admin/stats":
            self._handle_admin_stats()
            return

        if path == "/api/admin/users":
            self._handle_admin_users()
            return

        if path == "/api/chat/status":
            self._handle_chat_status(parsed.query)
            return

        if path.startswith("/reports/"):
            filename = unquote(path[len("/reports/"):]).strip()
            self._handle_report_download(filename)
            return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/register":
            self._handle_register()
            return
        if path == "/api/login":
            self._handle_login()
            return
        if path == "/api/logout":
            self._handle_logout()
            return
        if path == "/api/chat":
            self._handle_chat()
            return
        if path == "/api/chat/start":
            self._handle_chat_start()
            return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)


def run_server(host: str = "127.0.0.1", port: int = 8000):
    ensure_schema()
    delete_expired_sessions()
    server = ThreadingHTTPServer((host, port), StockChatHandler)
    print(f"Server running at http://{host}:{port}")
    print("Open / in your browser to use the chat app.")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
