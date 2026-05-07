import os, subprocess
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
from PIL import Image
import numpy as np

# ======================
# DEVICE
# ======================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ======================
# PATHS
# ======================
video_path = "/content/drive/MyDrive/IDP/test.mp4"
frames_path = "/content/drive/MyDrive/IDP/training2/tes/frames"

os.makedirs(frames_path, exist_ok=True)

# ======================
# STEP 1: EXTRACT FRAMES
# ======================
subprocess.run([
    "ffmpeg","-y","-i",video_path,
    "-vf","fps=8",
    f"{frames_path}/frame_%04d.jpg"
])

# ======================
# STEP 2: LOAD MODELS
# ======================
mobilenet = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
mobilenet.classifier = nn.Identity()
mobilenet = mobilenet.to(device)
mobilenet.eval()

class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(1280,256,batch_first=True)
        self.fc = nn.Linear(256,2)

    def forward(self,x):
        out,_ = self.lstm(x)
        out = out[:,-1,:]
        return self.fc(out)

model = LSTMModel().to(device)
model.load_state_dict(torch.load("/content/drive/MyDrive/IDP/training2/model/model_final.pth"))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

# ======================
# STEP 3: FRAMES → FEATURES
# ======================
frames = sorted(os.listdir(frames_path))
features = []

for img_name in frames:
    img = Image.open(os.path.join(frames_path,img_name)).convert('RGB')
    img = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        f = mobilenet(img)

    features.append(f.squeeze().cpu().numpy())

features = np.array(features)

# ======================
# STEP 4: SEQUENCES (OVERLAP)
# ======================
sequences = []
for i in range(0, len(features)-20+1, 5):
    sequences.append(features[i:i+20])

# ======================
# STEP 5: PREDICTION + CONFIDENCE
# ======================
violence_scores = []

for seq in sequences:
    X_test = torch.tensor([seq], dtype=torch.float32).to(device)

    with torch.no_grad():
        out = model(X_test)

    probs = torch.softmax(out, dim=1)
    violence_prob = probs[0][1].item()

    violence_scores.append(violence_prob)

# ======================
# FINAL DECISION
# ======================
avg_score = sum(violence_scores) / len(violence_scores)
max_score = max(violence_scores)

print(f"Average confidence: {avg_score:.2f}")
print(f"Max confidence: {max_score:.2f}")

if max_score > 0.6:
    print(f"🚨 Violence detected ({max_score:.2f})")
else:
    print(f"✅ Non-Violence ({1-max_score:.2f})")
