import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

try:
    from server.tax_calculator import analyze_and_compare
    from server.rag_engine import query_tax_assistant
    from server.ingest import ingest_official_docs
except ImportError:
    from tax_calculator import analyze_and_compare
    from rag_engine import query_tax_assistant
    from ingest import ingest_official_docs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "public"))

app = Flask(__name__, static_folder=PUBLIC_DIR)
CORS(app)

@app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(PUBLIC_DIR, path)):
        return send_from_directory(PUBLIC_DIR, path)
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.route("/api/calculate", methods=["POST"])
def handle_calculate():
    try:
        data = request.json or {}
        result = analyze_and_compare(data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/rag/query", methods=["POST"])
def handle_rag_query():
    try:
        data = request.json or {}
        query = data.get("query", "How can I optimize my taxes?")
        profile = data.get("profile", {})
        
        calc_result = None
        if profile and float(profile.get("gross_income", 0)) > 0:
            calc_result = analyze_and_compare(profile)
            
        result = query_tax_assistant(query, calc_result)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/ingest", methods=["POST"])
def handle_ingest():
    try:
        ingest_official_docs()
        return jsonify({"status": "success", "message": "Official tax knowledge base updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Indian Tax RAG Assistant Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
