import flet as ft
import flet_audio as fta
from router import Router
import utils
from time import sleep

class DownUpApp:
    def main(self, page: ft.Page):
        page.title = "Down Up"
        page.bgcolor = "#FAF5EF"
        page.padding = 0

        if page.platform in (ft.PagePlatform.WINDOWS, ft.PagePlatform.MACOS, ft.PagePlatform.LINUX):
            page.window.width = 1180 // 3
            page.window.height = 2300 // 3
        
        # page.client_storage.clear() # --- DELETE ---
        page.app = self
        self.page = page

        self.utils = {}
        for func_name in dir(utils):
            if not func_name.startswith("__"):
                self.utils[func_name] = getattr(utils, func_name)
        
        page.fonts = {"MPlus": "fonts/mplus-bold.ttf", "MPlus Bold": "fonts/mplus-extrabold.ttf"}
        page.theme = ft.Theme(font_family="MPlus")
        page.theme_mode = ft.ThemeMode.LIGHT

        self.current_letter = "A"

        self.home_buttons_map = [
            {"text": "Duygular", "icon": "home/duygular_icon.png", "bgcolor": "#FBD5BE", "route": "/emotions_index"},
            {"text": "Alfabe", "icon": "home/alfabe_icon.png", "bgcolor": "#B7DABA", "route": "/alphabet_index"},
            {"text": "Günlük Yaşam", "icon": "home/gunluk_yasam_icon.png", "bgcolor": "#C7E1C4", "route": "/daily_life_index"},
            {"text": "Matematik", "icon": "home/matematik_icon.png", "bgcolor": "#C6D3E3", "route": "/maths_index"},
            {"text": "Hafıza & Problem", "icon": "home/hafiza_icon.png", "bgcolor": "#DED3E4", "route": "/memory_index"},
            {"text": "Müzik & Ritim", "icon": "home/muzik_icon.png", "bgcolor": "#F2ACA0", "route": "/music_index"},
        ]
        self.home_route_names = {item["route"]: item["text"] for item in self.home_buttons_map}

        self.audiobook_buttons_map = [
            {"text": "Ali Baba'nın Çiftliği", "icon": "audiobooks/ali-baba.png", "bgcolor": "#A3E2A7", "route": "/audiobook/ali-baba", "voice": "Duru Gezekli"},
            {"text": "Bay Yumurtacık", "icon": "audiobooks/bay-yumurtacik.png", "bgcolor": "#FFBD8E", "route": "/audiobook/bay-yumurtacik", "voice": "Ayberk Atalay"},
            {"text": "Küçük Kurbağa", "icon": "audiobooks/kucuk-kurbaga.png", "bgcolor": "#BDD3EA", "route": "/audiobook/kucuk-kurbaga", "voice": "Ayberk Atalay"},
            {"text": "Arı Vız Vız Vız", "icon": "audiobooks/ari-viz-viz-viz.png", "bgcolor": "#BDC1EA", "route": "/audiobook/ari-viz-viz-viz", "voice": "Ayberk Atalay"},
        ]
        self.audiobook_datas_by_route = {item["route"]: item for item in self.audiobook_buttons_map}

        navigation_hashmap = {0: "/home", 1: "/audiobooks", 2: "/observer"}
        self.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME_ROUNDED, 
                    label="Ana Sayfa",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.BOOK_ROUNDED, 
                    label="Mini Şarkılar",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.TRACK_CHANGES_ROUNDED,
                    label="Çalışma Takibi",
                ),
            ],
            on_change=lambda e: page.go(navigation_hashmap[self.navigation_bar.selected_index]),
        )

        self.home_appbar = ft.AppBar(
            title=ft.Text("", color="#0E444D"),
            center_title=True,
            leading=ft.Container(
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: page.go("/home"),
                    icon_color="#0E444D",
                    icon_size=32,
                ),
                padding=4
            )
        )

        self.audiobooks_appbar = ft.AppBar(
            title=ft.Text("Mini Şarkı", color="#0E444D"),
            center_title=True,
            leading=ft.Container(
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: page.go("/audiobooks"),
                    icon_color="#0E444D",
                    icon_size=32,
                ),
                padding=4
            )
        )

        self.modules_appbar = ft.AppBar(
            title=ft.Text("Modül", color="#0E444D"),
            center_title=True,
            leading=ft.Container(
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color="#0E444D",
                    icon_size=32,
                ),
                padding=4
            ),
        )

        self.button_style = ft.ButtonStyle(
            bgcolor="#0E444D",
            color="#FAF5EF",
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=15),
            elevation=3,
            overlay_color=ft.Colors.with_opacity(0.1, "#FAF5EF"),
            animation_duration=200,
            text_style=ft.TextStyle(size=17, font_family="MPlus")
        )

        self.audio = fta.Audio(
            src="null",
            autoplay=False,
            volume=1.0,
        )
        page.overlay.append(self.audio)

        self.router = Router(page)
        page.on_route_change = lambda e: self.router.route_change()
        self.router.initialize()

    def get_index_element(self, title, thumbnail_path, target_route, fake=False):
        return ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Image(
                        src=thumbnail_path,
                        fit=ft.ImageFit.COVER,
                        width=float("inf"),
                        height=float("inf"),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Text(title, size=20, color="#0E444D"),
                                    border_radius=10,
                                    bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
                                    padding=ft.Padding(15, 5, 15, 5),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                        ),
                        padding=10,
                        alignment=ft.alignment.bottom_left,
                        bgcolor=ft.Colors.with_opacity(0, ft.Colors.WHITE),
                    )
                ]
            ),
            border_radius=10,
            height=200,
            on_click=(lambda e: self.page.go(target_route)) if not fake else (lambda e: e),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
                blur_style=ft.ShadowBlurStyle.NORMAL,
            ),
        )
    
    def play_sound(self, path):
        self.page.update()
        self.audio.src = path
        self.page.update()
        self.audio.on_loaded = self._play_on_load
        self.audio.seek(0)
        self.audio.play()
        self.page.update()
        
    def _play_on_load(self, e):
        self.audio.seek(0)
        self.audio.play()
        self.page.update()

    def check_connection(self):
        try:
            check_internet = self.utils["check_internet"]()
            check_server = self.utils["check_server"]()
        except:
            check_internet = False
            check_server = False
        if (not check_internet) or (not check_server):
            self.page.go("/no_connection")
            return True
        return False

ft.app(target=DownUpApp().main, name="Down Up")
