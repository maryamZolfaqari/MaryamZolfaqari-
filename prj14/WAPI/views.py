from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import sqlite3
import os
import json

# مسیر دیتابیس sqlite (db.sqlite3 در فولدر پروژه)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

# این تابع فقط یک بار جدول Users را ایجاد می‌کند (در صورت نیاز)
def ensure_users_table():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

# فراخوانی یک بار هنگام import
ensure_users_table()

@csrf_exempt
def Login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    # دریافت JSON از body
    try:
        data = json.loads(request.body.decode("utf-8"))
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return JsonResponse({"status": "failed", "message": "Username and password required"})
    except Exception:
        return JsonResponse({"status": "failed", "message": "Invalid JSON"})

    # بررسی اعتبار کاربر
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Users WHERE username=? AND password=?", (username, password))
            count = cur.fetchone()[0]
    except Exception as e:
        return JsonResponse({"status": "failed", "message": "Database error: {}".format(str(e))})

    if count == 1:
        return JsonResponse({"status": "success", "message": "Login OK"})
    else:
        return JsonResponse({"status": "failed", "message": "Invalid credentials"})
# WAPI/views.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "db.sqlite3")

@csrf_exempt
def Login(request):
    if request.method == "GET":
        # برگرداندن HTML فرم
        html_form = """
        <!DOCTYPE html>
        <html lang="en">
        <head><meta charset="UTF-8"><title>Login</title></head>
        <body>
        <h2>Login Test</h2>
        <form id="loginForm">
            <label>Username: <input type="text" id="username"></label><br><br>
            <label>Password: <input type="password" id="password"></label><br><br>
            <button type="submit">Login</button>
        </form>
        <div id="result"></div>
        <script>
        document.getElementById("loginForm").addEventListener("submit", function(e){
            e.preventDefault();
            fetch("/Login/", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    username: document.getElementById("username").value,
                    password: document.getElementById("password").value
                })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById("result").innerText = JSON.stringify(data);
            });
        });
        </script>
        </body>
        </html>
        """
        return HttpResponse(html_form)

    # POST JSON
    try:
        data = json.loads(request.body.decode("utf-8"))
        username = data.get("username")
        password = data.get("password")
    except Exception:
        return JsonResponse({"status": "failed", "message": "Invalid JSON"})

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Users (username TEXT, password TEXT)")
    cur.execute("SELECT COUNT(*) FROM Users WHERE username=? AND password=?", (username, password))
    count = cur.fetchone()[0]
    conn.close()

    if count == 1:
        return JsonResponse({"status": "success", "message": "Login OK"})
    else:
        return JsonResponse({"status": "failed", "message": "Invalid credentials"})
