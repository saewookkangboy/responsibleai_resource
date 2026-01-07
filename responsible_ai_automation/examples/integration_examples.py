"""
ML 프레임워크 통합 예제
"""

import numpy as np
import pandas as pd
from main import ResponsibleAIAutomationSystem

# TensorFlow/Keras 예제
def tensorflow_example():
    """TensorFlow/Keras 모델 통합 예제"""
    try:
        import tensorflow as tf
        from tensorflow import keras
        
        # 시스템 초기화
        system = ResponsibleAIAutomationSystem("config.yaml")
        
        # 간단한 Keras 모델 생성
        model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(10,)),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        # 데이터 준비
        X = np.random.rand(100, 10)
        y = np.random.randint(0, 2, 100)
        sensitive_features = pd.DataFrame({
            "gender": np.random.choice(["M", "F"], 100),
        })
        
        # 모델 학습
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        model.fit(X, y, epochs=10, verbose=0)
        
        # 시스템에 모델 등록
        system.initialize_model(model, X, y, sensitive_features)
        
        # 평가 수행
        y_pred = model.predict(X, verbose=0)
        y_pred = (y_pred > 0.5).astype(int).flatten()
        metrics = system.evaluate(X, y, y_pred, sensitive_features)
        
        print("TensorFlow/Keras 모델 평가 완료")
        print(f"Responsible AI 점수: {metrics['overall_responsible_ai_score']:.3f}")
        
    except ImportError:
        print("TensorFlow가 설치되지 않았습니다.")


# PyTorch 예제
def pytorch_example():
    """PyTorch 모델 통합 예제"""
    try:
        import torch
        import torch.nn as nn
        
        # 시스템 초기화
        system = ResponsibleAIAutomationSystem("config.yaml")
        
        # 간단한 PyTorch 모델 생성
        class SimpleModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(10, 64)
                self.fc2 = nn.Linear(64, 32)
                self.fc3 = nn.Linear(32, 1)
                self.sigmoid = nn.Sigmoid()
            
            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                x = self.sigmoid(self.fc3(x))
                return x
        
        model = SimpleModel()
        
        # 데이터 준비
        X = np.random.rand(100, 10).astype(np.float32)
        y = np.random.randint(0, 2, 100)
        sensitive_features = pd.DataFrame({
            "gender": np.random.choice(["M", "F"], 100),
        })
        
        # 모델 학습
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(model.parameters())
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y).unsqueeze(1)
        
        for epoch in range(10):
            optimizer.zero_grad()
            outputs = model(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
        
        # 시스템에 모델 등록
        system.initialize_model(model, X, y, sensitive_features)
        
        # 평가 수행
        model.eval()
        with torch.no_grad():
            outputs = model(torch.FloatTensor(X))
            y_pred = (outputs > 0.5).numpy().flatten()
        
        metrics = system.evaluate(X, y, y_pred, sensitive_features)
        
        print("PyTorch 모델 평가 완료")
        print(f"Responsible AI 점수: {metrics['overall_responsible_ai_score']:.3f}")
        
    except ImportError:
        print("PyTorch가 설치되지 않았습니다.")


if __name__ == "__main__":
    print("=== TensorFlow/Keras 예제 ===")
    tensorflow_example()
    
    print("\n=== PyTorch 예제 ===")
    pytorch_example()

