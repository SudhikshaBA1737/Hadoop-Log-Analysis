
from flask import Flask, render_template
import subprocess

app = Flask(__name__)

HDFS_OUTPUT = "/user/sudhi/loganalysis/output/result1/part-r-00000"

STATUS_INFO = {
    "200": "Successful Requests",
    "404": "Page Not Found",
    "500": "Internal Server Error"
}

@app.route("/")
def dashboard():
    try:
        result = subprocess.run(
            ["hdfs", "dfs", "-cat", HDFS_OUTPUT],
            capture_output=True,
            text=True,
            check=True
        )

        status_codes = []
        counts = []

        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) == 2:
                status_codes.append(parts[0])
                counts.append(int(parts[1]))

        total_requests = sum(counts)
        details = []

        for code, count in zip(status_codes, counts):
            details.append({
                "code": code,
                "description": STATUS_INFO.get(code, "Other Status"),
                "count": count,
                "percentage": round(count * 100 / total_requests, 1)
                if total_requests else 0
            })

        return render_template(
            "index.html",
            details=details,
            total_requests=total_requests,
            total_status_codes=len(status_codes),
            error=None
        )

    except Exception as e:
        return render_template(
            "index.html",
            details=[],
            total_requests=0,
            total_status_codes=0,
            error=str(e)
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
