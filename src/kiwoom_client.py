"""
키움증권 REST API 클라이언트
OAuth 인증 및 토큰 관리를 담당합니다.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging


class KiwoomAPIClient:
    """키움증권 REST API 클라이언트"""

    # API 도메인
    PRODUCTION_DOMAIN = "https://api.kiwoom.com"
    MOCK_DOMAIN = "https://mockapi.kiwoom.com"

    # API 엔드포인트
    TOKEN_ENDPOINT = "/oauth2/token"

    def __init__(self, appkey: str, secretkey: str, environment: str = "mock"):
        """
        Args:
            appkey: 발급받은 App Key
            secretkey: 발급받은 Secret Key
            environment: 'production' 또는 'mock' (기본값: 'mock')
        """
        self.appkey = appkey
        self.secretkey = secretkey
        self.environment = environment

        # 환경에 따른 도메인 설정
        self.base_url = (
            self.PRODUCTION_DOMAIN if environment == "production"
            else self.MOCK_DOMAIN
        )

        # 토큰 정보
        self.access_token: Optional[str] = None
        self.token_type: Optional[str] = None
        self.expires_dt: Optional[str] = None

        # 로거 설정
        self.logger = logging.getLogger(__name__)

    def get_access_token(self) -> Tuple[bool, Dict]:
        """
        접근 토큰 발급 (au10001)

        Returns:
            Tuple[bool, Dict]: (성공 여부, 응답 데이터 또는 에러 정보)
        """
        url = f"{self.base_url}{self.TOKEN_ENDPOINT}"

        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }

        payload = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "secretkey": self.secretkey
        }

        try:
            self.logger.info(f"토큰 발급 요청 시작 - 환경: {self.environment}")
            self.logger.debug(f"요청 URL: {url}")

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )

            self.logger.info(f"응답 상태 코드: {response.status_code}")

            # 응답 처리
            if response.status_code == 200:
                data = response.json()

                # 토큰 정보 저장
                self.access_token = data.get("token")
                self.token_type = data.get("token_type")
                self.expires_dt = data.get("expires_dt")

                self.logger.info("토큰 발급 성공")
                self.logger.info(f"토큰 만료 일시: {self.expires_dt}")

                return True, data
            else:
                error_data = {
                    "status_code": response.status_code,
                    "message": response.text,
                    "url": url
                }
                self.logger.error(f"토큰 발급 실패: {error_data}")
                return False, error_data

        except requests.exceptions.Timeout:
            error_msg = "요청 시간 초과 (Timeout)"
            self.logger.error(error_msg)
            return False, {"error": error_msg}

        except requests.exceptions.ConnectionError:
            error_msg = "네트워크 연결 오류"
            self.logger.error(error_msg)
            return False, {"error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"요청 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            return False, {"error": error_msg}

        except Exception as e:
            error_msg = f"예상치 못한 오류: {str(e)}"
            self.logger.exception(error_msg)
            return False, {"error": error_msg}

    def is_token_valid(self) -> bool:
        """
        현재 토큰이 유효한지 확인

        Returns:
            bool: 토큰 유효 여부
        """
        if not self.access_token or not self.expires_dt:
            return False

        try:
            # 만료 일시 파싱 (YYYYMMDDHHmmss 형식)
            expire_time = datetime.strptime(self.expires_dt, "%Y%m%d%H%M%S")
            current_time = datetime.now()

            return current_time < expire_time
        except Exception as e:
            self.logger.error(f"토큰 유효성 검사 중 오류: {e}")
            return False

    def get_authorization_header(self) -> Dict[str, str]:
        """
        API 호출 시 사용할 Authorization 헤더 반환

        Returns:
            Dict[str, str]: Authorization 헤더
        """
        if not self.access_token:
            raise ValueError("토큰이 발급되지 않았습니다.")

        return {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

    def get_token_info(self) -> Dict:
        """
        현재 토큰 정보 반환

        Returns:
            Dict: 토큰 정보
        """
        return {
            "token": self.access_token,
            "token_type": self.token_type,
            "expires_dt": self.expires_dt,
            "is_valid": self.is_token_valid()
        }
