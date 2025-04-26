import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

url = os.getenv("DATABASE_URL")
print(" DB 연결 URL:", url)