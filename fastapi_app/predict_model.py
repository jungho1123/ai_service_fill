import os
import json
import torch
from PIL import Image
import io
from torchvision import transforms
from torchvision.models import efficientnet_b3

# === 경로 설정 ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "best_model.pth")
CLASS_MAPPING_PATH = os.path.join(BASE_DIR, "data", "class_idx_to_id.json")

# === 클래스 매핑 로드 (인덱스 → class_id)
with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
    idx_to_class_id = json.load(f)

# === 전처리 정의
predict_transform = transforms.Compose([
    transforms.Resize(300),
    transforms.CenterCrop(300),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# === 모델 캐싱
_model = None

def load_model():
    global _model
    if _model is None:
        model = efficientnet_b3(weights=None)
        model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(idx_to_class_id))
        model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cuda" if torch.cuda.is_available() else "cpu")))
        model.eval()
        _model = model
    return _model

# === 예측 함수
def predict_from_image(image_bytes: bytes, threshold: float = 0.5) -> tuple[str | None, float]:
    try:
        # 이미지 로드 및 전처리
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = predict_transform(image).unsqueeze(0)

        model = load_model()
        device = next(model.parameters()).device
        tensor = tensor.to(device)

        # 추론
        with torch.no_grad():
            output = model(tensor)
            probs = torch.nn.functional.softmax(output, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)
            class_id = idx_to_class_id.get(str(pred_idx.item()))
            confidence = conf.item()

            if confidence < threshold:
                return None, confidence
            return class_id, confidence

    except Exception as e:
        print(f"❌ 예측 실패: {e}")
        return None, 0.0
