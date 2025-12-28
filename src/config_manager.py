"""
설정 관리자
config.ini 및 .env 파일을 관리합니다.
"""

import os
import configparser
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class ConfigManager:
    """설정 관리 클래스"""

    def __init__(self, config_file: str = "config.ini", env_file: str = ".env"):
        """
        Args:
            config_file: 설정 파일 경로
            env_file: 환경 변수 파일 경로
        """
        self.config_file = config_file
        self.env_file = env_file

        # .env 파일 로드 (있는 경우)
        if Path(env_file).exists():
            load_dotenv(env_file)

        # config.ini 파일 로드
        self.config = configparser.ConfigParser()
        if Path(config_file).exists():
            self.config.read(config_file, encoding='utf-8')
        else:
            # 기본 설정 생성
            self._create_default_config()

    def _create_default_config(self):
        """기본 설정 파일 생성"""
        self.config['KIWOOM'] = {
            'environment': 'mock',
            'production_domain': 'https://api.kiwoom.com',
            'mock_domain': 'https://mockapi.kiwoom.com',
            'appkey': 'YOUR_APP_KEY',
            'secretkey': 'YOUR_SECRET_KEY'
        }

        self.config['LOGGING'] = {
            'log_level': 'INFO',
            'log_file': 'logs/kiwoom_api.log',
            'max_log_size': '10',
            'backup_count': '5'
        }

        self.save_config()

    def save_config(self):
        """설정 파일 저장"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get(self, section: str, key: str, fallback: Optional[str] = None) -> str:
        """
        설정 값 가져오기
        우선순위: 환경변수 > config.ini

        Args:
            section: 섹션 이름
            key: 키 이름
            fallback: 기본값

        Returns:
            str: 설정 값
        """
        # 환경변수 먼저 확인
        env_key = f"{section.upper()}_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value:
            return env_value

        # config.ini에서 확인
        return self.config.get(section, key, fallback=fallback)

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """정수형 설정 값 가져오기"""
        value = self.get(section, key, str(fallback))
        try:
            return int(value)
        except ValueError:
            return fallback

    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """불리언 설정 값 가져오기"""
        value = self.get(section, key, str(fallback))
        return value.lower() in ('true', 'yes', '1', 'on')

    def set(self, section: str, key: str, value: str):
        """설정 값 저장"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    # Kiwoom 관련 설정
    def get_environment(self) -> str:
        """환경 가져오기"""
        return self.get('KIWOOM', 'environment', 'mock')

    def get_appkey(self) -> str:
        """App Key 가져오기"""
        return self.get('KIWOOM', 'appkey', '')

    def get_secretkey(self) -> str:
        """Secret Key 가져오기"""
        return self.get('KIWOOM', 'secretkey', '')

    # Logging 관련 설정
    def get_log_level(self) -> str:
        """로그 레벨 가져오기"""
        return self.get('LOGGING', 'log_level', 'INFO')

    def get_log_file(self) -> str:
        """로그 파일 경로 가져오기"""
        return self.get('LOGGING', 'log_file', 'logs/kiwoom_api.log')

    def get_max_log_size(self) -> int:
        """로그 파일 최대 크기 가져오기 (바이트)"""
        size_mb = self.get_int('LOGGING', 'max_log_size', 10)
        return size_mb * 1024 * 1024

    def get_backup_count(self) -> int:
        """로그 백업 개수 가져오기"""
        return self.get_int('LOGGING', 'backup_count', 5)
