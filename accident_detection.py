import os
import subprocess
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
from PIL import Image
import numpy as np

# ======================
# CONFIGURATION & PATHS
# ======================
# Change this to the path of the video you want to test
video_input_path = "/content/drive/MyDrive/IDP/test1.mp4"
temp_frames_path = "/content/temp_frames"
model_save_path = "/content/drive/MyDrive/IDP/training2/accident_model/accident_model_run1.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(temp_frames_path, exist_ok=True)

# ======================
# STEP 1: EXTRACT FRAMES
# ======================
# Extracting at 8 FPS to match your sequence logic
subprocess.run([
    "ffmpeg", "-y",
    "-i", video_input_path,
    "-vf", "fps=8",
    f"{temp_frames_path}/frame_%04d.jpg"
], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

print("✅ Step 1: Frames extracted from video.")

# ======================
# STEP 2: LOAD MOBILENET (Feature Extractor)
# ======================
mobilenet = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
mobilenet.classifier = nn.Identity() # Remove classification layer to get 1280 features
mobilenet.to(device)
mobilenet.eval()

img_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# ======================
# STEP 3: LOAD ACCIDENT LSTM MODEL
# ======================
class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        # Hidden size 256 to match your training session
        self.lstm = nn.LSTM(1280, 256, batch_first=True)
        self.fc = nn.Linear(256, 2)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :] # Final hidden state
        return self.fc(out)

model = LSTMModel().to(device)
model.load_state_dict(torch.load(model_save_path, map_location=device))
model.eval()
print("✅ Step 2: Trained LSTM model loaded.")

# ======================
# STEP 4: EXTRACT FEATURES
# ======================
frame_files = sorted(os.listdir(temp_frames_path))
all_features = []

print(f"Processing {len(frame_files)} frames...")
for img_name in frame_files:
    img_path = os.path.join(temp_frames_path, img_name)
    img = Image.open(img_path).convert('RGB')
    img_tensor = img_transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        feature_vector = mobilenet(img_tensor)

    all_features.append(feature_vector.squeeze().cpu().numpy())

all_features = np.array(all_features)

# ======================
# STEP 5: CREATE SEQUENCES & PREDICT
# ======================
# We look at windows of 20 frames (2.5 seconds at 8fps)
accident_votes = 0
sequence_length = 20
step_size = 5 # Overlap
total_sequences = 0

print("Analyzing sequences...")
for i in range(0, len(all_features) - sequence_length + 1, step_size):
    seq = all_features[i : i + sequence_length]
    X_input = torch.tensor([seq], dtype=torch.float32).to(device)

    with torch.no_grad():
        output = model(X_input)
        probs = torch.softmax(output, dim=1)

        # Index 1 = Accident, Index 0 = No Accident
        accident_prob = probs[0][1].item()

        if accident_prob > 0.5: # Probability threshold
            accident_votes += 1

    total_sequences += 1

# ======================
# STEP 6: FINAL REPORT
# ======================
print("\n" + "="*30)
print("ACCIDENT DETECTION REPORT")
print("="*30)
print(f"Total Sequences Analyzed: {total_sequences}")
print(f"Accident Sequences Detected: {accident_votes}")

# Final decision: if more than 1 sequence shows an accident
if accident_votes >= 2:
    print("\n🚨 RESULT: ACCIDENT DETECTED")
else:
    print("\n✅ RESULT: NO ACCIDENT DETECTED")
print("="*30)

# Cleanup
import shutil
shutil.rmtree(temp_frames_path)
