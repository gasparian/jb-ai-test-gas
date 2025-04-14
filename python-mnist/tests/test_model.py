import pytest
import torch
from src.model import SimpleCNN

def test_model_instantiation():
    model = SimpleCNN()
    assert isinstance(model, SimpleCNN)

def test_model_forward():
    model = SimpleCNN()
    sample_input = torch.randn(1, 1, 28, 28)  # Batch of 1, 1 channel, 28x28
    output = model(sample_input)
    assert output.shape == (1, 10)  # Output should be batch_size x num_classes