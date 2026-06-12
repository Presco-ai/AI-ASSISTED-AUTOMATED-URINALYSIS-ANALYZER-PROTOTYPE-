from dataclasses import dataclass

@dataclass
class DoctorSignature:
    name: str = "Dr. Precious Belema Ibiabuo"
    credentials: str = "MLT, B.Sc., M.Sc., MD"
    title: str = "Consultant Pathologist"
    hospital: str = "University Teaching Hospital"
    department: str = "Department of Pathology & Laboratory Medicine"
    license_number: str = "MD/2024/12345"
    contact_phone: str = "+234-800-123-4567"
    email: str = "dr.ibiabuo@uth.edu.ng"
