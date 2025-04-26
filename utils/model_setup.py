import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.models import efficientnet_b3, EfficientNet_B3_Weights

def create_model(num_classes: int, learning_rate: float = 1e-4, freeze_feature: bool = True):
    # Load pretrained EfficientNet-B3 weights
    weights = EfficientNet_B3_Weights.DEFAULT
    model = efficientnet_b3(weights=weights)

    # Replace classifier (Dropout + Linear) with custom structure
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.1),
        nn.Linear(model.classifier[1].in_features, num_classes)
    )

    # Move model to GPU (cuda:1 if multiple GPUs)
    device = torch.device("cuda:1" if torch.cuda.device_count() > 1 else "cuda")
    model = model.to(device)

    # Freeze feature extractor if specified
    if freeze_feature:
        for param in model.features.parameters():
            param.requires_grad = False

    # Define loss function
    criterion = nn.CrossEntropyLoss()

    # Define optimizer with layer-wise learning rates
    optimizer = optim.AdamW([
        {"params": model.features.parameters(), "lr": 1e-5},
        {"params": model.classifier.parameters(), "lr": learning_rate}
    ])

    return model, criterion, optimizer, device
