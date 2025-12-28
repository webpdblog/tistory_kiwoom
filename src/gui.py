"""
키움증권 토큰 관리 GUI
tkinter를 사용한 모던한 디자인의 GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
from typing import Optional
import logging


class ModernButton(tk.Button):
    """모던한 스타일의 버튼"""

    def __init__(self, master, **kwargs):
        # 기본 스타일 설정
        default_config = {
            'relief': tk.FLAT,
            'borderwidth': 0,
            'padx': 20,
            'pady': 10,
            'font': ('맑은 고딕', 10, 'bold'),
            'cursor': 'hand2',
        }
        default_config.update(kwargs)

        super().__init__(master, **default_config)

        # 호버 효과
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

        self.default_bg = default_config.get('bg', '#4A90E2')
        self.hover_bg = default_config.get('activebackground', '#357ABD')

    def _on_enter(self, event):
        self['background'] = self.hover_bg

    def _on_leave(self, event):
        self['background'] = self.default_bg


class KiwoomTokenGUI:
    """키움증권 토큰 관리 GUI"""

    # 색상 팔레트
    COLOR_PRIMARY = '#4A90E2'
    COLOR_SUCCESS = '#5CB85C'
    COLOR_DANGER = '#D9534F'
    COLOR_WARNING = '#F0AD4E'
    COLOR_DARK = '#2C3E50'
    COLOR_LIGHT = '#ECF0F1'
    COLOR_BG = '#F5F6FA'
    COLOR_WHITE = '#FFFFFF'

    def __init__(self, kiwoom_client, config_manager):
        """
        Args:
            kiwoom_client: KiwoomAPIClient 인스턴스
            config_manager: ConfigManager 인스턴스
        """
        self.client = kiwoom_client
        self.config = config_manager
        self.logger = logging.getLogger(__name__)

        # 메인 윈도우 생성
        self.root = tk.Tk()
        self.root.title("키움증권 토큰 관리 시스템")
        self.root.geometry("900x700")
        self.root.configure(bg=self.COLOR_BG)
        self.root.resizable(False, False)

        # 아이콘 설정 시도 (없으면 무시)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # GUI 구성
        self._create_header()
        self._create_connection_frame()
        self._create_token_info_frame()
        self._create_log_frame()
        self._create_footer()

        # 초기 상태 업데이트
        self._update_token_display()

    def _create_header(self):
        """헤더 생성"""
        header_frame = tk.Frame(self.root, bg=self.COLOR_DARK, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # 타이틀
        title_label = tk.Label(
            header_frame,
            text="키움증권 REST API 토큰 관리",
            font=('맑은 고딕', 20, 'bold'),
            bg=self.COLOR_DARK,
            fg=self.COLOR_WHITE
        )
        title_label.pack(pady=20)

        # 현재 시간 표시
        self.time_label = tk.Label(
            header_frame,
            text="",
            font=('맑은 고딕', 9),
            bg=self.COLOR_DARK,
            fg=self.COLOR_LIGHT
        )
        self.time_label.pack(pady=(0, 10))
        self._update_time()

    def _create_connection_frame(self):
        """연결 정보 프레임 생성"""
        frame = tk.LabelFrame(
            self.root,
            text="  연결 설정  ",
            font=('맑은 고딕', 11, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK,
            relief=tk.FLAT,
            borderwidth=2
        )
        frame.pack(padx=20, pady=(20, 10), fill=tk.X)

        inner_frame = tk.Frame(frame, bg=self.COLOR_WHITE)
        inner_frame.pack(padx=20, pady=15)

        # 환경 선택
        env_frame = tk.Frame(inner_frame, bg=self.COLOR_WHITE)
        env_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            env_frame,
            text="환경:",
            font=('맑은 고딕', 10),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.env_var = tk.StringVar(value=self.client.environment)
        env_combo = ttk.Combobox(
            env_frame,
            textvariable=self.env_var,
            values=['mock', 'production'],
            state='readonly',
            width=12,
            font=('맑은 고딕', 10)
        )
        env_combo.pack(side=tk.LEFT)
        env_combo.bind('<<ComboboxSelected>>', self._on_env_changed)

        # 상태 표시
        status_frame = tk.Frame(inner_frame, bg=self.COLOR_WHITE)
        status_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            status_frame,
            text="상태:",
            font=('맑은 고딕', 10),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.status_label = tk.Label(
            status_frame,
            text="미연결",
            font=('맑은 고딕', 10, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DANGER,
            width=12
        )
        self.status_label.pack(side=tk.LEFT)

        # 토큰 발급 버튼
        self.token_button = ModernButton(
            inner_frame,
            text="토큰 발급",
            bg=self.COLOR_PRIMARY,
            fg=self.COLOR_WHITE,
            activebackground='#357ABD',
            command=self._request_token
        )
        self.token_button.pack(side=tk.LEFT)

    def _create_token_info_frame(self):
        """토큰 정보 프레임 생성"""
        frame = tk.LabelFrame(
            self.root,
            text="  토큰 정보  ",
            font=('맑은 고딕', 11, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK,
            relief=tk.FLAT,
            borderwidth=2
        )
        frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(frame, bg=self.COLOR_WHITE)
        inner_frame.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)

        # 정보 레이블들
        info_fields = [
            ("토큰 타입:", "token_type"),
            ("만료 일시:", "expires_dt"),
            ("유효 상태:", "valid_status"),
        ]

        for i, (label_text, attr_name) in enumerate(info_fields):
            row_frame = tk.Frame(inner_frame, bg=self.COLOR_WHITE)
            row_frame.pack(fill=tk.X, pady=5)

            tk.Label(
                row_frame,
                text=label_text,
                font=('맑은 고딕', 10, 'bold'),
                bg=self.COLOR_WHITE,
                fg=self.COLOR_DARK,
                width=12,
                anchor='w'
            ).pack(side=tk.LEFT, padx=(0, 10))

            label = tk.Label(
                row_frame,
                text="-",
                font=('맑은 고딕', 10),
                bg=self.COLOR_WHITE,
                fg=self.COLOR_DARK,
                anchor='w'
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            setattr(self, f"{attr_name}_label", label)

        # 토큰 값 표시
        tk.Label(
            inner_frame,
            text="액세스 토큰:",
            font=('맑은 고딕', 10, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK,
            anchor='w'
        ).pack(fill=tk.X, pady=(15, 5))

        self.token_text = scrolledtext.ScrolledText(
            inner_frame,
            height=4,
            font=('Consolas', 9),
            bg=self.COLOR_LIGHT,
            fg=self.COLOR_DARK,
            relief=tk.FLAT,
            borderwidth=1,
            wrap=tk.WORD
        )
        self.token_text.pack(fill=tk.BOTH, expand=True)
        self.token_text.config(state=tk.DISABLED)

    def _create_log_frame(self):
        """로그 프레임 생성"""
        frame = tk.LabelFrame(
            self.root,
            text="  실행 로그  ",
            font=('맑은 고딕', 11, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK,
            relief=tk.FLAT,
            borderwidth=2
        )
        frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(frame, bg=self.COLOR_WHITE)
        inner_frame.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            inner_frame,
            height=8,
            font=('Consolas', 9),
            bg='#1E1E1E',
            fg='#D4D4D4',
            relief=tk.FLAT,
            borderwidth=0,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        # 로그 색상 태그
        self.log_text.tag_config('INFO', foreground='#4EC9B0')
        self.log_text.tag_config('ERROR', foreground='#F48771')
        self.log_text.tag_config('SUCCESS', foreground='#B5CEA8')
        self.log_text.tag_config('WARNING', foreground='#DCDCAA')

    def _create_footer(self):
        """푸터 생성"""
        footer_frame = tk.Frame(self.root, bg=self.COLOR_LIGHT, height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        # 정보 텍스트
        tk.Label(
            footer_frame,
            text="키움증권 REST API v1.0 | © 2025",
            font=('맑은 고딕', 9),
            bg=self.COLOR_LIGHT,
            fg=self.COLOR_DARK
        ).pack(pady=15)

    def _update_time(self):
        """현재 시간 업데이트"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"현재 시간: {current_time}")
        self.root.after(1000, self._update_time)

    def _on_env_changed(self, event):
        """환경 변경 이벤트"""
        new_env = self.env_var.get()
        self.client.environment = new_env
        self.client.base_url = (
            self.client.PRODUCTION_DOMAIN if new_env == 'production'
            else self.client.MOCK_DOMAIN
        )
        self.log_message(f"환경이 '{new_env}'로 변경되었습니다.", 'INFO')

    def _request_token(self):
        """토큰 발급 요청 (스레드에서 실행)"""
        self.token_button.config(state=tk.DISABLED, text="발급 중...")
        self.log_message("토큰 발급을 요청합니다...", 'INFO')

        # 별도 스레드에서 실행
        thread = threading.Thread(target=self._request_token_thread, daemon=True)
        thread.start()

    def _request_token_thread(self):
        """토큰 발급 스레드"""
        try:
            success, data = self.client.get_access_token()

            # GUI 업데이트는 메인 스레드에서
            self.root.after(0, lambda: self._handle_token_response(success, data))

        except Exception as e:
            self.logger.exception("토큰 발급 중 예외 발생")
            self.root.after(0, lambda: self._handle_token_response(False, {"error": str(e)}))

    def _handle_token_response(self, success: bool, data: dict):
        """토큰 발급 응답 처리"""
        self.token_button.config(state=tk.NORMAL, text="토큰 발급")

        if success:
            self.log_message("✓ 토큰 발급 성공!", 'SUCCESS')
            self.status_label.config(text="연결됨", fg=self.COLOR_SUCCESS)
            self._update_token_display()
        else:
            error_msg = data.get('error', data.get('message', '알 수 없는 오류'))
            self.log_message(f"✗ 토큰 발급 실패: {error_msg}", 'ERROR')
            self.status_label.config(text="연결 실패", fg=self.COLOR_DANGER)
            messagebox.showerror("토큰 발급 실패", f"토큰 발급에 실패했습니다.\n\n{error_msg}")

    def _update_token_display(self):
        """토큰 정보 표시 업데이트"""
        token_info = self.client.get_token_info()

        # 토큰 타입
        self.token_type_label.config(
            text=token_info.get('token_type', '-')
        )

        # 만료 일시
        expires_dt = token_info.get('expires_dt', '-')
        if expires_dt and expires_dt != '-':
            try:
                dt = datetime.strptime(expires_dt, '%Y%m%d%H%M%S')
                expires_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        self.expires_dt_label.config(text=expires_dt)

        # 유효 상태
        is_valid = token_info.get('is_valid', False)
        valid_text = "유효함" if is_valid else "만료됨"
        valid_color = self.COLOR_SUCCESS if is_valid else self.COLOR_DANGER
        self.valid_status_label.config(text=valid_text, fg=valid_color)

        # 토큰 값
        token_value = token_info.get('token', '')
        self.token_text.config(state=tk.NORMAL)
        self.token_text.delete('1.0', tk.END)
        if token_value:
            self.token_text.insert('1.0', token_value)
        else:
            self.token_text.insert('1.0', '토큰이 발급되지 않았습니다.')
        self.token_text.config(state=tk.DISABLED)

    def log_message(self, message: str, level: str = 'INFO'):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run(self):
        """GUI 실행"""
        self.root.mainloop()
