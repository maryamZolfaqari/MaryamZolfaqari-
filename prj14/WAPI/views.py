# WAPI/views.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import sqlite3
import os
import json
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "db.sqlite3")

# ----------------------------
# ایجاد جدول Users و ستون token
# ----------------------------
def ensure_users_table_and_tokens():
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        cur.execute("PRAGMA table_info(Users)")
        columns = [col[1] for col in cur.fetchall()]
        if 'token' not in columns:
            cur.execute("ALTER TABLE Users ADD COLUMN token TEXT")
        cur.execute("SELECT username, token FROM Users")
        users = cur.fetchall()
        for username, token in users:
            if not token:
                new_token = str(uuid.uuid4())
                cur.execute("UPDATE Users SET token=? WHERE username=?", (new_token, username))
        conn.commit()

ensure_users_table_and_tokens()

# ----------------------------
# Login + HTML اصلی
# ----------------------------
@csrf_exempt
def Login(request):
    if request.method == "GET":
        # فرم HTML کامل با ورود دو عدد
        html_form = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Login & Add Numbers</title>
        </head>
        <body>
        <h2>Login</h2>
        <form id="loginForm">
            Username: <input type="text" id="username"><br><br>
            Password: <input type="password" id="password"><br><br>
            <button type="submit">Login</button>
        </form>

        <div id="loginResult"></div>
        <hr>

        <div id="addNumbersSection" style="display:none;">
            <h2>Enter Two Numbers</h2>
            X: <input type="number" id="x"><br><br>
            Y: <input type="number" id="y"><br><br>
            <button id="addBtn">Calculate Sum</button>
            <div id="addResult"></div>
        </div>

        <script>
        let token = "";

        // Login
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
                document.getElementById("loginResult").innerText = JSON.stringify(data);
                if(data.status === "success"){
                    token = data.token;
                    document.getElementById("addNumbersSection").style.display = "block";
                } else {
                    token = "";
                    document.getElementById("addNumbersSection").style.display = "none";
                }
            });
        });

        // Add Numbers
        document.getElementById("addBtn").addEventListener("click", function(){
            const x = Number(document.getElementById("x").value);
            const y = Number(document.getElementById("y").value);

            if(token === ""){
                alert("You must login first!");
                return;
            }

            fetch("/AddNumbers/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": token
                },
                body: JSON.stringify({x: x, y: y})
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById("addResult").innerText = "Sum: " + data.sum;
            });
        });
        </script>
        </body>
        </html>
        """
        return HttpResponse(html_form)

    # POST Login
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                return JsonResponse({"status": "failed", "message": "Username and password required"})
        except Exception:
            return JsonResponse({"status": "failed", "message": "Invalid JSON"})

        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM Users WHERE username=? AND password=?", (username, password))
                count = cur.fetchone()[0]
                if count == 1:
                    token = str(uuid.uuid4())
                    cur.execute("UPDATE Users SET token=? WHERE username=?", (token, username))
                    conn.commit()
                    return JsonResponse({"status": "success", "message": "Login OK", "token": token})
                else:
                    return JsonResponse({"status": "failed", "message": "Invalid credentials"})
        except Exception as e:
            return JsonResponse({"status": "failed", "message": str(e)})

# ----------------------------
# AddNumbers view
# ----------------------------
@csrf_exempt

def AddNumbers(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    token = request.headers.get("Authorization")
    if not token:
        return JsonResponse({"error": "Token required"}, status=401)

    # اعتبارسنجی توکن
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT username FROM Users WHERE token=?", (token,))
        user = cur.fetchone()
        if not user:
            return JsonResponse({"error": "Invalid token"}, status=403)

    # دریافت پارامترهای x و y از URL
    try:
        x = request.GET.get("x")
        y = request.GET.get("y")
        if x is None or y is None:
            return JsonResponse({"error": "x and y required"})
        x = float(x)
        y = float(y)
        result = x + y
    except Exception:
        return JsonResponse({"error": "Invalid values"})

    return JsonResponse({"user": user[0], "x": x, "y": y, "sum": result})

