import flet as ft

# --- Constants ---
STUDENT = 0
OBSERVER = 1

class LoginPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/login")
        self.page = page
        self.app = page.app

        self.padding = 0
        self.bgcolor = "#FAF5EF"

        self.loading_overlay = ft.Container(
            visible=False,
            bgcolor=ft.Colors.with_opacity(0.6, "#0E444D"),
            alignment=ft.alignment.center,
            content=ft.ProgressRing(width=64, height=64, color="#1B747F"),
            expand=True,
        )

        student_button_style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10), padding=ft.Padding(24, 12, 24, 12),
            text_style=ft.TextStyle(size=26, font_family="MPlus"),
            bgcolor="#F5761C", color="#FFEEE2"
        )
        observer_button_style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10), padding=ft.Padding(24, 12, 24, 12),
            text_style=ft.TextStyle(size=26, font_family="MPlus"),
            bgcolor="#1B747F", color="#D6F8FD"
        )

        self.main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Giriş seçimi", size=40, weight=ft.FontWeight.BOLD, color="#125C65"),
                    ft.Container(
                        content=ft.Image("login/bg.png", fit=ft.ImageFit.FIT_WIDTH),
                        alignment=ft.alignment.center,
                        padding=0,
                    ),
                    ft.Row([
                        ft.ElevatedButton(
                            "Öğrenci",
                            style=student_button_style,
                            on_click=lambda e: self.page.run_thread(self.register, STUDENT)
                        ),
                        ft.ElevatedButton(
                            "Gözetmen",
                            style=observer_button_style,
                            on_click=lambda e: self.page.run_thread(self.register, OBSERVER)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER)
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
                        ft.Stack([
                            ft.Column(
                                [
                                    ft.Container(bgcolor="#A2E9E5", expand=True, padding=0),
                                    ft.Container(bgcolor="#C7F3EE", expand=True, padding=0),
                                ],
                                expand=True,
                                spacing=0,
                            ),
                        ]),
                        self.main_content,
                        self.loading_overlay,
                    ],
                    expand=True,
                ),
                expand=True
            )
        ]

    def register(self, role: int):
        self.loading_overlay.visible = True
        self.page.update()

        try:
            status_code, user_id = self.app.utils["register"](role)

            if status_code in (200, 201):
                self.page.client_storage.set("user_id", user_id)
                self.page.client_storage.set("role", role)
                self.app.router.initialize()
            else:
                print(f"Sunucu hatası: Giriş yapılamadı. ({status_code})")
        except Exception as e:
            print(f"API hatası: Giriş yapılamadı. {e}")
        finally:
            self.loading_overlay.visible = False
            self.page.update()
