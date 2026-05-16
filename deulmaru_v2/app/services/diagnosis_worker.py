from __future__ import annotations

import base64
import io
import json
import sys

CLASS_LABELS = {
    0: "정상",
    1: "고추탄저병",
    2: "고추마일드모틀바이러스병",
    3: "딸기잿빛곰팡이병",
    4: "딸기흰가루병",
    5: "참외노균병",
    6: "참외흰가루병",
    7: "토마토잎곰팡이병",
    8: "토마토황화잎말이바이러스병",
    9: "포도탄저병",
}

CROP_CLASS_INDICES = {
    "고추": [0, 1, 2],
    "딸기": [0, 3, 4],
    "참외": [0, 5, 6],
    "토마토": [0, 7, 8],
    "포도": [0, 9],
}


def write_json(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        crop_name = payload["crop"]
        filename = payload["filename"]
        size_kb = payload["size_kb"]
        model_path = payload["model_path"]
        image_bytes = base64.b64decode(payload["image_base64"])

        import torch
        import torch.nn.functional as F
        from PIL import Image, UnidentifiedImageError
        from torchvision import models, transforms

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except UnidentifiedImageError:
            write_json({"ok": False, "message": "이미지 파일을 읽을 수 없습니다. 다른 이미지를 선택해 주세요."})
            return 0

        try:
            state_dict = torch.load(model_path, map_location=torch.device("cpu"), weights_only=True)
        except TypeError:
            state_dict = torch.load(model_path, map_location=torch.device("cpu"))

        model = models.resnet50(weights=None)
        if any(key.startswith("fc.3.") for key in state_dict):
            model.fc = torch.nn.Sequential(
                torch.nn.Linear(model.fc.in_features, 512),
                torch.nn.ReLU(),
                torch.nn.Dropout(0.3),
                torch.nn.Linear(512, len(CLASS_LABELS)),
            )
        else:
            model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_LABELS))

        model.load_state_dict(state_dict)
        model.eval()

        transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

        tensor = transform(image).unsqueeze(0)
        with torch.no_grad():
            probabilities = F.softmax(model(tensor), dim=1).squeeze()

        valid_indices = CROP_CLASS_INDICES.get(crop_name, list(CLASS_LABELS.keys()))
        predicted_index = max(valid_indices, key=lambda index: float(probabilities[index]))
        confidence = round(float(probabilities[predicted_index]) * 100, 1)
        disease = CLASS_LABELS.get(predicted_index, "추가 확인 필요")

        if predicted_index == 0:
            next_action = "정상 가능성이 높습니다. 재배 환경과 잎·열매 상태를 주기적으로 관찰하세요."
        elif confidence < 60:
            next_action = "신뢰도가 낮습니다. 다른 각도의 사진으로 다시 진단하고 NCPMS 정보를 함께 확인하세요."
        else:
            next_action = "NCPMS 병해충 정보와 현장 증상을 함께 확인한 뒤 방제 여부를 결정하세요."

        write_json(
            {
                "ok": True,
                "crop": crop_name,
                "filename": filename,
                "size_kb": size_kb,
                "disease": disease,
                "confidence": confidence,
                "next_action": next_action,
                "model_mode": "pytorch",
            }
        )
        return 0
    except Exception as exc:
        write_json({"ok": False, "message": f"모델 추론 중 오류가 발생했습니다: {exc}"})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
