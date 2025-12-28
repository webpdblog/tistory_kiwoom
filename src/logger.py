"""
로깅 시스템
파일 및 콘솔 로그를 관리합니다.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    """로깅 시스템 관리 클래스"""

    def __init__(
        self,
        log_file: str = "logs/kiwoom_api.log",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        Args:
            log_file: 로그 파일 경로
            log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: 로그 파일 최대 크기 (바이트)
            backup_count: 백업 파일 개수
        """
        self.log_file = log_file
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        self._setup_logger()

    def _setup_logger(self):
        """로거 설정"""
        # 로그 디렉토리 생성
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # 루트 로거 가져오기
        logger = logging.getLogger()
        logger.setLevel(self.log_level)

        # 기존 핸들러 제거
        logger.handlers.clear()

        # 파일 핸들러 (Rotating)
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)

        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 핸들러 추가
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.info("=" * 80)
        logger.info("로깅 시스템 초기화 완료")
        logger.info(f"로그 파일: {self.log_file}")
        logger.info(f"로그 레벨: {logging.getLevelName(self.log_level)}")
        logger.info("=" * 80)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        이름으로 로거 가져오기

        Args:
            name: 로거 이름

        Returns:
            logging.Logger: 로거 인스턴스
        """
        return logging.getLogger(name)
