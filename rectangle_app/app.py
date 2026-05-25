from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__)

# ---------------------------
# LOGIN PAGE / API
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method in ("GET", "HEAD"):
        return render_template("login.html")

    try:
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({"status": "fail", "message": "No data received"}), 400

        username = data.get("username")
        password = data.get("password")

        if username == "admin" and password == "admin":
            if request.is_json:
                return jsonify({"status": "success"})
            return redirect("/home")

        if request.is_json:
            return jsonify({"status": "fail"})
        return render_template("login.html", message="Invalid username or password")

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------------------------
# HOME PAGE (INPUT PAGE)
# ---------------------------
@app.route("/")
def index():
    return redirect("/login")

@app.route("/home")
def home():
    return render_template("home.html")


# ---------------------------
# CALCULATE + RESULT PAGE (NEW PAGE)
# ---------------------------
@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        length = request.form.get("length")
        breadth = request.form.get("breadth")
        operation = request.form.get("operation", "area")

        length = float(length) if length else 0
        breadth = float(breadth) if breadth else 0

        area = length * breadth
        perimeter = 2 * (length + breadth)

        result = area if operation == "area" else perimeter

        return render_template(
            "result.html",
            result=result,
            operation=operation
        )

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------------------
# LOGOUT (BACK TO LOGIN APP)
# ---------------------------
@app.route("/logout")
def logout():
    host = request.host.split(':')[0]
    return redirect(f"http://{host}:5000/login")
    # For EC2 deployment with an external login app, update the URL below.
    # return redirect("http://35.180.199.56:5000/login")


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)