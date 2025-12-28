"""
키움증권 토큰 관리 시스템 - 메인 진입점
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config_manager import ConfigManager
from src.logger import Logger
from src.kiwoom_client import KiwoomAPIClient
from src.gui import KiwoomTokenGUI


def main():
    """메인 함수"""
    print("=" * 60)
    print("키움증권 REST API 토큰 관리 시스템 v1.0")
    print("=" * 60)

    # 설정 관리자 초기화
    config = ConfigManager()

    # 로거 초기화
    logger_manager = Logger(
        log_file=config.get_log_file(),
        log_level=config.get_log_level(),
        max_bytes=config.get_max_log_size(),
        backup_count=config.get_backup_count()
    )

    # API 클라이언트 초기화
    client = KiwoomAPIClient(
        appkey=config.get_appkey(),
        secretkey=config.get_secretkey(),
        environment=config.get_environment()
    )

    # GUI 실행
    print("\nGUI를 시작합니다...")
    app = KiwoomTokenGUI(client, config)
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
