from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return redirect("/login")

# ---------------------------
# LOGIN PAGE / API (used by login app)
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method in ("GET", "HEAD"):
        return render_template("login.html")

    try:
        data = request.get_json(silent=True) or request.form

        if not data:
            return jsonify({"status": "fail", "message": "No input"}), 400

        username = data.get("username")
        password = data.get("password")

        if username == "admin" and password == "admin":
            if request.is_json:
                return jsonify({"status": "success"})
            host = request.host.split(':')[0]
            return redirect(f"http://{host}:5001/home")

        if request.is_json:
            return jsonify({"status": "fail"})
        return render_template("login.html", message="Invalid username or password")

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------------------------
# HOME PAGE (INPUT PAGE)
# ---------------------------
@app.route("/home")
def home():
    host = request.host.split(':')[0]
    return redirect(f"http://{host}:5001/home")


# ---------------------------
# CALCULATE + RESULT PAGE
# ---------------------------
@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        l = request.form.get("length")
        b = request.form.get("breadth")
        operation = request.form.get("operation", "both")

        # safe conversion
        l = float(l) if l else 0
        b = float(b) if b else 0

        area = l * b
        perimeter = 2 * (l + b)
        result = None if operation == "both" else (area if operation == "area" else perimeter)

        return render_template(
            "result.html",
            result=result,
            area=area,
            perimeter=perimeter,
            operation=operation
        )

    except Exception as e:
        return f"Error occurred: {str(e)}"


# ---------------------------
# LOGOUT (BACK TO LOGIN APP)
# ---------------------------
@app.route("/logout")
def logout():
    return redirect("/login")


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)