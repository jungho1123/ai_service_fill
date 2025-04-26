import os, json
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

DATA_DIR = "C:/AI/ALL_DATA/PILL_DATA"
CLASS_IDX_JSON_PATH = os.path.join(DATA_DIR, "class_idx_to_id.json")

transform = transforms.Compose([
    transforms.Resize(300),           # 정사각형 Resize
    transforms.CenterCrop(300),  # 중앙 Crop
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def get_dataloaders(batch_size=24, num_workers=4):
    train_dataset = datasets.ImageFolder(os.path.join(DATA_DIR, "dataset_classification/train"), transform)
    valid_dataset = datasets.ImageFolder(os.path.join(DATA_DIR, "dataset_classification/valid"), transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
    valid_loader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)

    return train_loader, valid_loader, train_dataset.classes

def save_class_mapping(class_names):
    mapping = {str(i): name for i, name in enumerate(class_names)}
    with open(CLASS_IDX_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
