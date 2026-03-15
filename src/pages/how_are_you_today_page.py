import flet as ft
import time

# --- Constants ---
STUDENT = 0
OBSERVER = 1

ASSET_DIR = "how-are-you-today"

class HowAreYouTodayPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/login")
        self.page = page
        self.app = page.app
        self.padding = 0
        self.bgcolor = "#FAF5EF"

        self.selected_emotion = None
        self.start_time = time.time()  # sayfa açılış zamanı

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
                        "Bugün nasılsın?",
                        max_lines=2,
                        expand=True,
                        size=20,
                        color="#0E444D",
                    ),
                ]
            ),
            scale=0.85,
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
            border_radius=20,
        )

        continue_button_style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=54),
            padding=ft.Padding(64, 12, 64, 12),
            text_style=ft.TextStyle(size=28, font_family="MPlus"),
            bgcolor="#EFDAB3",
            color="#5A3C2F",
        )

        def make_emotion_container(key: str, filename: str) -> ft.Container:
            c = ft.Container(
                content=ft.Image(src=f"{ASSET_DIR}/{filename}", fit=ft.ImageFit.CONTAIN),
                height=86,
                width=86,
                padding=8,
                border_radius=16,
                bgcolor=ft.Colors.with_opacity(0.0, ft.Colors.WHITE),
                border=ft.border.all(2, ft.Colors.with_opacity(0.0, ft.Colors.WHITE)),
                animate_scale=ft.Animation(150, "easeOut"),
                animate_opacity=300,
                on_click=lambda e, k=key: self.set_selected_emotion(k),
            )
            return c

        self.sad_box = make_emotion_container("sad", "sad.png")
        self.neutral_box = make_emotion_container("neutral", "neutral.png")
        self.happy_box = make_emotion_container("happy", "happy.png")

        self.continue_btn = ft.ElevatedButton(
            "Devam",
            style=continue_button_style,
            on_click=lambda e: self.page.run_thread(self.set_data),
            disabled=True,
        )

        self.main_content = ft.Container(
            content=ft.Column(
                [
                    info_container,
                    ft.Row(
                        [
                            self.sad_box,
                            self.neutral_box,
                            self.happy_box,
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        content=ft.Image(f"{ASSET_DIR}/bg.png", fit=ft.ImageFit.FIT_WIDTH),
                        alignment=ft.alignment.center,
                        padding=0,
                    ),
                    ft.Row(
                        [self.continue_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=0,
        )

        self.controls = [
            ft.SafeArea(
                ft.Stack(
                    [
                        ft.Stack(
                            [
                                ft.Column(
                                    [
                                        ft.Container(bgcolor="#A2E9E5", expand=True, padding=0),
                                        ft.Container(bgcolor="#C7F3EE", expand=True, padding=0),
                                    ],
                                    expand=True,
                                    spacing=0,
                                ),
                            ]
                        ),
                        self.main_content,
                    ],
                    expand=True,
                ),
                expand=True,
            )
        ]

    def set_selected_emotion(self, emotion_key: str):
        self.selected_emotion = emotion_key

        def style(box: ft.Container, active: bool):
            box.scale = 1.04 if active else 1
            box.bgcolor = (
                ft.Colors.with_opacity(0.25, ft.Colors.WHITE) if active else ft.Colors.with_opacity(0.0, ft.Colors.WHITE)
            )
            box.border = ft.border.all(
                2,
                "#FFFFFF" if active else ft.Colors.with_opacity(0.0, ft.Colors.WHITE),
            )
            box.update()

        style(self.sad_box, emotion_key == "sad")
        style(self.neutral_box, emotion_key == "neutral")
        style(self.happy_box, emotion_key == "happy")

        if self.continue_btn.disabled:
            self.continue_btn.disabled = False
            self.continue_btn.bgcolor = "#FEB836"
            self.continue_btn.color = "#5B2109"
            self.continue_btn.update()

    def set_data(self):
        try:
            user_id = self.page.client_storage.get("user_id")
        except Exception as e:
            user_id = None
            print(f"[DEBUG] user_id okunamadı: {e}")

        try:
            emotion = getattr(self, "selected_emotion", None)
            add_action = self.app.utils.get("add_action")

            seconds = round(float(time.time() - self.start_time), 1)

            if not user_id:
                print("[DEBUG] user_id bulunamadı, action gönderilmeyecek")
            elif not emotion:
                print("[DEBUG] selected_emotion boş, action gönderilmeyecek")
            elif not callable(add_action):
                print("[DEBUG] add_action util'i bulunamadı veya çağrılabilir değil")
            else:
                status = add_action(user_id, ("how_are_you_today", emotion, seconds))
                if status not in (200, 201):
                    print(f"[DEBUG] add_action başarısız: status={status}")
        except Exception as e:
            print(f"[DEBUG] add_action çağrısı sırasında hata: {e}")

        self.page.go("/home")
