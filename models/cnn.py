import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):

    def __init__(self, num_classes=4):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, num_classes)
    
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
    def run_train(self, train_loader, val_loader, criterion, optimizer, num_epochs=10):
        for epoch in range(num_epochs):
            avg_loss = 0
            for batch in train_loader:
                inputs, labels = batch
                inputs = inputs.float()
                labels = labels.float()
                optimizer.zero_grad()
                outputs = self.forward(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                avg_loss += loss
            print(f"Epoch {epoch} - Avg Train Loss: {avg_loss/len(train_loader)}")
            
            with torch.no_grad():
                self.eval()
                val_loss = 0
                for batch in val_loader:
                    inputs, labels = batch
                    inputs = inputs.float()
                    labels = labels.float()
                    outputs = self.forward(inputs).squeeze()
                    val_loss += criterion(outputs, labels)
                self.train()
                print(f"Epoch {epoch} - Val Loss: {val_loss/len(val_loader)}")
