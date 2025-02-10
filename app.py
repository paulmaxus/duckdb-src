from flask import Flask, request, render_template_string
import duckdb
import threading

app = Flask(__name__)

# Create a DuckDB connection with multiple threads enabled
con = duckdb.connect("test.duckdb")
con.execute("CREATE SEQUENCE IF NOT EXISTS seq_id START 1")  # for auto-increment
con.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY default nextval('seq_id'), text STRING)")

# HTML templates (simplified for quick testing)
HTML_FORM = """
<!doctype html>
<html>
    <body>
        <h2>Enter a Message</h2>
        <form method="post">
            <input type="text" name="message" required>
            <button type="submit">Submit</button>
        </form>
        <br>
        <a href="/view">View Messages</a>
    </body>
</html>
"""

HTML_VIEW = """
<!doctype html>
<html>
    <body>
        <h2>Stored Messages</h2>
        <ul>
            {% for msg in messages %}
                <li>{{ msg }}</li>
            {% endfor %}
        </ul>
        <br>
        <a href="/">Go Back</a>
    </body>
</html>
"""

def insert_message(message):
    """Runs the DuckDB insert in a separate thread."""
    def task():
        local_con = con.cursor()
        local_con.execute("INSERT INTO messages (text) VALUES (?)", [message])
    threading.Thread(target=task).start()

def fetch_messages():
    """Runs the DuckDB select in a separate thread and returns results."""
    results = []
    def task():
        nonlocal results
        local_con = con.cursor()
        results = local_con.execute("SELECT text FROM messages").fetchall()
    thread = threading.Thread(target=task)
    thread.start()
    thread.join()  # Ensure we get the results before proceeding
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        message = request.form.get("message")
        if message:
            insert_message(message)  # Insert in a separate thread
    return render_template_string(HTML_FORM)

@app.route("/view")
def view():
    messages = fetch_messages()  # Fetch in a separate thread
    return render_template_string(HTML_VIEW, messages=[msg[0] for msg in messages])

if __name__ == "__main__":
    app.run(threaded=True)  # Use multiple threads