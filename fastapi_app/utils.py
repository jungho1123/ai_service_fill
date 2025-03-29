import os
import requests
import urllib.parse
from fastapi_app.database import SessionLocal
from fastapi_app.models.pill import PillInfo

# === 공통 상수 ===
DEFAULT_IMAGE_URL = "http://localhost:8000/static/default-pill.png"

# === 환경 변수에서 API 키 가져오기 ===
from dotenv import load_dotenv
load_dotenv()

SERVICE_KEY = os.getenv("API_SERVICE_KEY") or "3xLep1OK4iaf%2FrmKgsiZS5Cph78JcK7153P%2BCJ8cpnIJNuOw%2Bus7LKekz5NEaGEDS4nW%2FVWhJMIofbvZqfhxTA%3D%3D"
ENCODED_SERVICE_KEY = urllib.parse.quote(SERVICE_KEY, safe="")

# === DB fallback 조회 ===
def get_fallback_info_from_db(class_id: str) -> dict | None:
    db = SessionLocal()
    try:
        pill = db.query(PillInfo).filter(PillInfo.class_id == class_id).first()
        if pill:
            return {
                "dl_name": pill.dl_name,
                "dl_material": pill.dl_material,
                "dl_company": pill.dl_company,
                "di_company_mf": pill.di_company_mf,
                "di_class_no": pill.di_class_no,
                "di_etc_otc_code": pill.di_etc_otc_code,
                "di_edi_code": pill.di_edi_code,
                "item_seq": pill.item_seq,
                "img_key": pill.img_key or DEFAULT_IMAGE_URL,
                "source": "fallback",
                "message": "공공데이터 API에 등록되지 않은 약입니다. 내부 데이터 기준 간단한 정보를 제공합니다."
            }
    finally:
        db.close()
    return None

# === 공공데이터 API: item_seq로 약 조회 ===
def get_drug_info_by_item_seq(item_seq: int) -> dict:
    url = (
        f"http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
        f"?serviceKey={SERVICE_KEY}&itemSeq={item_seq}&type=json"
    )
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            items = data.get("body", {}).get("items", [])
            if items:
                result = items[0]
                result["source"] = "api"
                return result
            else:
                return {"message": "약 정보를 찾을 수 없습니다."}
        except Exception as e:
            return {"message": f"JSON 파싱 오류: {str(e)}"}
    else:
        return {"message": f"API 요청 실패 - status code: {response.status_code}"}

# === 공공데이터 API: 이름으로 약 검색 ===
def search_drug_by_name(name: str) -> list | dict:
    url = (
        f"http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
        f"?serviceKey={SERVICE_KEY}&itemName={urllib.parse.quote(name)}&type=json&numOfRows=10&pageNo=1"
    )
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            items = data.get("body", {}).get("items", [])
            if not items:
                return {"message": "해당 이름으로 등록된 약이 없습니다."}
            return [
                {
                    "item_name": item.get("itemName"),
                    "entp_name": item.get("entpName"),
                    "efcy_qesitm": item.get("efcyQesitm"),
                    "use_method_qesitm": item.get("useMethodQesitm"),
                    "atpn_qesitm": item.get("atpnQesitm"),
                    "item_seq": item.get("itemSeq"),
                    "item_image": item.get("itemImage") or DEFAULT_IMAGE_URL,
                }
                for item in items
            ]
        except Exception as e:
            return {"message": f"JSON 파싱 오류: {str(e)}"}
    else:
        return {"message": f"API 요청 실패 - status code: {response.status_code}"}
