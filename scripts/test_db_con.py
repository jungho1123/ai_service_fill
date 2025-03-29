import os
import psycopg2
from dotenv import load_dotenv

# ✅ 루트 경로 기준으로 .env 경로 설정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(BASE_DIR, ".env")

# ✅ .env 파일 강제 로드 (override=True 중요!)
load_dotenv(dotenv_path=dotenv_path, override=True)

# ✅ 환경 변수 가져오기
url = os.getenv("DATABASE_URL")  # 변수명에 맞게 수정 (DATABASE_URL 쓰면 거기에 맞춰야 함)

print("\n📦 최종 적용된 DB URL:", url)

# ✅ 연결 시도
print("\n🔗 Supabase DB 연결 시도 중...")
try:
    conn = psycopg2.connect(url)
    print("✅ 연결 성공!")
    conn.close()
except Exception as e:
    print("❌ 연결 실패:")
    print(e)
