import os
import threading

from dotenv import load_dotenv

load_dotenv()

_oracledb = None
_cx_oracle = None
_pool = None
_pool_lock = threading.Lock()

try:
    import oracledb as _oracledb
except ImportError:
    _oracledb = None

try:
    import cx_Oracle as _cx_oracle
except ImportError:
    _cx_oracle = None


def _connection_params():
    return {
        "user": os.getenv("ORA_USER", "system"),
        "password": os.getenv("ORA_PASSWORD", ""),
        "host": os.getenv("ORA_HOST", "localhost"),
        "port": int(os.getenv("ORA_PORT", "1521")),
        "sid": os.getenv("ORA_SID", "XE"),
        "service_name": os.getenv("ORA_SERVICE_NAME", "").strip(),
    }


def _make_dsn(params, driver):
    if params["service_name"]:
        return driver.makedsn(
            params["host"],
            params["port"],
            service_name=params["service_name"],
        )
    return driver.makedsn(params["host"], params["port"], sid=params["sid"])


def _pool_config():
    return {
        "min": int(os.getenv("ORA_POOL_MIN", "2")),
        "max": int(os.getenv("ORA_POOL_MAX", "10")),
        "increment": int(os.getenv("ORA_POOL_INCREMENT", "1")),
    }


def _create_pool():
    params = _connection_params()
    cfg = _pool_config()

    if _oracledb is not None:
        dsn = _make_dsn(params, _oracledb)
        return _oracledb.create_pool(
            user=params["user"],
            password=params["password"],
            dsn=dsn,
            min=cfg["min"],
            max=cfg["max"],
            increment=cfg["increment"],
        )

    if _cx_oracle is not None:
        dsn = _make_dsn(params, _cx_oracle)
        return _cx_oracle.SessionPool(
            user=params["user"],
            password=params["password"],
            dsn=dsn,
            min=cfg["min"],
            max=cfg["max"],
            increment=cfg["increment"],
            threaded=True,
        )

    raise RuntimeError(
        "No Oracle driver found. Install with: pip install oracledb"
    )


def get_pool():
    """Return the shared connection pool (lazy init, thread-safe)."""
    global _pool
    if _pool is not None:
        return _pool
    with _pool_lock:
        if _pool is None:
            _pool = _create_pool()
    return _pool


def get_connection():
    """
    Acquire a connection from the pool. Call conn.close() when done —
    that returns the connection to the pool (does not destroy it).
    """
    return get_pool().acquire()


def close_pool():
    """Release the pool (tests / graceful shutdown)."""
    global _pool
    with _pool_lock:
        if _pool is not None:
            _pool.close()
            _pool = None
