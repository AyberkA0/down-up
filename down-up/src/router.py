import flet as ft

from pages.login_page import LoginPage
from pages.no_connection_page import NoConnectionPage
from pages.how_are_you_today_page import HowAreYouTodayPage

from pages.home_page import HomePage
from pages.audiobooks_page import AudiobooksPage
from pages.observer_page import ObserverPage

from pages.audiobook_page import AudiobookPage

from pages.emotions.emotions_index_page import EmotionsIndexPage
from pages.emotions.whats_going_on_page import WhatsGoingOnPage
from pages.emotions.which_kid_has_emotion_page import WhichKidHasEmotionPage

from pages.alphabet.alphabet_index_page import AlphabetIndexPage
from pages.alphabet.which_letter_page import WhichLetterPage

from pages.daily_life.daily_life_index_page import DailyLifeIndexPage
from pages.daily_life.tooth_brushing_page import ToothBrushingPage
from pages.daily_life.healthy_foods_page import HealthyFoodsPage

from pages.maths.maths_index_page import MathsIndexPage
from pages.maths.how_much_page import HowMuchPage
from pages.maths.name_shapes_page import NameShapesPage

from pages.memory.memory_index_page import MemoryIndexPage
from pages.memory.memory_cards_page import MemoryCardsPage

from pages.music.music_index_page import MusicIndexPage
from pages.music.clap_rhythm_page import ClapRhythmPage

# --- Constants ---
STUDENT = 0
OBSERVER = 1

class Router:
    def __init__(self, page):
        self.page = page
        self.app = page.app
        self._loading_overlay = None

    def _show_loading(self):
        if self._loading_overlay is not None:
            return
        self._loading_overlay = ft.Container(
            expand=True,
            opacity=1,
            alignment=ft.alignment.center,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.ProgressRing(width=64, height=64, stroke_width=6, color="#0E444D"),
                ],
            ),
        )
        self.page.overlay.append(self._loading_overlay)
        self.page.update()

    def _hide_loading(self):
        if self._loading_overlay is None:
            return

        try:
            if self._loading_overlay in self.page.overlay:
                self.page.overlay.remove(self._loading_overlay)
        except Exception:
            pass
        self._loading_overlay = None
        self.page.update()

    def initialize(self):
        self._show_loading()

        try:
            ret = self.app.check_connection()
            if ret: return

            user_id = self.page.client_storage.get("user_id")
            role = self.page.client_storage.get("role")
            is_user_id_valid = self.app.utils["is_user_id_valid"](user_id)
            if role in (STUDENT, OBSERVER) and is_user_id_valid:
                is_last_online_today = self.app.utils["is_last_online_today"](self.page)
                status_code = self.app.utils["update_last_online"](user_id, self.page)

                if not is_last_online_today:
                    self.page.go("/how_are_you_today")
                    return

                if status_code in (200, 201):
                    if role == STUDENT:
                        self.page.go("/home")
                    elif role == OBSERVER:
                        self.page.go("/observer")
                else:
                    print(f"Sunucu hatası: 'last_online' belirlenemedi. ({status_code})")
            else:
                self.page.client_storage.clear()
                self.page.go("/login")
        finally:
            self._hide_loading()

    def route_change(self):
        self.clear_audio()

        self.page.views.clear()
        view = None

        if self.page.route == "/login":
            view = LoginPage(self.page)
        elif self.page.route == "/no_connection":
            view = NoConnectionPage(self.page)
        elif self.page.route == "/how_are_you_today":
            view = HowAreYouTodayPage(self.page)

        elif self.page.route == "/home":
            view = HomePage(self.page)
        elif self.page.route == "/audiobooks":
            view = AudiobooksPage(self.page)
        elif self.page.route == "/observer":
            view = ObserverPage(self.page)

        elif self.page.route.startswith("/audiobook"):
            view = AudiobookPage(self.page)

        elif self.page.route == "/emotions_index":
            view = EmotionsIndexPage(self.page)
        elif self.page.route == "/alphabet_index":
            view = AlphabetIndexPage(self.page)
        elif self.page.route == "/daily_life_index":
            view = DailyLifeIndexPage(self.page)
        elif self.page.route == "/maths_index":
            view = MathsIndexPage(self.page)
        elif self.page.route == "/memory_index":
            view = MemoryIndexPage(self.page)
        elif self.page.route == "/music_index":
            view = MusicIndexPage(self.page)

        elif self.page.route == "/tooth_brushing":
            view = ToothBrushingPage(self.page)
        elif self.page.route == "/healthy_foods":
            view = HealthyFoodsPage(self.page)
        elif self.page.route == "/memory_cards":
            view = MemoryCardsPage(self.page)
        elif self.page.route == "/clap_rhythm":
            view = ClapRhythmPage(self.page)
        elif self.page.route == "/how_much":
            view = HowMuchPage(self.page)
        elif self.page.route == "/name_shapes":
            view = NameShapesPage(self.page)
        elif self.page.route == "/which_letter":
            view = WhichLetterPage(self.page)
        elif self.page.route == "/which_kid_has_emotion":
            view = WhichKidHasEmotionPage(self.page)
        elif self.page.route == "/whats_going_on":
            view = WhatsGoingOnPage(self.page)
        else:
            self.initialize()

        role = self.page.client_storage.get("role")
        if (self.page.route in ("/home", "/audiobooks")) or (self.page.route == "/observer" and role == STUDENT):
            view.navigation_bar = self.app.navigation_bar
            view.navigation_bar.bgcolor = view.bgcolor

        elif self.page.route.endswith("_index"):
            view.appbar = self.app.home_appbar
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = self.app.home_route_names[self.page.route]

        elif self.page.route.startswith("/audiobook/"):
            view.appbar = self.app.audiobooks_appbar
            view.appbar.bgcolor = view.bgcolor

        elif "/tooth_brushing" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/daily_life_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Diş Fırçalama"
        elif "/healthy_foods" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/daily_life_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Sağlıklı Beslen"
        elif "/memory_cards" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/memory_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Kartları Hatırla"
        elif "/clap_rhythm" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/music_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Ritmi Yakala"
        elif "/how_much" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/maths_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Kaç tane kalır?"
        elif "/name_shapes" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/maths_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Şekilleri Keşfet"
        elif "/which_letter" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/alphabet_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Alfabe Avı"
        elif "/whats_going_on" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/emotions_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Ne oldu burada?"
        elif "/which_kid_has_emotion" in self.page.route:
            view.appbar = self.app.modules_appbar
            view.appbar.leading.content.on_click = lambda e: self.page.go("/emotions_index")
            view.appbar.bgcolor = view.bgcolor
            view.appbar.title.value = "Duyguları Tanı"

        if view is not None:
            self.page.views.append(view)
        self.page.update()

    def clear_audio(self):
        for control in self.page.overlay:
            if type(control).__name__ == "Audio":
                try:
                    control.pause()
                    control.update()
                except: pass
