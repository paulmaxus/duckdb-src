from flask import Flask, request, render_template, redirect, url_for, jsonify
import duckdb
import threading
import json

app = Flask(__name__)

# Create a DuckDB connection with multiple threads enabled
#con = duckdb.connect("test.duckdb")
con = duckdb.connect(":memory:")  # in-memory for now
con.execute("CREATE SEQUENCE IF NOT EXISTS seq_id START 1")  # for auto-increment
con.execute("CREATE TABLE IF NOT EXISTS staging (id INTEGER PRIMARY KEY default nextval('seq_id'), study STRING, text STRING)")
con.execute("CREATE TABLE IF NOT EXISTS validated (id INTEGER PRIMARY KEY default nextval('seq_id'), study STRING, text INTEGER)")  # int, not free text

def insert(study, text):
    """Runs the DuckDB insert in a separate thread."""
    def task():
        local_con = con.cursor()
        local_con.execute("INSERT INTO staging (study, text) VALUES (?, ?)", [study, text])
    threading.Thread(target=task).start()

def fetch():
    """Runs the DuckDB select in a separate thread and returns results."""
    results = []
    def task():
        nonlocal results
        local_con = con.cursor()
        results = local_con.execute("SELECT study, text FROM staging").df()
        results = json.dumps(results.to_dict(orient="records"))
    thread = threading.Thread(target=task)
    thread.start()
    thread.join()  # Ensure we get the results before proceeding
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    """ Renders the text submission form """
    return render_template("input.html")

@app.route("/submit", methods=["POST"])
def submit_message():    
    study, text = request.form.get("study"), request.form.get("text")
    if study and text:
        insert(study, text)  # Insert in a separate thread
    return redirect("/")

@app.route("/display", methods=["GET"])
def display_messages():
    """ Renders the page displaying all submitted messages for editing """
    table = fetch()  # Fetch in a separate thread
    return render_template("display.html", table=table)

if __name__ == "__main__":
    app.run(threaded=True)  # Use multiple threads