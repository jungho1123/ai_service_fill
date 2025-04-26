import os
import sys
from dotenv import load_dotenv

#  프로젝트 루트 경로를 모듈 경로에 추가
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

#  .env 파일 강제 로드
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

#  DB 및 모델 import
from fastapi_app.database import Base, engine
from fastapi_app.models.pill import PillInfo

def init_db():
    print(" Supabase PostgreSQL 테이블 생성 시작")
    Base.metadata.create_all(bind=engine)
    print(" Supabase DB 테이블 생성 완료")

if __name__ == "__main__":
    init_db()
