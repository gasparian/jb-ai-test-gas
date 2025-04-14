from src.model import SimpleCNN
from src.utils import load_mnist_data
from src.train import train_model

if __name__ == '__main__':
    trainloader, testloader = load_mnist_data()
    model = SimpleCNN()
    train_model(model, trainloader, testloader, epochs=5)