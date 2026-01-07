"""
FastAPI 기반 RESTful API 서버
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from datetime import datetime

from ..main import ResponsibleAIAutomationSystem
from ..monitoring.dashboard import MonitoringDashboard

app = FastAPI(
    title="Responsible AI Automation API",
    description="Responsible AI 평가 및 모니터링 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 보안 (간단한 예제)
security = HTTPBearer()
SYSTEM: Optional[ResponsibleAIAutomationSystem] = None


class EvaluationRequest(BaseModel):
    """평가 요청 모델"""
    X: List[List[float]]
    y: List[int]
    y_pred: List[int]
    sensitive_features: Optional[Dict[str, List]] = None


class ModelInitRequest(BaseModel):
    """모델 초기화 요청 모델"""
    model_type: str
    X: List[List[float]]
    y: List[int]
    sensitive_features: Optional[Dict[str, List]] = None


class UpdateRequest(BaseModel):
    """업데이트 요청 모델"""
    X: Optional[List[List[float]]] = None
    y: Optional[List[int]] = None
    sensitive_features: Optional[Dict[str, List]] = None


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    global SYSTEM
    try:
        SYSTEM = ResponsibleAIAutomationSystem("config.yaml")
    except Exception as e:
        print(f"시스템 초기화 실패: {e}")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Responsible AI Automation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "evaluate": "/evaluate",
            "metrics": "/metrics",
            "update": "/update"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/evaluate")
async def evaluate(request: EvaluationRequest):
    """Responsible AI 평가"""
    if SYSTEM is None:
        raise HTTPException(status_code=500, detail="시스템이 초기화되지 않았습니다.")
    
    try:
        X = np.array(request.X)
        y = np.array(request.y)
        y_pred = np.array(request.y_pred)
        
        sensitive_features = None
        if request.sensitive_features:
            sensitive_features = pd.DataFrame(request.sensitive_features)
        
        metrics = SYSTEM.evaluate(X, y, y_pred, sensitive_features)
        
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """최신 메트릭 조회"""
    if SYSTEM is None:
        raise HTTPException(status_code=500, detail="시스템이 초기화되지 않았습니다.")
    
    try:
        latest_metrics = SYSTEM.dashboard.get_latest_metrics()
        if latest_metrics is None:
            return {"status": "no_metrics", "message": "아직 평가된 메트릭이 없습니다."}
        
        return {
            "status": "success",
            "metrics": latest_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/history")
async def get_metrics_history(limit: int = 100):
    """메트릭 히스토리 조회"""
    if SYSTEM is None:
        raise HTTPException(status_code=500, detail="시스템이 초기화되지 않았습니다.")
    
    try:
        history = SYSTEM.dashboard.get_metrics_history(limit=limit)
        return {
            "status": "success",
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update")
async def update_model(request: UpdateRequest):
    """모델 업데이트"""
    if SYSTEM is None:
        raise HTTPException(status_code=500, detail="시스템이 초기화되지 않았습니다.")
    
    try:
        X = None
        y = None
        sensitive_features = None
        
        if request.X:
            X = np.array(request.X)
        if request.y:
            y = np.array(request.y)
        if request.sensitive_features:
            sensitive_features = pd.DataFrame(request.sensitive_features)
        
        SYSTEM.perform_update(X, y, sensitive_features)
        
        return {
            "status": "success",
            "message": "모델 업데이트가 완료되었습니다.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/update/conditions")
async def check_update_conditions():
    """업데이트 조건 확인"""
    if SYSTEM is None:
        raise HTTPException(status_code=500, detail="시스템이 초기화되지 않았습니다.")
    
    try:
        should_update = SYSTEM.check_update_conditions()
        return {
            "status": "success",
            "should_update": should_update,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

