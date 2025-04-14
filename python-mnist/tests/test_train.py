import torch
from torch.utils.data import DataLoader, TensorDataset
from src.model import SimpleCNN
from src.train import train_model

def test_train_model():
    # Create dummy data
    dummy_inputs = torch.randn(10, 1, 28, 28)
    dummy_labels = torch.randint(0, 10, (10,))
    dummy_dataset = TensorDataset(dummy_inputs, dummy_labels)
    dummy_loader = DataLoader(dummy_dataset, batch_size=2)

    model = SimpleCNN()
    # Run training on dummy data for 1 epoch
    train_model(model, dummy_loader, dummy_loader, epochs=1)
    # Test passes if no errors occur