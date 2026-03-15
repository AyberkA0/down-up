import flet as ft
from time import sleep

class AudiobookPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/audiobook")
        self.page = page
        self.app = page.app

        data = self.app.audiobook_datas_by_route[self.page.route]

        self.bgcolor = "#FAF5EF"
        self.padding = 28

        filename = self.page.route.split("/")[-1] + ".mp3"
        src = f"audiobooks/{filename}"

        self.playing = False
        self.is_last_state_is_playing = False

        self.play_button = ft.IconButton(icon=ft.Icons.PLAY_ARROW_ROUNDED, icon_size=48, on_click=self.toggle_play)
        self.slider = ft.Slider(min=0, max=0, value=0, expand=True, on_change_start=self.on_slider_change_start, on_change_end=self.on_slider_change_end)
        self.time_text = ft.Text("00.00 / 00.00", size=14, color="#0E444D")
        replay_button = ft.IconButton(icon=ft.Icons.REPLAY_10_ROUNDED, icon_size=32, on_click=lambda e: self.shift_audio_seek(-10))
        forward_button = ft.IconButton(icon=ft.Icons.FORWARD_10_ROUNDED, icon_size=32, on_click=lambda e: self.shift_audio_seek(10))

        self.audio = self.app.audio
        if self.audio.src == src:
            self.on_audio_loaded()
        else:
            self.audio.src = src
        self.audio.on_loaded = self.on_audio_loaded
        self.audio.on_position_changed = self.on_audio_position_changed

        image_container = ft.Container(
            content=ft.Image(
                src=data["icon"],
                fit=ft.ImageFit.CONTAIN,
                scale=0.5
            ),
            bgcolor=data["bgcolor"],
            border_radius=10,
            alignment=ft.alignment.center,
            aspect_ratio=1,
        )

        self.vertical_alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.controls = [
            image_container,
            ft.Container(
                ft.Column(
                    controls=[
                        ft.Text(data["text"], size=24, font_family="MPlus Bold", color="#0E444D"),
                        ft.Text(data["voice"], size=16, color="#0E444D"),
                    ],
                    spacing=0,
                ),
                alignment=ft.alignment.center_left
            ),
            ft.Container(height=12),
            ft.Row([self.slider], alignment=ft.MainAxisAlignment.CENTER),
            self.time_text,
            ft.Container(height=12),
            ft.Row([replay_button, self.play_button, forward_button], alignment=ft.MainAxisAlignment.CENTER),
        ]

    def toggle_play(self, e=None, force=None):
        if self.playing or force is False:
            self.audio.pause()
            self.play_button.icon = ft.Icons.PLAY_ARROW_ROUNDED
            self.playing = False
        elif (not self.playing) or force is True:
            self.audio.resume()
            self.play_button.icon = ft.Icons.PAUSE
            self.playing = True

        self.page.update()

    def shift_audio_seek(self, shift):
        self.audio.seek(int((self.slider.value+shift) * 1000))

    def on_audio_loaded(self, e=None):
        if self.audio.src == "null": return
        self.slider.max = int(self.audio.get_duration()/1000)
        self.time_text.value = f"00.00 / {self.ms_to_mmss(self.slider.max*1000)}"
        self.audio.seek(0)
        self.page.update()

    def on_audio_position_changed(self, e=None):
        current_position = e.position
        self.time_text.value = f"{self.ms_to_mmss(current_position)} / {self.ms_to_mmss(self.slider.max*1000)}"
        self.slider.value = min(self.slider.max, current_position/1000)
        if self.slider.value == self.slider.max: 
            self.audio.seek(0)
            self.toggle_play(force=False)
        self.audio.page.update()

    def on_slider_change_start(self, e=None):
        self.is_last_state_is_playing = self.playing
        self.toggle_play(force=False)

    def on_slider_change_end(self, e=None):
        sleep(0.2)
        target_position = int(self.slider.value * 1000)
        self.audio.seek(target_position)
        self.toggle_play(force=True if self.is_last_state_is_playing else False)

    def ms_to_mmss(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02}.{remaining_seconds:02}"