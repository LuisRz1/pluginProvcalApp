import base64
import csv
import io
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from uuid import uuid4

from app.menu.domain.monthly_menu import MonthlyMenu
from app.menu.domain.menu_day import MenuDay
from app.menu.application.ports.monthly_menu_repository import MonthlyMenuRepository
from app.menu.application.ports.menu_day_repository import MenuDayRepository

try:
    import pandas as pd
except ImportError:
    pd = None  # se valida al leer xlsx

# ---- Reglas base ----
REQUIRED_COLUMNS = ["date", "breakfast", "lunch", "dinner"]

# Aceptamos ES/EN
SYNONYMS = {
    "date": {"date", "fecha", "dia", "día"},
    "breakfast": {"breakfast", "desayuno"},
    "lunch": {"lunch", "almuerzo"},
    "dinner": {"dinner", "cena"},
}

def _norm(s: str) -> str:
    return str(s).strip().lower()

def _build_header_map(cols: list[str]) -> dict[str, str]:
    """
    Devuelve un mapeo {canonico -> nombre_columna_original}
    para los canónicos: date, breakfast, lunch, dinner.
    """
    lowered = [_norm(c) for c in cols]
    mapping: dict[str, str] = {}
    for canon, syns in SYNONYMS.items():
        for i, low in enumerate(lowered):
            if low in syns:
                mapping[canon] = cols[i]  # nombre original tal como viene
                break
    return mapping

def _missing_required(header_map: dict[str, str]) -> list[str]:
    return [c for c in REQUIRED_COLUMNS if c not in header_map]

def _parse_date_flex(s: str) -> date:
    s = str(s).strip()
    if not s:
        raise ValueError("empty date")
    # ISO
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        pass
    # dd/mm/yyyy, dd-mm-yyyy, mm/dd/yyyy, mm-dd-yyyy (+ variantes 2 dígitos)
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y",
                "%d/%m/%y", "%d-%m-%y", "%m/%d/%y", "%m-%d-%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    # Serial Excel
    if s.isdigit():
        serial = int(s)
        base = datetime(1899, 12, 30)  # regla Excel
        return (base + timedelta(days=serial)).date()
    raise ValueError(f"Unsupported date: {s}")

def _all_empty(*vals) -> bool:
    return all(not str(v or "").strip() for v in vals)

# ---- Comandos/resultado ----
@dataclass(frozen=True)
class UploadMonthlyMenuCommand:
    user_id: str
    filename: str
    file_bytes: bytes  # contenido XLSX (no usado aquí)
    year: int
    month: int
    mark_holidays: bool = True

@dataclass
class UploadMonthlyMenuResult:
    status: str  # "ok" | "conflict" | "error"
    message: str
    preview_days: List[Dict[str, Any]]
    template_example: List[str] | None = None

# ---- Use case ----
class UploadMonthlyMenuUseCase:
    def __init__(
        self,
        monthly_repo: MonthlyMenuRepository,
        menu_day_repo: MenuDayRepository,
        holiday_service=None,
        nutrition_validator=None
    ):
        self.monthly_repo = monthly_repo
        self.menu_day_repo = menu_day_repo
        self.holiday_service = holiday_service
        self.nutrition_validator = nutrition_validator

    async def execute(self, year: int, month: int, filename: str, file_base64: str):
        # 1) decodificar base64
        try:
            raw = base64.b64decode(file_base64)
        except Exception:
            return {"status": "error", "message": "El archivo no está en base64 válido"}

        # 2) detectar parser
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        rows: List[Dict[str, Any]] = []

        if ext in {"xlsx", "xls"}:
            # ---------- XLSX ----------
            if pd is None:
                return {
                    "status": "error",
                    "message": "El archivo es Excel (.xlsx), pero el servidor no tiene pandas instalado"
                }
            try:
                import io as _io

                # intento 1: header en primera fila
                df = pd.read_excel(_io.BytesIO(raw), dtype=str, header=0)
                cols = list(df.columns)
                header_map = _build_header_map(cols)

                # si faltan, busco encabezado en primeras 5 filas
                if _missing_required(header_map):
                    df_noheader = pd.read_excel(_io.BytesIO(raw), dtype=str, header=None)
                    candidate_idx = None
                    max_scan = min(5, len(df_noheader.index))
                    for i in range(max_scan):
                        rowvals = [str(v) for v in list(df_noheader.iloc[i].values)]
                        hm = _build_header_map(rowvals)
                        if not _missing_required(hm):
                            candidate_idx = i
                            break
                    if candidate_idx is not None:
                        df = pd.read_excel(_io.BytesIO(raw), dtype=str, header=candidate_idx)
                        cols = list(df.columns)
                        header_map = _build_header_map(cols)

                if _missing_required(header_map):
                    return {
                        "status": "error",
                        "message": "Faltan columnas requeridas",
                        "expected_columns": REQUIRED_COLUMNS,
                        "found_columns": [_norm(c) for c in cols],
                    }

                # renombrar a canónico
                rename_map = {src: canon for canon, src in header_map.items()}
                df = df.rename(columns=rename_map)
                df = df[["date", "breakfast", "lunch", "dinner"]].copy()
                df = df.fillna("")
                # quitar filas totalmente vacías
                df = df[~df.apply(lambda r: _all_empty(r["date"], r["breakfast"], r["lunch"], r["dinner"]), axis=1)]

                # normalizar fechas
                def _coerce_date(x):
                    # si viene como texto, intenta parseo flexible
                    try:
                        return _parse_date_flex(str(x))
                    except Exception:
                        return None

                parsed_dates = df["date"].apply(_coerce_date)
                if parsed_dates.isna().any():
                    bad = df["date"][parsed_dates.isna()].iloc[0]
                    return {
                        "status": "error",
                        "message": f"La columna 'date' debe ser YYYY-MM-DD o dd/mm/aaaa. Valor inválido: {bad}",
                    }
                df["date"] = parsed_dates

                rows = [
                    {
                        "date": r["date"].isoformat(),
                        "breakfast": (r.get("breakfast") or "").strip(),
                        "lunch": (r.get("lunch") or "").strip(),
                        "dinner": (r.get("dinner") or "").strip(),
                    }
                    for r in df.to_dict(orient="records")
                ]

            except Exception as e:
                return {"status": "error", "message": f"No se pudo leer Excel: {e}"}

        else:
            # --- CSV (intenta varios encodings) ---
            decoded = None
            for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
                try:
                    decoded = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if decoded is None:
                return {
                    "status": "error",
                    "message": "No se pudo decodificar el CSV (pruebe UTF-8/UTF-8 BOM/Latin-1).",
                }

            csv_buffer = io.StringIO(decoded)

            # Primero leo las cabeceras crudas para normalizarlas
            peek_reader = csv.reader(csv_buffer)
            headers = next(peek_reader, None)
            if not headers:
                return {"status": "error", "message": "CSV vacío o sin cabeceras."}

            # Mapa: canónica -> original (limpio espacios y BOM)
            canon_to_orig = {}
            for h in headers:
                canon = str(h).strip().lower().lstrip("\ufeff")
                canon_to_orig[canon] = h

            missing = [c for c in REQUIRED_COLUMNS if c not in canon_to_orig]
            if missing:
                return {
                    "status": "error",
                    "message": f"Faltan columnas: {', '.join(missing)}",
                    "expected_columns": REQUIRED_COLUMNS,
                }

            # Vuelvo a empezar y ahora sí uso DictReader con esas cabeceras originales
            csv_buffer.seek(0)
            dict_reader = csv.DictReader(csv_buffer)

            rows = []
            for row in dict_reader:
                # valores crudos (pueden venir None)
                raw_date = (row.get(canon_to_orig["date"], "") or "").strip()
                b = (row.get(canon_to_orig["breakfast"], "") or "").strip()
                l = (row.get(canon_to_orig["lunch"], "") or "").strip()
                d = (row.get(canon_to_orig["dinner"], "") or "").strip()

                # Caso problemático: toda la fila cayó en 'date'
                # (otras columnas vacías y 'date' contiene comas)
                if not b and not l and not d and ("," in raw_date):
                    try:
                        # Reparseamos esa sola cadena como una fila CSV independiente
                        reparsed = next(csv.reader([raw_date]))
                        # esperamos al menos 4 columnas
                        if len(reparsed) >= 4:
                            raw_date, b, l, d = reparsed[0].strip(), reparsed[1].strip(), reparsed[2].strip(), reparsed[
                                3].strip()
                    except Exception:
                        pass  # caerá en la validación de fecha más abajo

                # Omitir filas completamente vacías
                if _all_empty(raw_date, b, l, d):
                    continue

                if not raw_date:
                    return {
                        "status": "error",
                        "message": "Fila sin fecha. La columna 'date' es obligatoria (YYYY-MM-DD o dd/mm/aaaa)."
                    }

                # Parseo flexible de fecha (YYYY-MM-DD, dd/mm/aaaa, serial Excel, etc.)
                try:
                    parsed = _parse_date_flex(raw_date)
                except Exception:
                    return {
                        "status": "error",
                        "message": f"La columna 'date' debe ser YYYY-MM-DD o dd/mm/aaaa. Valor inválido: {raw_date}",
                    }

                rows.append({
                    "date": parsed.isoformat(),
                    "breakfast": b,
                    "lunch": l,
                    "dinner": d,
                })

        # 3) conflicto por mes existente
        existing = await self.monthly_repo.find_by_year_month(year, month)
        if existing:
            return {
                "status": "conflict",
                "message": "conflict: Ya existe un menú para este mes. Confirme sobrescritura.",
                "preview_days": rows,
            }

        # 4) crear menú mensual
        monthly = MonthlyMenu(
            id=str(uuid4()),  # ← id requerido por tu dataclass
            year=year,
            month=month,
            source_filename=filename  # status tiene default = DRAFT
        )
        monthly = await self.monthly_repo.upsert(monthly)

        # 5) crear días
        days: List[MenuDay] = []
        for r in rows:
            day_date = r["date"] if isinstance(r["date"], date) else datetime.strptime(r["date"], "%Y-%m-%d").date()

            is_holiday = False
            if self.holiday_service is not None:
                is_holiday = await self.holiday_service.is_holiday(day_date)

            day = MenuDay(
                id=str(uuid4()),  # ← id requerido por tu dataclass
                menu_id=str(monthly.id),
                date=day_date,
                breakfast=r["breakfast"],
                lunch=r["lunch"],
                dinner=r["dinner"],
                is_holiday=is_holiday,
            )
            days.append(day)

        # 6) guardar
        await self.menu_day_repo.bulk_replace(str(monthly.id), days)

        # 7) validación nutricional (si existe)
        if self.nutrition_validator is not None:
            await self.nutrition_validator.validate_menu_days(days, self.menu_day_repo)

        return {"status": "ok", "message": "Menú mensual cargado correctamente", "menu_id": str(monthly.id)}
