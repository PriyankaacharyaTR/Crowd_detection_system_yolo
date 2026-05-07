import os
import subprocess
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
from PIL import Image
import numpy as np

# ======================
# PATH
# ======================
video_path = "/content/drive/MyDrive/IDP/test1.mp4"
test_frames_path = "/content/drive/MyDrive/IDP/test1_frames"

# ======================
# STEP 1: EXTRACT ALL FRAMES
# ======================
os.makedirs(test_frames_path, exist_ok=True)

subprocess.run([
    "ffmpeg", "-y",
    "-i", video_path,
    "-vf", "fps=5",
    f"{test_frames_path}/frame_%04d.jpg"
])

print("✅ Frames extracted")

# ======================
# STEP 2: LOAD MOBILENET
# ======================
mobilenet = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
mobilenet.classifier = nn.Identity()
mobilenet.eval()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

# ======================
# STEP 3: LOAD MODEL
# ======================
class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(1280, 128, batch_first=True)
        self.fc = nn.Linear(128, 2)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out)

model = LSTMModel()
model.load_state_dict(torch.load("/content/drive/MyDrive/IDP/model.pth"))
model.eval()

# ======================
# STEP 4: ALL FRAMES → FEATURES
# ======================
frames = sorted(os.listdir(test_frames_path))
all_features = []

for img_name in frames:
    img_path = os.path.join(test_frames_path, img_name)

    img = Image.open(img_path).convert('RGB')
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        feat = mobilenet(img)

    all_features.append(feat.squeeze().numpy())

all_features = np.array(all_features)
print("Total frames:", len(all_features))

# ======================
# STEP 5: SEQUENCES OF 20
# ======================
sequences = []

for i in range(0, len(all_features) - 20 + 1, 20):
    sequences.append(all_features[i:i+20])

print("Total sequences:", len(sequences))

# ======================
# STEP 6: PREDICT EACH
# ======================
predictions = []

for seq in sequences:
    X_test = torch.tensor([seq], dtype=torch.float32)

    with torch.no_grad():
        output = model(X_test)

    pred = torch.argmax(output, dim=1).item()
    predictions.append(pred)

# ======================
# STEP 7: FINAL DECISION
# ======================
violence_count = sum(predictions)
nonviolence_count = len(predictions) - violence_count

print("Violence sequences:", violence_count)
print("NonViolence sequences:", nonviolence_count)

if violence_count > nonviolence_count:
    print("🚨 FINAL: Violence detected")
else:
    print("✅ FINAL: Non-Violence")
