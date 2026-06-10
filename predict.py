import sys
import os
import json
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

#  프로젝트 경로 설정
project_root = os.path.abspath(os.path.dirname(__file__))
model_dir = os.path.join(project_root, "models")  # 학습된 모델 저장 폴더
os.makedirs(model_dir, exist_ok=True)

#  최신 모델 가져오기
def get_latest_model():
    model_files = [f for f in os.listdir(model_dir) if f.startswith("model_epoch_") and f.endswith(".pth")]
    if not model_files:
        return None  # 저장된 모델이 없음
    model_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))  # 최신 순 정렬
    return os.path.join(model_dir, model_files[-1])

latest_model_path = get_latest_model()

if not latest_model_path:
    print(json.dumps({"error": " 최신 모델을 찾을 수 없습니다."}, ensure_ascii=False))
    sys.exit(1)

try:
    #  ResNet50 모델 로드
    model = models.resnet50(weights=None)
    model.fc = torch.nn.Sequential(
        torch.nn.Linear(model.fc.in_features, 512),
        torch.nn.ReLU(),
        torch.nn.Dropout(0.3),
        torch.nn.Linear(512, 10)  # 학습한 클래스 수 (10개)
    )

    model.load_state_dict(torch.load(latest_model_path, map_location=torch.device('cpu')))
    model.eval()
except Exception as e:
    print(json.dumps({"error": f" 모델 로드 실패: {str(e)}"}, ensure_ascii=False))
    sys.exit(1)

#  병해 코드 매핑
disease_mapping = {
    0: "정상",
    1: "고추마일드모틀바이러스병",
    2: "고추점무늬병",
    3: "딸기잿빛곰팡이병",
    4: "딸기흰가루병",
    5: "참외노균병",
    6: "참외흰가루병",
    7: "토마토잎곰팡이병",
    8: "토마토황화잎말이바이러스병",
    9: "포도노균병"
}

def predict(crop_name, image_path):
    try:
        if not os.path.exists(image_path):
            return " 이미지 파일을 찾을 수 없습니다."

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        image = Image.open(image_path).convert("RGB")
        image = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = model(image)
            probabilities = F.softmax(output, dim=1)

        probs = probabilities.squeeze().cpu().numpy()

        crop_valid_indices = {
            "고추": [0, 1, 2],
            "딸기": [0, 3, 4],
            "참외": [0, 5, 6],
            "토마토": [0, 7, 8],
            "포도": [0, 9]
        }


        valid_indices = crop_valid_indices[crop_name]
        valid_probs = {i: probs[i] for i in valid_indices}
        predicted_index = max(valid_probs, key=valid_probs.get)
        confidence_percent = valid_probs[predicted_index] * 100

        if confidence_percent < 60:
            return f"작물이 아닙니다. (정확도: {confidence_percent:.1f}%)"

        result = disease_mapping.get(predicted_index, "알 수 없음")

        return f"병해충 진단 결과: {result}, 정확도: {confidence_percent:.1f}%"

    except Exception as e:
        return f" 예측 오류: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 2:
        crop_name = sys.argv[1]
        image_path = sys.argv[2]
        print(predict(crop_name, image_path))
    else:
        print(json.dumps({"error": " 사용법: python predict.py [작물명] [이미지파일경로]"}, ensure_ascii=False))
