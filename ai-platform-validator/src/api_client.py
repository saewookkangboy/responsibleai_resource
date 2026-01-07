"""
통합 API 클라이언트 - 다양한 생성형 AI 플랫폼 지원
"""
import os
from typing import Optional, Dict, Any
from enum import Enum

try:
    import openai
    from anthropic import Anthropic
    import google.generativeai as genai
except ImportError:
    print("경고: 일부 라이브러리가 설치되지 않았습니다. pip install -r requirements.txt 실행 필요")

class AIPlatform(Enum):
    """지원하는 AI 플랫폼"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"

class APIClient:
    """다양한 생성형 AI 플랫폼과 통신하는 통합 클라이언트"""
    
    def __init__(self, platform: AIPlatform, api_key: Optional[str] = None):
        self.platform = platform
        self.api_key = api_key or self._get_api_key_from_env()
        self._initialize_client()
    
    def _get_api_key_from_env(self) -> str:
        """환경변수에서 API 키 가져오기"""
        key_map = {
            AIPlatform.OPENAI: "OPENAI_API_KEY",
            AIPlatform.ANTHROPIC: "ANTHROPIC_API_KEY",
            AIPlatform.GOOGLE: "GOOGLE_API_KEY",
            AIPlatform.AZURE_OPENAI: "AZURE_OPENAI_API_KEY",
        }
        key_name = key_map.get(self.platform)
        if not key_name:
            raise ValueError(f"지원하지 않는 플랫폼: {self.platform}")
        api_key = os.getenv(key_name)
        if not api_key:
            raise ValueError(f"{key_name} 환경변수가 설정되지 않았습니다.")
        return api_key
    
    def _initialize_client(self):
        """플랫폼별 클라이언트 초기화"""
        if self.platform == AIPlatform.OPENAI:
            self.client = openai.OpenAI(api_key=self.api_key)
        elif self.platform == AIPlatform.ANTHROPIC:
            self.client = Anthropic(api_key=self.api_key)
        elif self.platform == AIPlatform.GOOGLE:
            genai.configure(api_key=self.api_key)
            self.client = genai
        elif self.platform == AIPlatform.AZURE_OPENAI:
            self.client = openai.AzureOpenAI(
                api_key=self.api_key,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
    
    def generate(self, prompt: str, model: str = None, max_tokens: int = 1000, 
                 temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """텍스트 생성 요청"""
        if self.platform == AIPlatform.OPENAI:
            return self._generate_openai(prompt, model, max_tokens, temperature, **kwargs)
        elif self.platform == AIPlatform.ANTHROPIC:
            return self._generate_anthropic(prompt, model, max_tokens, temperature, **kwargs)
        elif self.platform == AIPlatform.GOOGLE:
            return self._generate_google(prompt, model, max_tokens, temperature, **kwargs)
        elif self.platform == AIPlatform.AZURE_OPENAI:
            return self._generate_azure_openai(prompt, model, max_tokens, temperature, **kwargs)
    
    def _generate_openai(self, prompt: str, model: str, max_tokens: int, 
                         temperature: float, **kwargs) -> Dict[str, Any]:
        """OpenAI API 호출"""
        model = model or "gpt-4"
        response = self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens, temperature=temperature, **kwargs
        )
        return {
            "text": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "platform": "openai"
        }
    
    def _generate_anthropic(self, prompt: str, model: str, max_tokens: int,
                           temperature: float, **kwargs) -> Dict[str, Any]:
        """Anthropic API 호출"""
        model = model or "claude-3-opus-20240229"
        response = self.client.messages.create(
            model=model, max_tokens=max_tokens, temperature=temperature,
            messages=[{"role": "user", "content": prompt}], **kwargs
        )
        return {
            "text": response.content[0].text,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "platform": "anthropic"
        }
    
    def _generate_google(self, prompt: str, model: str, max_tokens: int,
                        temperature: float, **kwargs) -> Dict[str, Any]:
        """Google AI API 호출"""
        model = model or "gemini-pro"
        model_instance = self.client.GenerativeModel(model)
        response = model_instance.generate_content(
            prompt, generation_config={
                "max_output_tokens": max_tokens, "temperature": temperature,
            }, **kwargs
        )
        return {"text": response.text, "model": model, "platform": "google"}
    
    def _generate_azure_openai(self, prompt: str, model: str, max_tokens: int,
                              temperature: float, **kwargs) -> Dict[str, Any]:
        """Azure OpenAI API 호출"""
        model = model or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        response = self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens, temperature=temperature, **kwargs
        )
        return {
            "text": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "platform": "azure_openai"
        }
