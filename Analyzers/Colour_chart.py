import cv2
import numpy as np

class ColorChartStripAnalyzer:
    def __init__(self):
        self.reference_charts = {
            "Leukocytes": {"pad_position":1,"unit":"Leu/µL","levels":{"Negative":{"bgr":(220,220,210)},"Trace":{"bgr":(200,190,180)},"+":{"bgr":(180,160,150)},"++":{"bgr":(150,120,110)},"+++":{"bgr":(120,80,70)}}},
            "Nitrite": {"pad_position":2,"unit":"","levels":{"Negative":{"bgr":(220,220,210)},"Positive":{"bgr":(180,140,200)}}},
            "Urobilinogen": {"pad_position":3,"unit":"mg/dL","levels":{"Normal (0.2-1.0)":{"bgr":(200,200,190)},"2.0":{"bgr":(180,170,150)},"4.0":{"bgr":(160,140,110)},"8.0":{"bgr":(140,110,80)}}},
            "Protein": {"pad_position":4,"unit":"mg/dL","levels":{"Negative":{"bgr":(210,210,200)},"Trace":{"bgr":(190,200,180)},"+":{"bgr":(170,180,160)},"++":{"bgr":(140,150,130)},"+++":{"bgr":(100,110,90)}}},
            "pH": {"pad_position":5,"unit":"","levels":{"5.0":{"bgr":(100,140,200)},"6.0":{"bgr":(130,180,210)},"7.0":{"bgr":(170,200,180)},"8.0":{"bgr":(180,170,140)}}},
            "Blood": {"pad_position":6,"unit":"RBC/µL","levels":{"Negative":{"bgr":(210,210,200)},"Trace":{"bgr":(200,190,180)},"+":{"bgr":(180,150,130)},"++":{"bgr":(160,100,80)},"+++":{"bgr":(130,60,40)}}},
            "Specific Gravity": {"pad_position":7,"unit":"","levels":{"1.000":{"bgr":(200,200,180)},"1.010":{"bgr":(170,170,150)},"1.020":{"bgr":(140,140,120)},"1.030":{"bgr":(110,110,90)}}},
            "Ketones": {"pad_position":8,"unit":"mg/dL","levels":{"Negative":{"bgr":(210,200,190)},"Trace":{"bgr":(200,180,170)},"+":{"bgr":(190,150,140)},"++":{"bgr":(180,120,100)},"+++":{"bgr":(170,90,60)}}},
            "Bilirubin": {"pad_position":9,"unit":"mg/dL","levels":{"Negative":{"bgr":(210,200,190)},"+":{"bgr":(190,160,130)},"++":{"bgr":(170,120,80)},"+++":{"bgr":(150,80,40)}}},
            "Glucose": {"pad_position":10,"unit":"mg/dL","levels":{"Negative":{"bgr":(200,200,180)},"100":{"bgr":(180,175,155)},"250":{"bgr":(160,150,130)},"500":{"bgr":(140,125,105)},"1000":{"bgr":(120,100,80)}}},
            "Ascorbic Acid": {"pad_position":11,"unit":"mg/dL","levels":{"Negative":{"bgr":(210,210,200)},"+":{"bgr":(180,180,170)},"++":{"bgr":(150,150,140)}}}
        }
        self.active_params = dict(self.reference_charts)

    def detect_pads(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)==3 else image
        blurred = cv2.GaussianBlur(gray,(5,5),0)
        thresh = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
        contours,_ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        pads = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x,y,pw,ph = cv2.boundingRect(contour)
                if 0.3 < (pw/ph if ph>0 else 0) < 3.0 and pw>10 and ph>10:
                    pads.append({'x':x,'y':y,'width':pw,'height':ph})
        pads.sort(key=lambda p:p['y'])
        for i,pad in enumerate(pads): pad['detected_position']=i+1
        return pads

    def extract_pad_color(self,image,pad):
        x,y,w,h = pad['x'],pad['y'],pad['width'],pad['height']
        m=3; x1,y1=max(0,x+m),max(0,y+m); x2,y2=min(image.shape[1],x+w-m),min(image.shape[0],y+h-m)
        if x2<=x1 or y2<=y1: return np.array([128,128,128],dtype=np.float32)
        region=image[y1:y2,x1:x2]
        if region.size==0: return np.array([128,128,128],dtype=np.float32)
        return np.array(cv2.mean(region)[:3],dtype=np.float32)

    def match_color_to_level(self,detected_bgr,levels):
        best_match,best_distance=None,float('inf')
        for level_name,level_data in levels.items():
            ref_bgr=np.array(level_data['bgr'],dtype=np.float32)
            distance=np.linalg.norm(detected_bgr-ref_bgr)
            if distance<best_distance: best_distance,best_match=distance,level_name
        max_dist=np.linalg.norm(np.array([255,255,255],dtype=np.float32))
        confidence=max(0,100-(best_distance/max_dist*100))
        return best_match,confidence

    def analyze(self,image):
        h,w=image.shape[:2]
        pads=self.detect_pads(image)
        results={}
        for pad in pads:
            pad_pos=pad.get('detected_position',0)
            for param_name,param_data in self.active_params.items():
                if abs(pad_pos-param_data.get('pad_position',0))<=2 and param_name not in results:
                    detected_color=self.extract_pad_color(image,pad)
                    matched_level,confidence=self.match_color_to_level(detected_color,param_data.get('levels',{}))
                    normal_vals={"Leukocytes":"Negative","Nitrite":"Negative","Protein":"Negative","Blood":"Negative","Ketones":"Negative","Bilirubin":"Negative","Glucose":"Negative","Ascorbic Acid":"Negative"}
                    is_normal=matched_level==normal_vals.get(param_name,matched_level)
                    if param_name=="pH": is_normal=matched_level in ["5.0","6.0","7.0","8.0"]
                    elif param_name=="Specific Gravity": is_normal=matched_level in ["1.010","1.020"]
                    results[param_name]={"value":matched_level,"is_normal":is_normal,"pad_position":param_data.get('pad_position',0),"unit":param_data.get('unit',''),"confidence":round(confidence,1)}
                    break
        for param_name in self.active_params:
            if param_name not in results:
                results[param_name]={"value":"Not Detected","is_normal":False,"pad_position":self.active_params[param_name].get('pad_position',0),"unit":self.active_params[param_name].get('unit',''),"confidence":0}
        return {"results":results,"strip_type":"Color Chart Analysis","total_pads":len(self.active_params),"detected_pads":len(pads),"image_size":f"{w}x{h}","analysis_method":"Color Chart Matching"}

    def set_config(self,params,strip_type="Custom"):
        self.active_params=params
    def reset(self):
        self.active_params=dict(self.reference_charts)
