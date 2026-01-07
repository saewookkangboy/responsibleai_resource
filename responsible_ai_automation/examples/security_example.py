"""
보안 기능 사용 예제
"""

import yaml
from src.utils.security import SecurityManager, APIKeyManager, RateLimiter


def api_key_management_example():
    """API 키 관리 예제"""
    print("=== API 키 관리 예제 ===")

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # API 키 관리자 생성
    key_manager = APIKeyManager(config)

    # API 키 저장
    test_key = "test_api_key_12345"
    key_manager.store_api_key("test_service", test_key, encrypt=True)

    # API 키 조회
    retrieved_key = key_manager.get_api_key("test_service")
    print(f"저장된 키: {retrieved_key}")

    # API 키 로테이션
    new_key = key_manager.rotate_api_key("test_service")
    print(f"새 키: {new_key}")


def rate_limiting_example():
    """Rate Limiting 예제"""
    print("\n=== Rate Limiting 예제 ===")

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Rate Limiter 생성
    rate_limiter = RateLimiter(config)

    # 요청 허용 확인
    user_id = "user_123"
    for i in range(5):
        allowed = rate_limiter.is_allowed(user_id, limit=10)
        remaining = rate_limiter.get_remaining(user_id, limit=10)
        print(f"요청 {i+1}: 허용={allowed}, 남은 횟수={remaining}")


def security_manager_example():
    """통합 보안 관리 예제"""
    print("\n=== 통합 보안 관리 예제 ===")

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # 보안 관리자 생성
    security_manager = SecurityManager(config)

    # 요청 검증
    identifier = "192.168.1.1"
    api_key = "test_key"

    # API 키 저장
    security_manager.api_key_manager.store_api_key("api_service", api_key)

    # 요청 검증
    is_valid, message = security_manager.validate_request(
        identifier,
        api_key=api_key,
        required_key="api_service"
    )

    print(f"요청 검증: {is_valid}, 메시지: {message}")


if __name__ == "__main__":
    api_key_management_example()
    rate_limiting_example()
    security_manager_example()

