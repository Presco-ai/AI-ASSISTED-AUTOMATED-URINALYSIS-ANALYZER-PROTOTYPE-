import sqlite3
import json
from datetime import datetime
from models.patient import Patient
from models.enums import Sex
from utils.id_generator import PatientIDGenerator

class DatabaseManager:
    def __init__(self, db_path="urinalysis.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(patients)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        required_columns = {
            'pregnancy_status': "TEXT DEFAULT 'Not Applicable'",
            'chronic_conditions': "TEXT DEFAULT ''",
            'culture_ids': "TEXT DEFAULT ''",
            'last_urinalysis_date': "TEXT DEFAULT ''",
            'clinical_history': "TEXT DEFAULT ''",
            'allergies': "TEXT DEFAULT ''"
        }
        for col_name, col_def in required_columns.items():
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE patients ADD COLUMN {col_name} {col_def}")
                except:
                    pass
        cursor.execute("""CREATE TABLE IF NOT EXISTS patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            surname TEXT, first_name TEXT, middle_name TEXT,
            patient_id TEXT UNIQUE, age INTEGER, age_unit TEXT DEFAULT 'Years',
            sex TEXT, hospital_number TEXT, contact_phone TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT UNIQUE, patient_id TEXT, report_json TEXT,
            status TEXT DEFAULT 'Pending Culture', diagnosis TEXT,
            risk_level TEXT, ai_model TEXT, created_date TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS cultures(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            culture_id TEXT UNIQUE, patient_id TEXT, sample_id TEXT,
            culture_json TEXT, status TEXT DEFAULT 'Pending')""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS followups(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT, patient_id TEXT, planned_date TEXT,
            completed INTEGER DEFAULT 0, notes TEXT, created_date TEXT)""")
        self.conn.commit()

    def add_patient(self, patient):
        if not patient.patient_id:
            patient.patient_id = PatientIDGenerator.generate_patient_id()
        cursor = self.conn.cursor()
        cursor.execute("""INSERT OR REPLACE INTO patients(
            surname, first_name, middle_name, patient_id, age, age_unit, sex,
            hospital_number, contact_phone, pregnancy_status, chronic_conditions,
            culture_ids, last_urinalysis_date, clinical_history, allergies)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (patient.surname, patient.first_name, patient.middle_name,
             patient.patient_id, patient.age, patient.age_unit, patient.sex.value,
             patient.hospital_number, patient.contact_phone, patient.pregnancy_status,
             patient.chronic_conditions, patient.culture_ids, patient.last_urinalysis_date,
             patient.clinical_history, patient.allergies))
        self.conn.commit()
        return patient.patient_id

    def search(self, query):
        q = f'%{query}%'
        cursor = self.conn.cursor()
        cursor.execute("""SELECT * FROM patients
            WHERE surname LIKE ? OR first_name LIKE ? OR patient_id LIKE ?
            ORDER BY surname LIMIT 50""", (q, q, q))
        return [self._row_to_patient(r) for r in cursor.fetchall()]

    def _row_to_patient(self, row):
        try:
            sex_map = {'Male': Sex.MALE, 'Female': Sex.FEMALE, 'Other': Sex.OTHER}
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(patients)")
            columns = [col[1] for col in cursor.fetchall()]
            row_dict = {col: row[i] if i < len(row) else "" for i, col in enumerate(columns)}
            return Patient(
                surname=row_dict.get('surname', ''),
                first_name=row_dict.get('first_name', ''),
                middle_name=row_dict.get('middle_name', ''),
                patient_id=row_dict.get('patient_id', ''),
                age=row_dict.get('age', 0) or 0,
                age_unit=row_dict.get('age_unit', 'Years') or 'Years',
                sex=sex_map.get(row_dict.get('sex', ''), Sex.MALE),
                hospital_number=row_dict.get('hospital_number', '') or '',
                contact_phone=row_dict.get('contact_phone', '') or '',
                pregnancy_status=row_dict.get('pregnancy_status', 'Not Applicable'),
                chronic_conditions=row_dict.get('chronic_conditions', '') or '',
                culture_ids=row_dict.get('culture_ids', '') or '',
                clinical_history=row_dict.get('clinical_history', '') or '',
                allergies=row_dict.get('allergies', '') or ''
            )
        except:
            return Patient()

    def save_report(self, rid, pid, rjson, status="Pending Culture"):
        diag = rjson.get('pathologic_diagnosis', {})
        self.conn.execute("""INSERT OR REPLACE INTO reports(
            report_id, patient_id, report_json, status, diagnosis, risk_level, ai_model, created_date)
            VALUES(?,?,?,?,?,?,?,?)""",
            (rid, pid, json.dumps(rjson), status,
             diag.get('diagnosis', ''), diag.get('severity', 'Low Risk'),
             rjson.get('ai_model', 'Standard AI'), datetime.now().isoformat()))
        self.conn.commit()

    def save_culture(self, cid, pid, sid, cjson, status="Pending"):
        self.conn.execute("""INSERT OR REPLACE INTO cultures(
            culture_id, patient_id, sample_id, culture_json, status)
            VALUES(?,?,?,?,?)""", (cid, pid, sid, json.dumps(cjson), status))
        self.conn.commit()

    def save_followup(self, rid, pid, planned_date, notes=""):
        self.conn.execute("""INSERT INTO followups(
            report_id, patient_id, planned_date, notes, created_date)
            VALUES(?,?,?,?,?)""", (rid, pid, planned_date, notes, datetime.now().isoformat()))
        self.conn.commit()

    def get_patient_history(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT report_id, created_date, diagnosis, risk_level FROM reports WHERE patient_id=? ORDER BY created_date DESC", (pid,))
        reports = c.fetchall()
        c.execute("SELECT culture_id, status FROM cultures WHERE patient_id=? ORDER BY culture_id DESC", (pid,))
        cultures = c.fetchall()
        return {"reports": reports, "cultures": cultures}
