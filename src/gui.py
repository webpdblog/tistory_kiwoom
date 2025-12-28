"""
키움증권 토큰 관리 GUI
웹 스타일의 사이드바 레이아웃 디자인
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


class SidebarButton(tk.Button):
    """사이드바 전용 버튼"""

    def __init__(self, master, **kwargs):
        default_config = {
            'relief': tk.FLAT,
            'borderwidth': 0,
            'padx': 20,
            'pady': 15,
            'font': ('맑은 고딕', 10),
            'cursor': 'hand2',
            'anchor': 'w',
            'bg': '#2C3E50',
            'fg': '#ECF0F1',
            'activebackground': '#34495E',
            'activeforeground': '#FFFFFF',
        }
        default_config.update(kwargs)

        super().__init__(master, **default_config)

        # 호버 효과
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

        self.is_active = False

    def _on_enter(self, event):
        if not self.is_active:
            self['background'] = '#34495E'

    def _on_leave(self, event):
        if not self.is_active:
            self['background'] = '#2C3E50'

    def set_active(self, active: bool):
        """활성 상태 설정"""
        self.is_active = active
        if active:
            self['background'] = '#4A90E2'
            self['fg'] = '#FFFFFF'
            self['font'] = ('맑은 고딕', 10, 'bold')
        else:
            self['background'] = '#2C3E50'
            self['fg'] = '#ECF0F1'
            self['font'] = ('맑은 고딕', 10)


class KiwoomTokenGUI:
    """키움증권 토큰 관리 GUI"""

    # 색상 팔레트
    COLOR_PRIMARY = '#4A90E2'
    COLOR_SUCCESS = '#5CB85C'
    COLOR_DANGER = '#D9534F'
    COLOR_WARNING = '#F0AD4E'
    COLOR_DARK = '#2C3E50'
    COLOR_SIDEBAR = '#2C3E50'
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

        # 현재 페이지 추적
        self.current_page = "token_issue"

        # 로그 메시지 저장소 (페이지 전환 시에도 유지)
        self.log_messages = []

        # 메인 윈도우 생성
        self.root = tk.Tk()
        self.root.title("키움증권 토큰 관리 시스템")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.COLOR_BG)
        self.root.resizable(True, True)  # 크기 조절 가능
        self.root.minsize(900, 600)  # 최소 크기 설정

        # 아이콘 설정 시도 (없으면 무시)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # 메인 컨테이너
        self.main_container = tk.Frame(self.root, bg=self.COLOR_BG)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 사이드바 생성
        self._create_sidebar()

        # 메인 컨텐츠 영역
        self.content_frame = tk.Frame(self.main_container, bg=self.COLOR_BG)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 초기 로그 메시지
        self.log_message("시스템이 시작되었습니다.", 'INFO')
        self.log_message(f"환경: {self.client.environment}", 'INFO')

        # 초기 페이지 표시
        self._show_token_issue_page()

    def _create_sidebar(self):
        """사이드바 생성"""
        sidebar = tk.Frame(
            self.main_container,
            bg=self.COLOR_SIDEBAR,
            width=250
        )
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # 로고/타이틀 영역
        logo_frame = tk.Frame(sidebar, bg=self.COLOR_SIDEBAR, height=100)
        logo_frame.pack(fill=tk.X, pady=(20, 30))
        logo_frame.pack_propagate(False)

        tk.Label(
            logo_frame,
            text="키움증권",
            font=('맑은 고딕', 18, 'bold'),
            bg=self.COLOR_SIDEBAR,
            fg=self.COLOR_WHITE
        ).pack(pady=(10, 0))

        tk.Label(
            logo_frame,
            text="REST API Manager",
            font=('맑은 고딕', 10),
            bg=self.COLOR_SIDEBAR,
            fg=self.COLOR_LIGHT
        ).pack()

        # 구분선
        tk.Frame(sidebar, bg='#34495E', height=1).pack(fill=tk.X, padx=10, pady=(0, 20))

        # 토큰 폐기 버튼 (맨 위)
        self.revoke_button = SidebarButton(
            sidebar,
            text="🗑  토큰 폐기",
            bg=self.COLOR_DANGER,
            activebackground='#C0392B',
            command=self._revoke_token
        )
        self.revoke_button.pack(fill=tk.X, padx=15, pady=(0, 10))

        # 구분선
        tk.Frame(sidebar, bg='#34495E', height=1).pack(fill=tk.X, padx=10, pady=20)

        # 네비게이션 메뉴
        tk.Label(
            sidebar,
            text="메뉴",
            font=('맑은 고딕', 9),
            bg=self.COLOR_SIDEBAR,
            fg='#95A5A6',
            anchor='w'
        ).pack(fill=tk.X, padx=25, pady=(0, 10))

        # 메뉴 버튼들
        self.nav_buttons = {}

        # 토큰 발급
        self.nav_buttons['token_issue'] = SidebarButton(
            sidebar,
            text="🔑  토큰 발급",
            command=lambda: self._switch_page('token_issue')
        )
        self.nav_buttons['token_issue'].pack(fill=tk.X, padx=15, pady=2)

        # 토큰 정보
        self.nav_buttons['token_info'] = SidebarButton(
            sidebar,
            text="📋  토큰 정보",
            command=lambda: self._switch_page('token_info')
        )
        self.nav_buttons['token_info'].pack(fill=tk.X, padx=15, pady=2)

        # 설정
        self.nav_buttons['settings'] = SidebarButton(
            sidebar,
            text="⚙  설정",
            command=lambda: self._switch_page('settings')
        )
        self.nav_buttons['settings'].pack(fill=tk.X, padx=15, pady=2)

        # 로그
        self.nav_buttons['logs'] = SidebarButton(
            sidebar,
            text="📝  실행 로그",
            command=lambda: self._switch_page('logs')
        )
        self.nav_buttons['logs'].pack(fill=tk.X, padx=15, pady=2)

        # 하단 정보
        footer_frame = tk.Frame(sidebar, bg=self.COLOR_SIDEBAR)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        # 현재 시간
        self.sidebar_time_label = tk.Label(
            footer_frame,
            text="",
            font=('맑은 고딕', 9),
            bg=self.COLOR_SIDEBAR,
            fg='#95A5A6'
        )
        self.sidebar_time_label.pack(pady=5)
        self._update_sidebar_time()

        # 버전 정보
        tk.Label(
            footer_frame,
            text="v1.0.0",
            font=('맑은 고딕', 8),
            bg=self.COLOR_SIDEBAR,
            fg='#7F8C8D'
        ).pack()

    def _update_sidebar_time(self):
        """사이드바 시간 업데이트"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.sidebar_time_label.config(text=current_time)
        self.root.after(1000, self._update_sidebar_time)

    def _switch_page(self, page_name: str):
        """페이지 전환"""
        # 모든 버튼 비활성화
        for btn in self.nav_buttons.values():
            btn.set_active(False)

        # 선택된 버튼 활성화
        if page_name in self.nav_buttons:
            self.nav_buttons[page_name].set_active(True)

        # 현재 페이지 업데이트
        self.current_page = page_name

        # 컨텐츠 프레임 초기화
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 페이지별 표시
        if page_name == 'token_issue':
            self._show_token_issue_page()
        elif page_name == 'token_info':
            self._show_token_info_page()
        elif page_name == 'settings':
            self._show_settings_page()
        elif page_name == 'logs':
            self._show_logs_page()

    def _show_token_issue_page(self):
        """토큰 발급 페이지"""
        # 페이지 헤더
        self._create_page_header("토큰 발급", "OAuth 인증을 통해 API 접근 토큰을 발급받습니다")

        # 컨텐츠 컨테이너
        content = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # 환경 설정 카드
        env_card = self._create_card(content, "환경 설정")
        env_card.pack(fill=tk.X, pady=(0, 20))

        env_inner = tk.Frame(env_card, bg=self.COLOR_WHITE)
        env_inner.pack(padx=30, pady=20, fill=tk.X)

        tk.Label(
            env_inner,
            text="API 환경:",
            font=('맑은 고딕', 11),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK
        ).pack(side=tk.LEFT, padx=(0, 15))

        self.env_var = tk.StringVar(value=self.client.environment)
        env_combo = ttk.Combobox(
            env_inner,
            textvariable=self.env_var,
            values=['mock', 'production'],
            state='readonly',
            width=15,
            font=('맑은 고딕', 10)
        )
        env_combo.pack(side=tk.LEFT)
        env_combo.bind('<<ComboboxSelected>>', self._on_env_changed)

        # 상태 표시
        status_frame = tk.Frame(env_inner, bg=self.COLOR_WHITE)
        status_frame.pack(side=tk.RIGHT)

        tk.Label(
            status_frame,
            text="상태:",
            font=('맑은 고딕', 11),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.status_label = tk.Label(
            status_frame,
            text="미연결",
            font=('맑은 고딕', 11, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DANGER
        )
        self.status_label.pack(side=tk.LEFT)

        # 토큰 발급 카드
        issue_card = self._create_card(content, "토큰 발급")
        issue_card.pack(fill=tk.BOTH, expand=True)

        issue_inner = tk.Frame(issue_card, bg=self.COLOR_WHITE)
        issue_inner.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)

        # 안내 메시지
        info_frame = tk.Frame(issue_inner, bg='#EBF5FB', relief=tk.FLAT, borderwidth=1)
        info_frame.pack(fill=tk.X, pady=(0, 30))

        tk.Label(
            info_frame,
            text="ℹ️  토큰 발급 안내",
            font=('맑은 고딕', 10, 'bold'),
            bg='#EBF5FB',
            fg='#2471A3',
            anchor='w'
        ).pack(fill=tk.X, padx=15, pady=(15, 5))

        tk.Label(
            info_frame,
            text="• 발급된 토큰은 Authorization 헤더에 포함하여 사용합니다\n• 토큰 만료 전 재발급이 필요합니다\n• config.ini 또는 .env 파일에 인증 정보가 설정되어 있어야 합니다",
            font=('맑은 고딕', 9),
            bg='#EBF5FB',
            fg='#2471A3',
            anchor='w',
            justify=tk.LEFT
        ).pack(fill=tk.X, padx=15, pady=(0, 15))

        # 발급 버튼 (중앙)
        button_frame = tk.Frame(issue_inner, bg=self.COLOR_WHITE)
        button_frame.pack(expand=True)

        self.token_button = ModernButton(
            button_frame,
            text="🔑  토큰 발급하기",
            bg=self.COLOR_PRIMARY,
            fg=self.COLOR_WHITE,
            activebackground='#357ABD',
            font=('맑은 고딕', 12, 'bold'),
            padx=40,
            pady=20,
            command=self._request_token
        )
        self.token_button.pack()

        # 마지막 발급 정보
        if self.client.access_token:
            last_issue_frame = tk.Frame(issue_inner, bg=self.COLOR_WHITE)
            last_issue_frame.pack(side=tk.BOTTOM, pady=(20, 0))

            tk.Label(
                last_issue_frame,
                text=f"✓ 마지막 발급: {self._format_datetime(self.client.expires_dt) if self.client.expires_dt else '-'}",
                font=('맑은 고딕', 9),
                bg=self.COLOR_WHITE,
                fg=self.COLOR_SUCCESS
            ).pack()

        # 네비게이션 활성화
        self.nav_buttons['token_issue'].set_active(True)

    def _show_token_info_page(self):
        """토큰 정보 페이지"""
        self._create_page_header("토큰 정보", "발급된 토큰의 상세 정보를 확인합니다")

        content = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # 토큰 상태 카드
        status_card = self._create_card(content, "토큰 상태")
        status_card.pack(fill=tk.X, pady=(0, 20))

        status_inner = tk.Frame(status_card, bg=self.COLOR_WHITE)
        status_inner.pack(padx=30, pady=20, fill=tk.X)

        token_info = self.client.get_token_info()
        is_valid = token_info.get('is_valid', False)

        # 상태 아이콘
        status_icon = "✓" if is_valid else "✗"
        status_text = "유효함" if is_valid else "만료됨 또는 미발급"
        status_color = self.COLOR_SUCCESS if is_valid else self.COLOR_DANGER

        tk.Label(
            status_inner,
            text=f"{status_icon} {status_text}",
            font=('맑은 고딕', 16, 'bold'),
            bg=self.COLOR_WHITE,
            fg=status_color
        ).pack(pady=10)

        # 토큰 세부 정보 카드
        detail_card = self._create_card(content, "세부 정보")
        detail_card.pack(fill=tk.BOTH, expand=True)

        detail_inner = tk.Frame(detail_card, bg=self.COLOR_WHITE)
        detail_inner.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)

        # 정보 행들
        info_items = [
            ("토큰 타입", token_info.get('token_type', '-')),
            ("만료 일시", self._format_datetime(token_info.get('expires_dt', '-'))),
            ("환경", self.client.environment.upper()),
        ]

        for label, value in info_items:
            row = tk.Frame(detail_inner, bg=self.COLOR_WHITE)
            row.pack(fill=tk.X, pady=10)

            tk.Label(
                row,
                text=label + ":",
                font=('맑은 고딕', 10, 'bold'),
                bg=self.COLOR_WHITE,
                fg=self.COLOR_DARK,
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=value,
                font=('맑은 고딕', 10),
                bg=self.COLOR_WHITE,
                fg=self.COLOR_DARK,
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 토큰 값
        tk.Label(
            detail_inner,
            text="액세스 토큰:",
            font=('맑은 고딕', 10, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK,
            anchor='w'
        ).pack(fill=tk.X, pady=(20, 5))

        token_text = scrolledtext.ScrolledText(
            detail_inner,
            height=6,
            font=('Consolas', 9),
            bg=self.COLOR_LIGHT,
            fg=self.COLOR_DARK,
            relief=tk.FLAT,
            borderwidth=1,
            wrap=tk.WORD
        )
        token_text.pack(fill=tk.BOTH, expand=True)
        token_value = token_info.get('token', '')
        token_text.insert('1.0', token_value if token_value else '토큰이 발급되지 않았습니다.')
        token_text.config(state=tk.DISABLED)

    def _show_settings_page(self):
        """설정 페이지"""
        self._create_page_header("설정", "API 및 애플리케이션 설정을 관리합니다")

        content = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # API 설정 카드
        api_card = self._create_card(content, "API 설정")
        api_card.pack(fill=tk.X, pady=(0, 20))

        api_inner = tk.Frame(api_card, bg=self.COLOR_WHITE)
        api_inner.pack(padx=30, pady=20, fill=tk.X)

        settings_items = [
            ("App Key", self.config.get_appkey()[:20] + "..." if len(self.config.get_appkey()) > 20 else self.config.get_appkey()),
            ("운영 도메인", "https://api.kiwoom.com"),
            ("모의투자 도메인", "https://mockapi.kiwoom.com"),
        ]

        for label, value in settings_items:
            row = tk.Frame(api_inner, bg=self.COLOR_WHITE)
            row.pack(fill=tk.X, pady=8)

            tk.Label(
                row,
                text=label + ":",
                font=('맑은 고딕', 10, 'bold'),
                bg=self.COLOR_WHITE,
                fg=self.COLOR_DARK,
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=value,
                font=('맑은 고딕', 10),
                bg=self.COLOR_WHITE,
                fg='#7F8C8D',
                anchor='w'
            ).pack(side=tk.LEFT)

        # 로깅 설정 카드
        log_card = self._create_card(content, "로깅 설정")
        log_card.pack(fill=tk.X)

        log_inner = tk.Frame(log_card, bg=self.COLOR_WHITE)
        log_inner.pack(padx=30, pady=20, fill=tk.X)

        log_items = [
            ("로그 레벨", self.config.get_log_level()),
            ("로그 파일", self.config.get_log_file()),
            ("최대 크기", f"{self.config.get_max_log_size() // 1024 // 1024} MB"),
        ]

        for label, value in log_items:
            row = tk.Frame(log_inner, bg=self.COLOR_WHITE)
            row.pack(fill=tk.X, pady=8)

            tk.Label(
                row,
                text=label + ":",
                font=('맑은 고딕', 10, 'bold'),
                bg=self.COLOR_WHITE,
                fg=self.COLOR_DARK,
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=value,
                font=('맑은 고딕', 10),
                bg=self.COLOR_WHITE,
                fg='#7F8C8D',
                anchor='w'
            ).pack(side=tk.LEFT)

    def _show_logs_page(self):
        """실행 로그 페이지"""
        self._create_page_header("실행 로그", "API 호출 내역 및 시스템 로그를 확인합니다")

        content = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # 로그 카드
        log_card = self._create_card(content, "로그")
        log_card.pack(fill=tk.BOTH, expand=True)

        log_inner = tk.Frame(log_card, bg=self.COLOR_WHITE)
        log_inner.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_inner,
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

        # 저장된 로그 메시지 복원
        self.log_text.config(state=tk.NORMAL)
        for msg, level in self.log_messages:
            self.log_text.insert(tk.END, msg, level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _create_page_header(self, title: str, description: str):
        """페이지 헤더 생성"""
        header_frame = tk.Frame(self.content_frame, bg=self.COLOR_WHITE, height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        inner = tk.Frame(header_frame, bg=self.COLOR_WHITE)
        inner.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        tk.Label(
            inner,
            text=title,
            font=('맑은 고딕', 22, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK,
            anchor='w'
        ).pack(fill=tk.X)

        tk.Label(
            inner,
            text=description,
            font=('맑은 고딕', 10),
            bg=self.COLOR_WHITE,
            fg='#7F8C8D',
            anchor='w'
        ).pack(fill=tk.X, pady=(5, 0))

    def _create_card(self, parent, title: str):
        """카드 컴포넌트 생성"""
        card = tk.LabelFrame(
            parent,
            text=f"  {title}  ",
            font=('맑은 고딕', 11, 'bold'),
            bg=self.COLOR_WHITE,
            fg=self.COLOR_DARK,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=0
        )
        return card

    def _format_datetime(self, dt_str: str) -> str:
        """날짜 시간 포맷팅"""
        if not dt_str or dt_str == '-':
            return '-'
        try:
            dt = datetime.strptime(dt_str, '%Y%m%d%H%M%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return dt_str

    def _on_env_changed(self, event):
        """환경 변경 이벤트"""
        new_env = self.env_var.get()
        self.client.environment = new_env
        self.client.base_url = (
            self.client.PRODUCTION_DOMAIN if new_env == 'production'
            else self.client.MOCK_DOMAIN
        )
        if hasattr(self, 'log_text'):
            self.log_message(f"환경이 '{new_env}'로 변경되었습니다.", 'INFO')

    def _revoke_token(self):
        """토큰 폐기"""
        if not self.client.access_token:
            messagebox.showinfo("토큰 폐기", "폐기할 토큰이 없습니다.")
            return

        result = messagebox.askyesno(
            "토큰 폐기 확인",
            "현재 토큰을 폐기하시겠습니까?\n\n토큰 폐기 후 API를 사용하려면 새로 발급받아야 합니다."
        )

        if result:
            # 토큰 정보 초기화
            self.client.access_token = None
            self.client.token_type = None
            self.client.expires_dt = None

            self.logger.info("토큰이 폐기되었습니다.")
            if hasattr(self, 'log_text'):
                self.log_message("토큰이 폐기되었습니다.", 'WARNING')

            # 상태 업데이트
            if hasattr(self, 'status_label'):
                self.status_label.config(text="미연결", fg=self.COLOR_DANGER)

            messagebox.showinfo("토큰 폐기 완료", "토큰이 성공적으로 폐기되었습니다.")

            # 토큰 발급 페이지로 이동
            self._switch_page('token_issue')

    def _request_token(self):
        """토큰 발급 요청 (스레드에서 실행)"""
        self.token_button.config(state=tk.DISABLED, text="🔄  발급 중...")
        if hasattr(self, 'log_text'):
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
        self.token_button.config(state=tk.NORMAL, text="🔑  토큰 발급하기")

        if success:
            if hasattr(self, 'log_text'):
                self.log_message("✓ 토큰 발급 성공!", 'SUCCESS')
            if hasattr(self, 'status_label'):
                self.status_label.config(text="연결됨", fg=self.COLOR_SUCCESS)

            messagebox.showinfo("토큰 발급 성공", "토큰이 성공적으로 발급되었습니다!")

            # 페이지 새로고침
            self._switch_page(self.current_page)
        else:
            error_msg = data.get('error', data.get('message', '알 수 없는 오류'))
            if hasattr(self, 'log_text'):
                self.log_message(f"✗ 토큰 발급 실패: {error_msg}", 'ERROR')
            if hasattr(self, 'status_label'):
                self.status_label.config(text="연결 실패", fg=self.COLOR_DANGER)

            messagebox.showerror("토큰 발급 실패", f"토큰 발급에 실패했습니다.\n\n{error_msg}")

    def log_message(self, message: str, level: str = 'INFO'):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        # 로그 메시지 저장소에 저장
        self.log_messages.append((log_entry, level))

        # log_text 위젯이 현재 존재하고 유효한 경우에만 업데이트
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            try:
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, log_entry, level)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
            except tk.TclError:
                # 위젯이 삭제된 경우 무시
                pass

    def run(self):
        """GUI 실행"""
        self.root.mainloop()
