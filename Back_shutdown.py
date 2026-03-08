import json
import os
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "create.json")

TASK_PREFIX = "PY_SHUTDOWN_"
NOTIFY_TASK_NAME = "PY_SHUTDOWN_NOTIFY_ON_LOGON"

DATE_FMT_DB = "%Y-%m-%d %H:%M:%S"


@dataclass
class TaskRecord:
    task_name: str
    kind: str  # once_datetime | in_hours | daily | hourly
    created_at: str
    schedule_at: Optional[str]  # for once/derived
    detail: Dict[str, Any]


def _run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, shell=False)


def _ensure_db() -> None:
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({"tasks": []}, f, ensure_ascii=False, indent=2)


def _load_db() -> Dict[str, Any]:
    _ensure_db()
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(data: Dict[str, Any]) -> None:
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _now_str() -> str:
    return datetime.now().strftime(DATE_FMT_DB)


def _sanitize_task_name(name: str) -> str:
    safe = []
    for ch in name:
        if ch.isalnum() or ch in ("_", "-", "."):
            safe.append(ch)
        else:
            safe.append("_")
    out = "".join(safe).strip("_")
    return out or "task"


def _make_task_name(base: str) -> str:
    base = _sanitize_task_name(base)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{TASK_PREFIX}{base}_{stamp}"


def _format_windows_date(dt: datetime) -> str:
    return dt.strftime("%m/%d/%Y")


def _format_windows_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def _shutdown_command() -> str:
    return r'shutdown /s /f /t 0'


def _schtasks_create_once(task_name: str, dt: datetime) -> subprocess.CompletedProcess:
    sd = _format_windows_date(dt)
    st = _format_windows_time(dt)
    tr = _shutdown_command()
    cmd = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/SC", "ONCE",
        "/SD", sd,
        "/ST", st,
        "/TR", tr,
        "/RU", "SYSTEM",
        "/F"
    ]
    return _run(cmd)


def _schtasks_create_daily(task_name: str, hhmm: str) -> subprocess.CompletedProcess:
    tr = _shutdown_command()
    cmd = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/SC", "DAILY",
        "/ST", hhmm,
        "/TR", tr,
        "/RU", "SYSTEM",
        "/F"
    ]
    return _run(cmd)


def _schtasks_create_hourly(task_name: str, every_n_hours: int) -> subprocess.CompletedProcess:
    tr = _shutdown_command()
    cmd = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/SC", "HOURLY",
        "/MO", str(every_n_hours),
        "/TR", tr,
        "/RU", "SYSTEM",
        "/F"
    ]
    return _run(cmd)


def _schtasks_delete(task_name: str) -> subprocess.CompletedProcess:
    cmd = ["schtasks", "/Delete", "/TN", task_name, "/F"]
    return _run(cmd)


def _schtasks_query(task_name: str) -> subprocess.CompletedProcess:
    cmd = ["schtasks", "/Query", "/TN", task_name, "/FO", "LIST", "/V"]
    return _run(cmd)


def list_records() -> List[TaskRecord]:
    data = _load_db()
    out: List[TaskRecord] = []
    for item in data.get("tasks", []):
        out.append(TaskRecord(**item))
    return out


def get_record(task_name: str) -> Optional[TaskRecord]:
    data = _load_db()
    for item in data.get("tasks", []):
        if item.get("task_name") == task_name:
            return TaskRecord(**item)
    return None


def _replace_record(task_name: str, new_record: TaskRecord) -> None:
    data = _load_db()
    tasks = data.get("tasks", [])
    replaced = False

    for i, item in enumerate(tasks):
        if item.get("task_name") == task_name:
            tasks[i] = asdict(new_record)
            replaced = True
            break

    if not replaced:
        tasks.append(asdict(new_record))

    data["tasks"] = tasks
    _save_db(data)


def _schtasks_create_once_with_name(task_name: str, dt: datetime) -> subprocess.CompletedProcess:
    return _schtasks_create_once(task_name, dt)


def _schtasks_create_daily_with_name(task_name: str, hhmm: str) -> subprocess.CompletedProcess:
    return _schtasks_create_daily(task_name, hhmm)


def _schtasks_create_hourly_with_name(task_name: str, every_n_hours: int) -> subprocess.CompletedProcess:
    return _schtasks_create_hourly(task_name, every_n_hours)


def create_shutdown_at_datetime(display_name: str, dt: datetime) -> Dict[str, Any]:
    task_name = _make_task_name(display_name)
    proc = _schtasks_create_once(task_name, dt)

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": proc.stderr.strip() or proc.stdout.strip() or "Error creando tarea.",
            "task_name": task_name
        }

    rec = TaskRecord(
        task_name=task_name,
        kind="once_datetime",
        created_at=_now_str(),
        schedule_at=dt.strftime(DATE_FMT_DB),
        detail={"datetime": dt.strftime(DATE_FMT_DB)}
    )

    data = _load_db()
    data["tasks"].append(asdict(rec))
    _save_db(data)

    return {"ok": True, "task_name": task_name}


def create_shutdown_in_hours(display_name: str, hours: float) -> Dict[str, Any]:
    dt = datetime.now() + timedelta(hours=hours)
    task_name = _make_task_name(display_name)
    proc = _schtasks_create_once(task_name, dt)

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": proc.stderr.strip() or proc.stdout.strip() or "Error creando tarea.",
            "task_name": task_name
        }

    rec = TaskRecord(
        task_name=task_name,
        kind="in_hours",
        created_at=_now_str(),
        schedule_at=dt.strftime(DATE_FMT_DB),
        detail={"hours": hours, "computed_datetime": dt.strftime(DATE_FMT_DB)}
    )

    data = _load_db()
    data["tasks"].append(asdict(rec))
    _save_db(data)

    return {"ok": True, "task_name": task_name, "scheduled_for": dt.strftime(DATE_FMT_DB)}


def create_shutdown_daily(display_name: str, hhmm: str) -> Dict[str, Any]:
    task_name = _make_task_name(display_name)
    proc = _schtasks_create_daily(task_name, hhmm)

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": proc.stderr.strip() or proc.stdout.strip() or "Error creando tarea diaria.",
            "task_name": task_name
        }

    rec = TaskRecord(
        task_name=task_name,
        kind="daily",
        created_at=_now_str(),
        schedule_at=None,
        detail={"time": hhmm}
    )

    data = _load_db()
    data["tasks"].append(asdict(rec))
    _save_db(data)

    return {"ok": True, "task_name": task_name}


def create_shutdown_hourly(display_name: str, every_n_hours: int) -> Dict[str, Any]:
    if every_n_hours < 1:
        every_n_hours = 1

    task_name = _make_task_name(display_name)
    proc = _schtasks_create_hourly(task_name, every_n_hours)

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": proc.stderr.strip() or proc.stdout.strip() or "Error creando tarea cada N horas.",
            "task_name": task_name
        }

    rec = TaskRecord(
        task_name=task_name,
        kind="hourly",
        created_at=_now_str(),
        schedule_at=None,
        detail={"every_n_hours": every_n_hours}
    )

    data = _load_db()
    data["tasks"].append(asdict(rec))
    _save_db(data)

    return {"ok": True, "task_name": task_name}


def edit_shutdown_task(
    task_name: str,
    new_kind: str,
    *,
    dt: Optional[datetime] = None,
    hours: Optional[float] = None,
    hhmm: Optional[str] = None,
    every_n_hours: Optional[int] = None
) -> Dict[str, Any]:
    """
    Edita una tarea existente recreándola con la nueva configuración.
    new_kind: once_datetime | in_hours | daily | hourly
    """
    old_record = get_record(task_name)
    if not old_record:
        return {"ok": False, "error": f"No se encontró la tarea en create.json: {task_name}"}

    schedule_at = None
    detail = {}

    if new_kind == "once_datetime":
        if dt is None:
            return {"ok": False, "error": "Falta 'dt' para editar la tarea."}
        proc_create = lambda: _schtasks_create_once_with_name(task_name, dt)
        schedule_at = dt.strftime(DATE_FMT_DB)
        detail = {"datetime": dt.strftime(DATE_FMT_DB)}

    elif new_kind == "in_hours":
        if hours is None:
            return {"ok": False, "error": "Falta 'hours' para editar la tarea."}
        dt_calc = datetime.now() + timedelta(hours=hours)
        proc_create = lambda: _schtasks_create_once_with_name(task_name, dt_calc)
        schedule_at = dt_calc.strftime(DATE_FMT_DB)
        detail = {"hours": hours, "computed_datetime": dt_calc.strftime(DATE_FMT_DB)}

    elif new_kind == "daily":
        if not hhmm:
            return {"ok": False, "error": "Falta 'hhmm' para editar la tarea diaria."}
        proc_create = lambda: _schtasks_create_daily_with_name(task_name, hhmm)
        schedule_at = None
        detail = {"time": hhmm}

    elif new_kind == "hourly":
        if every_n_hours is None:
            return {"ok": False, "error": "Falta 'every_n_hours' para editar la tarea por horas."}
        if every_n_hours < 1:
            every_n_hours = 1
        proc_create = lambda: _schtasks_create_hourly_with_name(task_name, every_n_hours)
        schedule_at = None
        detail = {"every_n_hours": every_n_hours}

    else:
        return {"ok": False, "error": f"Tipo no soportado: {new_kind}"}

    proc_delete = _schtasks_delete(task_name)
    delete_failed = proc_delete.returncode != 0
    delete_error = proc_delete.stderr.strip() or proc_delete.stdout.strip()

    proc_new = proc_create()
    if proc_new.returncode != 0:
        return {
            "ok": False,
            "error": proc_new.stderr.strip() or proc_new.stdout.strip() or "No se pudo recrear la tarea."
        }

    new_record = TaskRecord(
        task_name=task_name,
        kind=new_kind,
        created_at=old_record.created_at,
        schedule_at=schedule_at,
        detail=detail
    )
    _replace_record(task_name, new_record)

    result = {
        "ok": True,
        "task_name": task_name,
        "kind": new_kind
    }

    if delete_failed and delete_error:
        result["warning"] = (
            f"La tarea previa no se pudo eliminar limpiamente, "
            f"pero fue recreada. Detalle: {delete_error}"
        )

    return result


def delete_record(task_name: str) -> Dict[str, Any]:
    proc = _schtasks_delete(task_name)

    data = _load_db()
    before = len(data.get("tasks", []))
    data["tasks"] = [t for t in data.get("tasks", []) if t.get("task_name") != task_name]
    after = len(data.get("tasks", []))
    _save_db(data)

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": proc.stderr.strip() or proc.stdout.strip() or "Error eliminando tarea.",
            "db_removed": before != after
        }

    return {"ok": True, "db_removed": before != after}


def query_task_verbose(task_name: str) -> Dict[str, Any]:
    proc = _schtasks_query(task_name)
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr.strip() or proc.stdout.strip() or "No se pudo consultar."}
    return {"ok": True, "output": proc.stdout}


def enable_startup_notify(python_exe: str, ui_launcher_path: str, message: str) -> Dict[str, Any]:
    tr = f'"{python_exe}" "{ui_launcher_path}" --notify "{message}"'
    cmd = [
        "schtasks", "/Create",
        "/TN", NOTIFY_TASK_NAME,
        "/SC", "ONLOGON",
        "/TR", tr,
        "/RL", "HIGHEST",
        "/F"
    ]
    proc = _run(cmd)
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr.strip() or proc.stdout.strip() or "Error creando aviso de inicio."}
    return {"ok": True, "task_name": NOTIFY_TASK_NAME}


def disable_startup_notify() -> Dict[str, Any]:
    proc = _schtasks_delete(NOTIFY_TASK_NAME)
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr.strip() or proc.stdout.strip() or "Error eliminando aviso."}
    return {"ok": True}