import torch.nn as nn
import torch.nn.functional as F

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        # Input: 1 channel (grayscale), 28x28 pixels
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3)  # Output: 32x26x26
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3) # Output: 64x24x24
        self.pool = nn.MaxPool2d(2)                   # Halves spatial dimensions
        # After conv1 -> pool: 32x13x13
        # After conv2 -> pool: 64x5x5
        self.fc1 = nn.Linear(64 * 5 * 5, 128)         # 1600 -> 128
        self.fc2 = nn.Linear(128, 10)                 # 10 classes (0-9)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # 32x13x13
        x = self.pool(F.relu(self.conv2(x)))  # 64x5x5
        x = x.view(-1, 64 * 5 * 5)            # Flatten to 1600
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x
