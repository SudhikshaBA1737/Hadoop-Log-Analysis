

from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

BASE_DIR = os.path.expanduser("~/loganalysis")
HDFS_INPUT = "/user/sudhi/loganalysis/input"
HDFS_OUTPUT_DIR = "/user/sudhi/loganalysis/output/result1"
HDFS_OUTPUT = HDFS_OUTPUT_DIR + "/part-r-00000"
JAR_FILE = os.path.join(BASE_DIR, "loganalysis.jar")
INPUT_FILE = os.path.join(BASE_DIR, "access.log")

STATUS_INFO = {
    "200": "Successful Requests",
    "404": "Page Not Found",
    "500": "Internal Server Error"
}

def run_command(command):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

def analyze_logs(log_text):
    with open(INPUT_FILE, "w") as file:
        file.write(log_text.strip() + "\n")

    run_command([
        "hdfs", "dfs", "-mkdir", "-p", HDFS_INPUT
    ])

    run_command([
        "hdfs", "dfs", "-put", "-f",
        INPUT_FILE, HDFS_INPUT + "/access.log"
    ])

    run_command([
        "hdfs", "dfs", "-rm", "-r", "-f", HDFS_OUTPUT_DIR
    ])

    run_command([
        "hadoop", "jar", JAR_FILE,
        "LogAnalysis", HDFS_INPUT, HDFS_OUTPUT_DIR
    ])

def get_dashboard_data():
    result = run_command([
        "hdfs", "dfs", "-cat", HDFS_OUTPUT
    ])

    details = []
    total_requests = 0
    status_counts = []

    for line in result.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) == 2:
            status_counts.append((parts[0], int(parts[1])))
            total_requests += int(parts[1])

    for code, count in status_counts:
        details.append({
            "code": code,
            "description": STATUS_INFO.get(code, "Other Status"),
            "count": count,
            "percentage": round(count * 100 / total_requests, 1)
            if total_requests else 0
        })

    return details, total_requests, len(details)

@app.route("/", methods=["GET", "POST"])
def dashboard():
    error = None
    message = None

    if request.method == "POST":
        log_text = request.form.get("log_text", "").strip()
        uploaded_file = request.files.get("log_file")

        if uploaded_file and uploaded_file.filename:
            if not uploaded_file.filename.lower().endswith((".log", ".txt")):
                error = "Please upload a .log or .txt file."
            else:
                log_text = uploaded_file.read().decode(
                    "utf-8", errors="replace"
                ).strip()

        if not error:
            if not log_text:
                error = "Enter log entries or upload a log file."
            else:
                try:
                    analyze_logs(log_text)
                    message = "Logs processed successfully using Hadoop MapReduce."
                except Exception as e:
                    error = "Analysis failed: " + str(e)

    try:
        details, total_requests, total_status_codes = get_dashboard_data()
    except Exception as e:
        details, total_requests, total_status_codes = [], 0, 0
        if not error:
            error = "Could not read Hadoop results: " + str(e)

    return render_template(
        "index.html",
        details=details,
        total_requests=total_requests,
        total_status_codes=total_status_codes,
        error=error,
        message=message
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
