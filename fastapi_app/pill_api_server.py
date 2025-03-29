# pill_api_server.py

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
import torchvision.transforms as transforms
import uvicorn
import io

# === 모델 로드 ===
from torchvision.models import efficientnet_b3, EfficientNet_B3_Weights
import torch.nn as nn

weights = EfficientNet_B3_Weights.DEFAULT
model = efficientnet_b3(weights=weights)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 50)  # 클래스 수에 맞게 수정
model.load_state_dict(torch.load("efficientnet_b3_best.pth", map_location="cpu"))
model.eval()

# === 라벨 불러오기 ===
with open("classes.txt", "r", encoding="utf-8") as f:
    class_names = [line.strip() for line in f.readlines()]

# === 이미지 전처리 ===
transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.CenterCrop(300),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# === FastAPI 앱 생성 ===
app = FastAPI()

# CORS 설정 (앱에서 요청 가능하게 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        input_tensor = transform(image).unsqueeze(0)  # (1, C, H, W)

        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.nn.functional.softmax(outputs[0], dim=0)
            top_prob, top_idx = torch.max(probs, dim=0)
            pred_class = class_names[top_idx.item()]
            confidence = top_prob.item()

        return JSONResponse({"class": pred_class, "confidence": round(confidence, 4)})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# === 로컬 실행 (for dev) ===
if __name__ == "__main__":
    uvicorn.run("pill_api_server:app", host="0.0.0.0", port=8000, reload=True)