import flet as ft

class AudiobooksPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/")
        self.page = page
        self.app = page.app

        self.bgcolor = "#FAF5EF"
        self.padding = 28
        
        def build_button(data):
            return ft.Container(
                expand=True,
                padding=ft.padding.all(16),
                bgcolor=data["bgcolor"],
                border_radius=10,
                on_click=lambda e, route=data["route"]: self.page.go(route),
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=data["icon"],
                                fit=ft.ImageFit.CONTAIN,
                            ),
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text(
                                data["text"],
                                size=18,
                                text_align=ft.TextAlign.CENTER,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                color="#0E444D",
                            ),
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                                icon_color="#0E444D",
                                icon_size=24,
                                bgcolor="#FAF5EF",
                                disabled=True,
                            ),
                            alignment=ft.alignment.center,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                    expand=True,
                ),
            )

        grid_view = ft.GridView(
            runs_count=2,
            max_extent=200,
            spacing=16,
            run_spacing=16,
            child_aspect_ratio=0.7,
            expand=True,
        )

        for button_data in self.app.audiobook_buttons_map:
            grid_view.controls.append(build_button(button_data))

        self.controls = [
            ft.SafeArea(content=
                ft.Column(
                    controls=[
                        ft.Text("Mini Şarkılar", size=30, font_family="MPlus Bold", color="#0E444D"),
                        ft.Text("Dinlemek istediğin şarkıyı seç!", size=18, font_family="MPlus", color="#0E444D"),
                        ft.Container(height=12),
                        grid_view,
                    ],
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ]