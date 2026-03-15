import time
import threading
import flet as ft

ASSET_DIR = "modules/clap-rhythm"

class ClapRhythmPage(ft.View):
    SAMPLE_RATE = 44_100
    CLAP_THRESHOLD = 0.05

    def __init__(self, page: ft.Page):
        super().__init__(route="/clap_rhythm")
        self.app = getattr(page, "app", None)
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.padding = 0
        self.bgcolor = "#FEB42F"
        self.levels = [
            ("clap", 2, "clap", 0.5, "clap"),
            ("clap", 1, "clap", 0.5, "clap", 0.5, "clap"),
            ("clap", 0.5, "clap", 0.5, "clap", 1, "clap", 0.5, "clap"),
        ]
        self.level_index = 0
        self.SPACING = 8
        self.LEVEL_AR = 2
        self.ENTRANCE_MS = 220
        self.ENTRANCE_STAGGER_MS = 40

        # Clap boyutları
        self.CLAP_W = 64
        self.CLAP_H = 24

        self.app.play_sound(f"{ASSET_DIR}/info-audio.mp3")

        info_container = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.VOLUME_UP_ROUNDED,
                        icon_size=48,
                        icon_color="#0E444D",
                        on_click=lambda e: self.app.play_sound(f"{ASSET_DIR}/info-audio.mp3"),
                    ),
                    ft.Text(
                        "Parlayan sarı blok gördüğünde alkışla!",
                        max_lines=2,
                        expand=True,
                        size=18,
                        color="#0E444D",
                    ),
                ]
            ),
            margin=ft.Margin(0, 30, 0, 0),
            scale=0.9,
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
            border_radius=20,
        )

        self.grid_holder = ft.Container(
            padding=12,
            margin=ft.Margin(0, 10, 0, 0),
            expand=True,
            animate_opacity=300,
            animate_scale=ft.Animation(250),
            opacity=1,
            scale=1,
        )

        # Alt bar düğmeleri
        self.next_btn = ft.FilledButton(
            text="İleri",
            opacity=0,
            disabled=True,
            style=self.app.button_style if self.app else None,
            height=50,
            width=self.page.width // 1.5 if self.page.width else 320,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            scale=1,
            # on_click=self._handle_next,
        )
        self.replay_btn = ft.IconButton(
            icon=ft.Icons.REPLAY_ROUNDED,
            icon_size=20,
            tooltip="Tekrar başlat",
            opacity=0,
            disabled=True,
            style=self.app.button_style if self.app else None,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            height=50,
            width=50,
            # on_click=self._handle_replay,
        )
        self.play_btn = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            icon_size=24,
            tooltip="Çal",
            style=self.app.button_style if self.app else None,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            height=64,
            width=64,
            # on_click=self._play_reference_rhythm,
        )
        self.mic_btn = ft.IconButton(
            icon=ft.Icons.MIC_ROUNDED,
            icon_size=24,
            tooltip="Ses kaydet",
            style=self.app.button_style if self.app else None,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            height=64,
            width=64,
            # on_click=self._listen_and_check,
        )

        self.action_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[self.next_btn, self.replay_btn],
            opacity=0,
            scale=0.95,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            visible=False,
        )
        self.play_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            spacing=8,
            controls=[self.play_btn, self.mic_btn],
            opacity=1,
            scale=1,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            visible=True,
        )

        self.bottom_bar = ft.Container(
            height=100,
            bgcolor="#FDEDD4",
            content=ft.Stack(
                alignment=ft.alignment.center,
                controls=[self.play_row, self.action_row],
            ),
            border=ft.Border(
                ft.BorderSide(width=1, color=ft.Colors.with_opacity(0.7, "#B5B0AB")),
                None,
                None,
                None,
            ),
        )

        self.level_labels = ["Kolay", "Orta", "Zor"]
        self.level_active_colors = ["#5CBAA2", "#FFB43D", "#F87F64"]
        self.level_inactive_colors = ["#5CBAA2", "#FFB43D", "#F87F64"]
        self.level_ctrs = []
        self.level_inners = []

        for i, label in enumerate(self.level_labels):
            inner = ft.Container(
                bgcolor=self.level_inactive_colors[i],
                border_radius=10,
                alignment=ft.alignment.center,
                animate_scale=ft.Animation(150),
                content=ft.Text(label, size=18, color="#0E444D", weight=ft.FontWeight.W_600),
                # on_click=lambda e, idx=i: self._on_level_click(idx),
                border=ft.border.all(3, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            )
            outer = ft.Container(
                content=inner,
                aspect_ratio=self.LEVEL_AR,
                border_radius=10,
                expand=True,
            )
            self.level_ctrs.append(outer)
            self.level_inners.append(inner)

        self.level_buttons_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10,
            controls=self.level_ctrs,
        )
        self.level_buttons_wrap = ft.Container(
            content=self.level_buttons_row,
            margin=24,
        )

        background = ft.Container(
            expand=True,
            image=ft.DecorationImage(
                src=f"{ASSET_DIR}/bg.png",
                fit=ft.ImageFit.FIT_WIDTH,
                repeat=ft.ImageRepeat.REPEAT_Y,
            ),
        )
        foreground = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                info_container,
                self.grid_holder,
                self.level_buttons_wrap,
                self.bottom_bar,
            ],
        )

        self.controls = [
            ft.Stack(
                expand=True,
                controls=[background, ft.SafeArea(content=foreground)],
            )
        ]

        # self._apply_level(self.level_index)