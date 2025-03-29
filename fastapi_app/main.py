from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import json
import os

# === 내부 모듈 ===
from fastapi_app.utils import (
    get_fallback_info_from_db,
    get_drug_info_by_item_seq,
    search_drug_by_name,
    DEFAULT_IMAGE_URL
)
from fastapi_app.predict_model import predict_from_image

# === 경로 설정 ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "classid_to_itemseq.json")
STATIC_PATH = os.path.join(BASE_DIR, "fastapi_app", "static")

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔓 모든 출처 허용 (실서비스에선 도메인 제한 권장)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# === class_id → item_seq 매핑 로딩 ===
with open(DATA_PATH, "r", encoding="utf-8") as f:
    classid_to_itemseq = json.load(f)

# === GET: class_id 기반 약 정보 조회 ===
@app.get("/pill-info")
def pill_info(class_id: str = Query(..., description="예: K-039148")):
    item_seq = classid_to_itemseq.get(class_id)
    if not item_seq:
        fallback_info = get_fallback_info_from_db(class_id)
        if fallback_info:
            return fallback_info
        return JSONResponse(status_code=404, content={"message": f"'{class_id}'에 대한 정보가 존재하지 않습니다."})

    drug_info = get_drug_info_by_item_seq(item_seq)
    if "message" in drug_info and "약 정보를 찾을 수 없습니다." in drug_info["message"]:
        fallback_info = get_fallback_info_from_db(class_id)
        return fallback_info if fallback_info else drug_info

    return drug_info

# === GET: 이름 기반 약 검색 ===
@app.get("/search")
def search_pill_by_name(name: str = Query(..., description="예: 타이레놀")):
    return search_drug_by_name(name)

# === POST: 이미지 업로드로 약 예측 ===
CONFIDENCE_THRESHOLD = 0.5

@app.post("/predict")
async def predict_pill(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        class_id, confidence = predict_from_image(contents)

        # 예측 실패 or confidence 낮음
        if class_id is None or confidence < CONFIDENCE_THRESHOLD:
            return {
                "message": "모델이 약을 정확히 인식하지 못했습니다.",
                "search_suggest": True,
                "confidence": confidence
            }

        result = pill_info(class_id=class_id)
        if isinstance(result, dict):
            result["class_id"] = class_id
            result["confidence"] = confidence
        return result

    except Exception as e:
        return {
            "message": f"예측 중 오류 발생: {str(e)}",
            "search_suggest": True
        }
