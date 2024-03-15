import torch
import argparse
from torch.utils.data import Dataset, DataLoader
from torch import nn
from torch import optim
from torch.optim.lr_scheduler import StepLR
from dataset import EEGDataset, NewEEGDataset, generate_dataloaders
import numpy as np
from models.mlp import MLP
from models.rnn import RNN
from models.cnn import CNN
from models.lstm import LSTM
from models.eeg_net import EEGNet
from models.gru import GRU
from models.transformer import Transformer
from models.cnn_1d import CNN_1D
from models.resnet_1d import ResNet_1D
# from models.mamba_eeg import MambaEEG
from data_utils.timeseries_transforms import Composite, Stacking, Trimming, Resample, GaussianNoise, LowPassFilter, Scaling, MaxPooling
import matplotlib.pyplot as plt
# from models.mamba_eeg_net import MambaDepthWiseEEG

from training_utils.loops import run_train, run_testing


def train(experiment_name, num_epochs, batch_size, lr, transforms, device):

    if experiment_name == "mlp":

        if transforms:
            pass # apply transforms associated with specific model
        else:
            transform = None

        train_dataset = EEGDataset(train=True, transform=transform, device=device)
        test_dataset = EEGDataset(train=False, transform=transform, device=device)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()
       
        model = MLP([1000 * 22, 1024, 128, 4]).to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr)
        model.run_train(train_loader, test_loader, criterion, optimizer, num_epochs=num_epochs)

    elif experiment_name == "cnn":

        if transforms:
            train_transform = Composite([
                Trimming(0,750),
                MaxPooling(2),
                GaussianNoise(),
            ])
            test_transform = Composite([
                Trimming(0,750),
                MaxPooling(2),
            ])
        else:
            train_transform = None
            test_transform = None

        train_dataset = EEGDataset(train=True, transform=train_transform)
        test_dataset = EEGDataset(train=False, transform=test_transform)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()
        model = CNN(device=device)
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-1)
        scheduler = StepLR(optimizer, step_size=25, gamma=0.5)
        train_losses, val_losses, train_accuracies, val_accuracies = run_train(model, train_loader, test_loader, criterion, optimizer, scheduler, num_epochs=num_epochs, unsqueeze=True)

        return {
            "train_losses": train_losses,
            "test_losses": val_losses,
            "train_accuracies": train_accuracies,
            "test_accuracies": val_accuracies
        }
    
    elif experiment_name == "cnn_1d":
      
        if transforms:
            transform = None
        else:
            transform = None
        
        train_loader, val_loader, test_loader = generate_dataloaders(
            val=0.1, batch_size=batch_size, transform=transform
        )

        model = CNN_1D(device=device)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=5e-1)
        scheduler = StepLR(optimizer, step_size=25, gamma=0.5)

        train_losses, val_losses, train_accuracies, val_accuracies = run_train(model, train_loader, val_loader, criterion, optimizer, scheduler, num_epochs=num_epochs, unsqueeze=False)

        test_accuracy = run_testing(model, test_loader, criterion, unsqueeze=False)
        print(f"Test accuracy: {test_accuracy:.2f}%")

        return {
            "train_losses": train_losses,
            "val_losses": val_losses,
            "train_accuracies": train_accuracies,
            "val_accuracies": val_accuracies
        }

    elif experiment_name == "resnet_1d":
            
        if transforms:
            transform = None
        else:
            transform = None
        
        train_loader, val_loader, test_loader = generate_dataloaders(
            val=0.1, batch_size=batch_size, transform=transform
        )

        model = ResNet_1D(device=device)

        criterion = nn.CrossEntropyLoss()
        # optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=5e-1)
        optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-1)
        scheduler = StepLR(optimizer, step_size=25, gamma=0.1)

        train_losses, val_losses, train_accuracies, val_accuracies = run_train(model, train_loader, val_loader, criterion, optimizer, scheduler, num_epochs=num_epochs, unsqueeze=False)

        test_accuracy = run_testing(model, test_loader, criterion, unsqueeze=False)
        print(f"Test accuracy: {test_accuracy:.2f}%")

        return {
            "train_losses": train_losses,
            "val_losses": val_losses,
            "train_accuracies": train_accuracies,
            "val_accuracies": val_accuracies
        }


    elif experiment_name == "rnn":

        if transforms:
            pass # apply transforms associated with specific model
        else:
            transform = None

        train_dataset = EEGDataset(train=True, transform=transform, device=device)
        test_dataset = EEGDataset(train=False, transform=transform, device=device)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()

        model = RNN().to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr)
        model.run_train(train_loader, test_loader, criterion, optimizer, num_epochs=num_epochs)

    elif experiment_name == "lstm":

        if transforms:
            pass # apply transforms associated with specific model
        else:
            transform = None

        train_dataset = EEGDataset(train=True, transform=transform, device=device)
        test_dataset = EEGDataset(train=False, transform=transform, device=device)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()
        
        model = LSTM().to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr)
        model.run_train(train_loader, test_loader, criterion, optimizer, num_epochs=num_epochs)

    elif experiment_name == "eegnet":

        if transforms:
            pass # apply transforms associated with specific model
        else:
            transform = None

        train_dataset = EEGDataset(train=True, transform=transform, device=device)
        test_dataset = EEGDataset(train=False, transform=transform, device=device)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()
        
        model = EEGNet().to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr)
        model.run_train(train_loader, test_loader, criterion, optimizer, num_epochs=num_epochs)

    elif experiment_name == "gru":

        if transforms:
            pass # apply transforms associated with specific model
        else:
            transform = None

        train_dataset = EEGDataset(train=True, transform=transform, device=device)
        test_dataset = EEGDataset(train=False, transform=transform, device=device)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()
        
        model = GRU().to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr)
        model.run_train(train_loader, test_loader, criterion, optimizer, num_epochs=num_epochs)

    elif experiment_name == "transformer":

        if transforms:
            pass # apply transforms associated with specific model
        else:
            transform = None

        train_dataset = EEGDataset(train=True, transform=transform, device=device)
        test_dataset = EEGDataset(train=False, transform=transform, device=device)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()
        
        model = Transformer().to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr)
        model.run_train(train_loader, test_loader, criterion, optimizer, num_epochs=num_epochs)
        
    elif experiment_name == "mamba":

        if transforms:
            pass
        else:
            transform = None
        
        train_dataset = EEGDataset(train=True, transform=transform, device=device)
        test_dataset = EEGDataset(train=False, transform=transform, device=device)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()
        
        model = MambaEEG().to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr)
        model.run_train(train_loader, test_loader, criterion, optimizer, num_epochs=num_epochs)
        
    elif experiment_name == "mamba_eeg":

        if transforms:
            pass
        else:
            transform = None
        
        train_dataset = EEGDataset(train=True, transform=transform, device=device)
        test_dataset = EEGDataset(train=False, transform=transform, device=device)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        criterion = nn.CrossEntropyLoss()
        
        model = MambaDepthWiseEEG().to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr)
        model.run_train(train_loader, test_loader, criterion, optimizer, num_epochs=num_epochs)
    
        
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Train EEG classification models')
    parser.add_argument('experiment', type=str, help='Name of the experiment/model to train')
    parser.add_argument('--num_epochs', type=int, default=1000, help='Number of epochs for training (default: 10)')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size for training (default: 64)')
    parser.add_argument('--lr', type=float, default=0.000003, help='Learning rate for optimizer (default: 0.00001)')
    parser.add_argument('--device', type=str, default="cuda", help='Apply data transformations (default: cpu)')
    parser.add_argument('--transforms', action='store_true', help='Apply data transformations (default: False)')
    
    args = parser.parse_args()
    
    stats = train(args.experiment, args.num_epochs, args.batch_size, args.lr, args.transforms, args.device)
    
    if stats:
        train_losses = stats["train_losses"]
        val_losses = stats["val_losses"]
        train_accuracies = stats["train_accuracies"]
        val_accuracies = stats["val_accuracies"]

        plt.figure()
        plt.plot(train_losses, label="Average train Loss")
        plt.plot(val_losses, label="Average validation Loss")
        plt.xlabel("Epoch")
        plt.legend()
        plt.show()

        plt.figure()
        plt.plot(train_accuracies, label="Train Accuracy")
        plt.plot(val_accuracies, label="Validation Accuracy")
        plt.xlabel("Epoch")
        plt.legend()
        plt.show()