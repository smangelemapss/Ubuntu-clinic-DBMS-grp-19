import json
import os
import time

_ENABLED = os.getenv("DEBUG_LOG", "").lower() in ("1", "true", "yes")
_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "debug-b3fe85.log",
)


def debug_log(location, message, data=None, hypothesis_id="H0", run_id="pre-fix"):
    if not _ENABLED:
        return
    try:
        payload = {
            "sessionId": "b3fe85",
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000),
        }
        with open(_LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
    except OSError:
        pass
