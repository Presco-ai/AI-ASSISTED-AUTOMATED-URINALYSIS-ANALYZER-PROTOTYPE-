import cv2
import numpy as np
import os
from datetime import datetime

ROBOFLOW_AVAILABLE = False
try:
    from inference_sdk import InferenceHTTPClient
    ROBOFLOW_AVAILABLE = True
except ImportError:
    print("Warning: inference_sdk not installed. Run: pip install inference-sdk")

class RoboflowAnalyzer:
    def __init__(self):
        self.client=None; self.available=ROBOFLOW_AVAILABLE
        self.workspace_name="preciouss-workspace-q9b6m"
        self.workflow_id="detect-count-and-visualize-2"
        self.api_key="FELUYE8PRYh8YNjiLTnj"
        self.api_url="https://serverless.roboflow.com"
        if self.available:
            try:
                self.client=InferenceHTTPClient(api_url=self.api_url,api_key=self.api_key)
                print("✓ Roboflow AI Analyzer connected")
            except Exception as e:
                print(f"✗ Roboflow connection failed: {e}")
                self.available=False

    def analyze(self,image):
        if not self.available or self.client is None:
            return self._simulate_analysis(image)
        try:
            temp_path=self._save_temp_image(image)
            result=self.client.run_workflow(
                workspace_name=self.workspace_name,
                workflow_id=self.workflow_id,
                images={"image":temp_path},
                use_cache=True
            )
            try: os.remove(temp_path)
            except: pass
            return self._parse_workflow_results(result,image)
        except Exception as e:
            print(f"Roboflow error: {e}")
            return self._simulate_analysis(image)

    def _save_temp_image(self,image):
        temp_dir=os.path.join(os.path.expanduser('~'),'.urinalysis_temp')
        os.makedirs(temp_dir,exist_ok=True)
        temp_path=os.path.join(temp_dir,f"microscopy_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg")
        cv2.imwrite(temp_path,image)
        return temp_path

    def _parse_workflow_results(self,result,image):
        h,w=image.shape[:2]
        microscopy_results={}
        cell_map={"wbc":"Pus Cells (WBCs)","rbc":"Red Blood Cells (RBCs)","epithelial":"Epithelial Cells","hyaline_cast":"Casts - Hyaline","bacteria":"Bacteria","yeast":"Candida Yeast Cells","trichomonas":"Trichomonas","mucus":"Mucus Threads"}
        for ct in cell_map.values():
            microscopy_results[ct]="None Seen"
        try:
            predictions=[]
            if isinstance(result,dict):
                for key in ["predictions","result","results","data","output"]:
                    if key in result:
                        val=result[key]
                        if isinstance(val,list):
                            predictions=val; break
                        elif isinstance(val,dict) and "predictions" in val:
                            predictions=val["predictions"]; break
            detected_counts={}
            for pred in predictions:
                class_name=pred.get("class","").lower() if isinstance(pred,dict) else ""
                std_name=cell_map.get(class_name,class_name.replace("_"," ").title())
                detected_counts[std_name]=detected_counts.get(std_name,0)+1
            for std_name,count in detected_counts.items():
                microscopy_results[std_name]=f"{count}/HPF"
        except:
            pass
        return {"microscopy_results":microscopy_results,"image_size":f"{w}x{h}","ai_model":"Roboflow AI"}

    def _simulate_analysis(self,image):
        h,w=image.shape[:2]
        results={
            "Pus Cells (WBCs)":f"{np.random.randint(0,15)}-{np.random.randint(15,30)}/HPF",
            "Red Blood Cells (RBCs)":f"{np.random.randint(0,5)}-{np.random.randint(0,10)}/HPF",
            "Epithelial Cells":f"{np.random.randint(0,5)}-{np.random.randint(5,15)}/HPF",
            "Bacteria":"Moderate" if np.random.random()>0.5 else "Few",
            "Candida Yeast Cells":"None Seen"
        }
        return {"microscopy_results":results,"image_size":f"{w}x{h}","ai_model":"Simulated"}
