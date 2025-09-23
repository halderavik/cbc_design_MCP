import json
import subprocess
import sys


def main() -> int:
    req = {
        "jsonrpc": "2.0",
        "id": 301,
        "method": "design.generate",
        "params": {
            "method": "doptimal",
            "grid": {
                "attributes": [
                    {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                    {"name": "Size", "levels": [{"name": "S"}, {"name": "L"}]},
                ]
            },
            "options_per_screen": 2,
            "num_screens": 3,
        },
    }

    line = json.dumps(req) + "\n"
    proc = subprocess.Popen(
        [sys.executable, "-m", "conjoint_mcp.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout_data, stderr_data = proc.communicate(input=line, timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout_data, stderr_data = proc.communicate()
        print("Timed out. Stdout:\n" + (stdout_data or "") + "\nStderr:\n" + (stderr_data or ""))
        return 1

    if stderr_data:
        print("Stderr:\n" + stderr_data)
    if stdout_data:
        first_line = stdout_data.strip().splitlines()[0]
        print(first_line)
        return 0
    else:
        print("No output received from server.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
