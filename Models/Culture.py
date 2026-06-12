from dataclasses import dataclass, field
from typing import Dict, List
from .enums import CultureStatus, SensitivityResult

@dataclass
class CultureResult:
    culture_id: str = ""
    patient_id: str = ""
    sample_id: str = ""
    collection_date: str = ""
    report_date: str = ""
    culture_status: CultureStatus = CultureStatus.PENDING
    organism_identified: str = ""
    organism_count: str = ""
    gram_stain: str = ""
    gram_type: str = "Gram-negative"
    colony_count_level: str = ""
    sensitivity_panel: Dict[str, SensitivityResult] = field(default_factory=dict)
    esbl_positive: bool = False
    mrsa_positive: bool = False

    def __post_init__(self):
        if not self.sensitivity_panel:
            for abx in self._get_all_antibiotics():
                self.sensitivity_panel[abx] = SensitivityResult.NOT_TESTED

    @staticmethod
    def _get_all_antibiotics() -> List[str]:
        return ["Rifampicin","Ceftazidime","Streptomycin","Azithromycin","Amoxil","Ciprofloxacin",
                "Erythromycin","Levofloxacin","Gentamycin","Cefuroxime","Ofloxacin","Augmentin",
                "Pefloxacin","Ceporex","Ceftriaxone","Nitrofurantoin","Fosfomycin","Meropenem",
                "Imipenem","Vancomycin","Teicoplanin","Linezolid","Tigecycline","Colistin"]

    @staticmethod
    def get_gram_positive_antibiotics() -> List[str]:
        return ["Rifampicin","Ceftazidime","Streptomycin","Azithromycin","Amoxil","Ciprofloxacin",
                "Erythromycin","Levofloxacin","Gentamycin","Cefuroxime","Nitrofurantoin",
                "Vancomycin","Teicoplanin","Linezolid","Tigecycline"]

    @staticmethod
    def get_gram_negative_antibiotics() -> List[str]:
        return ["Ofloxacin","Augmentin","Pefloxacin","Ceftazidime","Gentamycin","Ciprofloxacin",
                "Ceporex","Ceftriaxone","Streptomycin","Cefuroxime","Nitrofurantoin",
                "Fosfomycin","Meropenem","Imipenem","Tigecycline","Colistin"]

    def get_effective_antibiotics(self) -> List[str]:
        return [abx for abx, res in self.sensitivity_panel.items() if res == SensitivityResult.SENSITIVE]

    def has_multi_drug_resistance(self) -> bool:
        return sum(1 for res in self.sensitivity_panel.values() if res == SensitivityResult.RESISTANT) >= 3
