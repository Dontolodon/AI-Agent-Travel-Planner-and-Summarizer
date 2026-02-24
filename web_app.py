import os
from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename

from modules.agent_core import summarize_file, plan_trip, maybe_send_email, export_plan_pdf, get_user_history

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
EXPORT_PDF_DIR = os.path.join(BASE_DIR, "exports", "itineraries")

ALLOWED_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}

app = Flask(__name__, template_folder="web/templates")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTS

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(EXPORT_PDF_DIR, filename, as_attachment=True)

@app.get("/history")
def history_route():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "missing ?name="}), 400
    return jsonify({"name": name, "history": get_user_history(name)})

@app.post("/summarize")
def summarize_route():
    file = request.files.get("file")
    email = request.form.get("email", "").strip()
    do_email = request.form.get("do_email") == "on"

    if not file or file.filename.strip() == "":
        return render_template("index.html", sum_error="No file uploaded."), 400
    if not allowed_file(file.filename):
        return render_template("index.html", sum_error="Unsupported file type."), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)

    try:
        result = summarize_file(path)
        if do_email and email:
            maybe_send_email(email, "Travel Summary", result)
            sum_notice = f"Summary generated and emailed to {email}."
        elif do_email and not email:
            sum_notice = "Summary generated, but email is empty."
        else:
            sum_notice = "Summary generated (not emailed)."
        return render_template("index.html", sum_result=result, sum_notice=sum_notice)
    except Exception as e:
        return render_template("index.html", sum_error=str(e)), 500

@app.post("/plan")
def plan_route():
    city = request.form.get("city", "").strip()
    start = request.form.get("start", "").strip()
    days = request.form.get("days", "").strip()

    # NEW: user_name (used for history)
    user_name = request.form.get("user_name", "").strip() or "Anonymous"

    vibe = request.form.get("vibe", "").strip()
    email = request.form.get("email", "").strip()

    do_email = request.form.get("do_email") == "on"
    fast_mode = request.form.get("fast_mode") == "on"
    export_pdf = request.form.get("export_pdf") == "on"

    if not city or not start or not days:
        return render_template("index.html", plan_error="City, start date, and days are required."), 400

    try:
        days_int = int(days)
        if days_int <= 0 or days_int > 30:
            return render_template("index.html", plan_error="Days must be between 1 and 30."), 400
    except ValueError:
        return render_template("index.html", plan_error="Days must be an integer."), 400

    try:
        if export_pdf:
            pdf_path, itinerary_text = export_plan_pdf(city, start, days_int, user_name, vibe, fast_mode)
            pdf_name = os.path.basename(pdf_path)

            if do_email and email:
                subject = f"{days_int}-Day Travel Itinerary – {city} (from {start})"
                body = itinerary_text + f"\n\nAttached: PDF itinerary with photos.\nUser: {user_name}"
                maybe_send_email(email, subject, body, attachments=[pdf_path])
                plan_notice = f"PDF generated and emailed to {email}."
            else:
                plan_notice = "PDF generated (not emailed)."

            return render_template(
                "index.html",
                plan_result=itinerary_text,
                plan_notice=plan_notice,
                pdf_link=f"/download/{pdf_name}",
            )

        itinerary_text, _ = plan_trip(city, start, days_int, user_name, vibe, fast_mode)

        if do_email and email:
            subject = f"{days_int}-Day Travel Itinerary – {city} (from {start})"
            maybe_send_email(email, subject, itinerary_text + f"\n\nUser: {user_name}")
            plan_notice = f"Itinerary generated and emailed to {email}."
        elif do_email and not email:
            plan_notice = "Itinerary generated, but email is empty."
        else:
            plan_notice = "Itinerary generated (not emailed)."

        return render_template("index.html", plan_result=itinerary_text, plan_notice=plan_notice)

    except Exception as e:
        return render_template("index.html", plan_error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
