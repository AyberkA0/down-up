import flet as ft

TEXT_COLOR = "#0E444D"

def status_chip(text, ok):
    if ok is True:
        icon, color, label = ft.Icons.CHECK_CIRCLE_ROUNDED, "#22C55E", "UYGUN"
    elif ok is False:
        icon, color, label = ft.Icons.CANCEL_ROUNDED, "#EF4444", "HATA"
    else:
        icon, color, label = ft.Icons.HOURGLASS_EMPTY_ROUNDED, "#F59E0B", "????"

    return ft.Container(
        padding=ft.padding.symmetric(8, 6),
        border_radius=999,
        bgcolor=ft.Colors.with_opacity(0.08, color),
        content=ft.Row(
            [
                ft.Icon(icon, size=16, color=color),
                ft.Text(label, size=12, color=color, weight=ft.FontWeight.W_600),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

class NoConnectionPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/no_connection")
        self.app = page.app
        self.page = page
        self.bgcolor = "#FAF5EF"
        self.padding = 20
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

        self.hero_card = ft.Container(
            width=420,
            padding=20,
            border_radius=24,
            bgcolor=ft.Colors.WHITE,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#FFFFFF", "#F3FAFF"],
            ),
            content=self._build_hero(),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=30, color="#00000020"),
        )

        self.internet_ok = None
        self.api_ok = None

        self.internet_row = self._status_row(
            icon=ft.Icons.WIFI_OFF_ROUNDED, title="İnternet erişimi", description="Kontrol ediliyor..."
        )
        self.api_row = self._status_row(
            icon=ft.Icons.CLOUD_ROUNDED, title="Sunucu erişimi", description="Kontrol ediliyor..."
        )

        self.status_card = ft.Container(
            width=420,
            padding=18,
            border_radius=20,
            bgcolor=ft.Colors.WHITE,
            content=ft.Column(
                [
                    ft.Row(
                        [ft.Text("Durum", size=18, weight=ft.FontWeight.W_700, color=TEXT_COLOR)],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.internet_row,
                    self.api_row,
                ],
                spacing=12,
            ),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=20, color="#00000015"),
        )

        self.ring = ft.ProgressRing(width=22, height=22, visible=False)
        self.retry_btn = ft.ElevatedButton(
            "Tekrar Dene",
            icon=ft.Icons.REFRESH_ROUNDED,
            on_click=self._on_retry,
            style=self.app.button_style,
        )

        self.controls = [
            ft.Column(
                [
                    self.hero_card,
                    ft.Container(height=0),
                    self.status_card,
                    ft.Container(height=8),
                    ft.Row(
                        [self.retry_btn, self.ring],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                expand=False,
            )
        ]

    def _build_hero(self) -> ft.Column:
        big_icon = ft.Container(
            width=84,
            height=84,
            border_radius=999,
            bgcolor=ft.Colors.with_opacity(0.08, "#EF4444"),
            alignment=ft.alignment.center,
            content=ft.Icon(ft.Icons.WIFI_OFF_ROUNDED, size=44, color="#EF4444"),
        )
        title = ft.Text("Bağlantı yok", size=28, weight=ft.FontWeight.W_800, color=TEXT_COLOR)
        subtitle = ft.Text(
            "İnternet bağlantınızı kontrol edip tekrar deneyin.",
            size=14,
            color=TEXT_COLOR,
            opacity=0.9,
        )

        line = ft.Row(
            [
                ft.Icon(ft.Icons.DEVICE_HUB_ROUNDED, size=20, color=TEXT_COLOR),
                ft.Divider(height=1, thickness=2, color="#E5EEF2"),
                ft.Icon(ft.Icons.CLOUD_OFF_ROUNDED, size=20, color=TEXT_COLOR),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Column([big_icon, title, subtitle, ft.Container(height=6), line],
                         spacing=10,
                         horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _status_row(self, icon, title: str, description: str) -> ft.Container:
        chip = status_chip("Durum", None)
        row = ft.Row(
            [
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=12,
                    bgcolor="#F5F9FB",
                    alignment=ft.alignment.center,
                    content=ft.Icon(icon, size=22, color=TEXT_COLOR),
                ),
                ft.Column(
                    [
                        ft.Text(title, size=14, weight=ft.FontWeight.W_700, color=TEXT_COLOR),
                        ft.Text(description, size=12, color=TEXT_COLOR, opacity=0.9),
                    ],
                    spacing=2,
                    expand=True,
                ),
                chip,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        )
        c = ft.Container(content=row, padding=ft.padding.symmetric(12, 10), border_radius=14, bgcolor="#FAFCFD")

        c._chip = chip
        c._desc = row.controls[1].controls[1]
        return c

    def _set_loading(self, loading: bool):
        self.ring.visible = loading
        self.retry_btn.disabled = loading
        self.page.update()

    def _apply_status(self, row_container: ft.Container, ok: bool | None, description: str | None = None):
        row_container._chip.content = status_chip("Durum", ok).content
        if description is not None:
            row_container._desc.value = description
        self.page.update()

    def _on_retry(self, e):
        self._set_loading(True)

        try:
            net_ok = self.app.utils["check_internet"]()
        except:
            net_ok = False
        self._apply_status(
            self.internet_row,
            net_ok,
            "Ağ bağlantısı mevcut." if net_ok else "Ağ bağlantısı bulunamadı.",
        )

        api_ok = False
        if net_ok:
            try:
                api_ok = self.app.utils["check_server"]()
            except:
                api_ok = False
        self._apply_status(
            self.api_row,
            api_ok if net_ok else None,
            "Sunucuya erişilemiyor." if net_ok and not api_ok else (
                "Sunucuya erişildi." if api_ok else "Sunucu kontrolü atlandı."
            ),
        )

        self._set_loading(False)

        self.app.router.initialize()