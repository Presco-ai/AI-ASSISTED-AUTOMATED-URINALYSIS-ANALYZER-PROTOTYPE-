from datetime import datetime

class PatientIDGenerator:
    @staticmethod
    def generate_patient_id():
        return f"PAT-{datetime.now().strftime('%Y%m%d')}-{str(datetime.now().microsecond)[:4]}"
    @staticmethod
    def generate_culture_id(patient_id):
        return f"CUL-{patient_id[-6:]}-{datetime.now().strftime('%H%M%S')}"
    @staticmethod
    def generate_sample_id(patient_id):
        return f"SPL-{patient_id[-6:]}-{datetime.now().strftime('%H%M%S')}"
