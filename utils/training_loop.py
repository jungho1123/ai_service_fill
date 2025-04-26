import torch
from tqdm import tqdm
import matplotlib.pyplot as plt
import os


def train_and_validate(model, optimizer, criterion, train_loader, valid_loader, device, start_epoch=0, num_epochs=10,
                       best_val_acc=0.0, early_stopping=True, patience=3, delta=0.001, scaler=None):
    # === 히스토리 초기화 ===
    train_loss_hist, valid_loss_hist = [], []
    train_acc_hist, valid_acc_hist = [], []

    best_loss = float("inf")  # Early stopping을 위한 최소 validation loss 초기값
    patience_counter = 0       # Early stopping 카운터

    for epoch in range(start_epoch, num_epochs):
        # === 특정 epoch에 feature layer의 requires_grad를 True로 설정하여 fine-tuning 시작 ===
        if epoch == 3:
            print("[INFO] Unfreezing feature layers...")
            for param in model.features.parameters():
                param.requires_grad = True

        model.train()  # 학습 모드 전환
        running_loss, correct = 0.0, 0

        loop = tqdm(train_loader, desc=f"Epoch [{epoch+1}/{num_epochs}]")  # tqdm을 이용한 배치 진행률 표시
        for inputs, labels in loop:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()  # gradient 초기화

            if scaler:
                # === AMP 자동 혼합 정밀도 적용 ===
                with torch.cuda.amp.autocast():
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()  # gradient scaling 적용
                scaler.step(optimizer)
                scaler.update()
            else:
                # === 일반 float32 학습 경로 ===
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

            # === 손실 및 정확도 누적 계산 ===
            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            loop.set_postfix(loss=loss.item())  # 현재 배치 손실 표시

        # === epoch 단위 평균 손실 및 정확도 계산 ===
        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_acc = correct / len(train_loader.dataset)
        train_loss_hist.append(epoch_loss)
        train_acc_hist.append(epoch_acc)

        # === 검증 모드 ===
        model.eval()
        valid_loss, correct = 0.0, 0
        with torch.no_grad():  # gradient 비계산 모드
            for inputs, labels in valid_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                valid_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                correct += (preds == labels).sum().item()

        val_loss = valid_loss / len(valid_loader.dataset)
        val_acc = correct / len(valid_loader.dataset)
        valid_loss_hist.append(val_loss)
        valid_acc_hist.append(val_acc)

        print(f"\n Epoch {epoch+1} 완료 | Train Acc: {epoch_acc:.4f} | Val Acc: {val_acc:.4f} | Val Loss: {val_loss:.4f}")

        # === Early Stopping 조건 확인 ===
        if early_stopping:
            if best_loss - val_loss < delta:
                patience_counter += 1
                print(f"[INFO] EarlyStopping counter: {patience_counter}/{patience}")
                if patience_counter >= patience:
                    print("[INFO] Early stopping triggered.")
                    break
            else:
                best_loss = val_loss
                patience_counter = 0

        # === 현재 모델이 가장 좋은 성능을 보일 경우 저장 ===
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "best_model.pth")
            print(" Best model saved!\n")

    # === 학습 곡선 시각화 ===
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(train_loss_hist, label="Train Loss")
    plt.plot(valid_loss_hist, label="Valid Loss")
    plt.title("Loss Curve")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(train_acc_hist, label="Train Acc")
    plt.plot(valid_acc_hist, label="Valid Acc")
    plt.title("Accuracy Curve")
    plt.legend()

    plt.tight_layout()
    plt.savefig("training_curve.png")  # 결과 저장
    plt.show()
