# scripts/init_script.py

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

#  루트 경로 등록 (fastapi_app import 가능하게)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

#  .env 강제 로드
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

#  공용 상수
DEFAULT_IMAGE_URL = "http://localhost:8000/static/default-pill.png"
FALLBACK_LABEL_PATH = os.getenv("FALLBACK_LABEL_PATH")

if not FALLBACK_LABEL_PATH:
    raise ValueError(" 환경변수 FALLBACK_LABEL_PATH가 설정되어 있지 않습니다.")

#  DB 관련 import
from fastapi_app.database import SessionLocal
from fastapi_app.models.pill import PillInfo

#  로깅 유틸
def log_info(msg: str):
    now = datetime.now().strftime("%H:%M:%S")
    print(f" [{now}] {msg}")

def log_warn(msg: str):
    now = datetime.now().strftime("%H:%M:%S")
    print(f" [{now}] {msg}")

def log_error(msg: str):
    now = datetime.now().strftime("%H:%M:%S")
    print(f" [{now}] {msg}")
