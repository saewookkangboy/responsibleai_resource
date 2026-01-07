"""
자동 하이퍼파라미터 튜닝 모듈
"""

from typing import Dict, Any, Optional, Callable
import logging

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

try:
    from ray import tune
    RAY_TUNE_AVAILABLE = True
except ImportError:
    RAY_TUNE_AVAILABLE = False


class HyperparameterTuner:
    """하이퍼파라미터 튜닝 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 튜닝 설정
        """
        self.config = config.get("hyperparameter_tuning", {})
        self.method = self.config.get("method", "optuna")
        self.n_trials = self.config.get("n_trials", 100)
        self.logger = logging.getLogger(__name__)

    def tune_with_optuna(
        self,
        objective_func: Callable,
        search_space: Dict[str, Any],
        direction: str = "maximize"
    ) -> Optional[Dict[str, Any]]:
        """
        Optuna를 사용한 하이퍼파라미터 튜닝

        Args:
            objective_func: 목적 함수
            search_space: 검색 공간 정의
            direction: 최적화 방향 ("maximize" 또는 "minimize")

        Returns:
            최적 하이퍼파라미터 또는 None
        """
        if not OPTUNA_AVAILABLE:
            self.logger.error("Optuna가 설치되지 않았습니다. pip install optuna를 실행하세요.")
            return None

        def objective(trial):
            # 검색 공간에서 하이퍼파라미터 샘플링
            params = {}
            for param_name, param_config in search_space.items():
                param_type = param_config.get("type", "float")
                
                if param_type == "float":
                    params[param_name] = trial.suggest_float(
                        param_name,
                        param_config.get("low", 0.0),
                        param_config.get("high", 1.0),
                        log=param_config.get("log", False)
                    )
                elif param_type == "int":
                    params[param_name] = trial.suggest_int(
                        param_name,
                        param_config.get("low", 1),
                        param_config.get("high", 100),
                        log=param_config.get("log", False)
                    )
                elif param_type == "categorical":
                    params[param_name] = trial.suggest_categorical(
                        param_name,
                        param_config.get("choices", [])
                    )

            # 목적 함수 실행
            return objective_func(params)

        study = optuna.create_study(direction=direction)
        study.optimize(objective, n_trials=self.n_trials)

        best_params = study.best_params
        best_value = study.best_value

        self.logger.info(f"최적 하이퍼파라미터: {best_params}")
        self.logger.info(f"최적 값: {best_value}")

        return {
            "best_params": best_params,
            "best_value": best_value,
            "study": study
        }

    def tune_with_ray(
        self,
        objective_func: Callable,
        search_space: Dict[str, Any],
        num_samples: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Ray Tune을 사용한 하이퍼파라미터 튜닝

        Args:
            objective_func: 목적 함수
            search_space: 검색 공간 정의
            num_samples: 샘플 수 (None이면 n_trials 사용)

        Returns:
            최적 하이퍼파라미터 또는 None
        """
        if not RAY_TUNE_AVAILABLE:
            self.logger.error("Ray Tune이 설치되지 않았습니다. pip install ray[tune]를 실행하세요.")
            return None

        if num_samples is None:
            num_samples = self.n_trials

        # Ray Tune 검색 공간 변환
        ray_search_space = {}
        for param_name, param_config in search_space.items():
            param_type = param_config.get("type", "float")
            
            if param_type == "float":
                ray_search_space[param_name] = tune.uniform(
                    param_config.get("low", 0.0),
                    param_config.get("high", 1.0)
                )
            elif param_type == "int":
                ray_search_space[param_name] = tune.randint(
                    param_config.get("low", 1),
                    param_config.get("high", 100)
                )
            elif param_type == "categorical":
                ray_search_space[param_name] = tune.choice(
                    param_config.get("choices", [])
                )

        def trainable(config):
            return objective_func(config)

        analysis = tune.run(
            trainable,
            config=ray_search_space,
            num_samples=num_samples,
            metric="score",
            mode="max"
        )

        best_config = analysis.get_best_config(metric="score", mode="max")
        best_result = analysis.get_best_trial(metric="score", mode="max")

        self.logger.info(f"최적 하이퍼파라미터: {best_config}")
        self.logger.info(f"최적 값: {best_result.last_result['score']}")

        return {
            "best_params": best_config,
            "best_value": best_result.last_result["score"],
            "analysis": analysis
        }

    def tune(
        self,
        objective_func: Callable,
        search_space: Dict[str, Any],
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        하이퍼파라미터 튜닝 수행

        Args:
            objective_func: 목적 함수
            search_space: 검색 공간 정의
            **kwargs: 추가 파라미터

        Returns:
            최적 하이퍼파라미터 또는 None
        """
        if self.method == "optuna":
            direction = kwargs.get("direction", "maximize")
            return self.tune_with_optuna(objective_func, search_space, direction)
        elif self.method == "ray":
            return self.tune_with_ray(objective_func, search_space, **kwargs)
        else:
            self.logger.error(f"지원하지 않는 튜닝 방법: {self.method}")
            return None

