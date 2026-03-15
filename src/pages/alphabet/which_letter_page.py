import flet as ft
from random import shuffle, sample
from time import sleep, perf_counter

ASSET_DIR = "modules/which-letter"

class WhichLetterPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/which_letter")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#FFF6E6"
        self.padding = 0

        self.ENTRANCE_MS = 220
        self.ENTRANCE_STAGGER_MS = 40

        self.letters = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
        self.color_pool = [
            "#FE939B", "#FEE557", "#C7F0B8", "#EFB7E6",
            "#B8F0D7", "#FEB157", "#D2BEFB", "#83BCF1"
        ]

        self.option_colors: list[str] = []
        self.options: list[str] = []
        self._tiles: list[ft.Container] = []
        self._option_shells: list[ft.Container] = []

        self.start_time = 0.0
        self.elapsed = 0.0
        self.correct = False

        # Global stats (reset yok, sadece summaryde sıfırlanır)
        if not hasattr(self.app, "letter_stats"):
            self.app.letter_stats = {"played": 0, "correct": 0, "seconds": 0.0}

        self.rebuild()

    def rebuild(self):
        self.start_time = perf_counter()
        self.correct = False

        self.app.play_sound(
            f"{ASSET_DIR}/{self.app.current_letter.lower() if self.app.current_letter != 'I' else 'ı'}.mp3"
        )

        self.option_colors = sample(self.color_pool, k=4)
        self.options = [self.app.current_letter] + sample(
            self.letters.replace(self.app.current_letter, ""), k=3
        )
        shuffle(self.options)

        info_container = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.VOLUME_UP_ROUNDED,
                        icon_size=48,
                        icon_color="#0E444D",
                        on_click=lambda e: self.app.play_sound(
                            f"{ASSET_DIR}/{self.app.current_letter.lower() if self.app.current_letter != 'I' else 'ı'}.mp3"
                        ),
                    ),
                    ft.Text(
                        "Bu harflerden hangisi ...?",
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
            bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
            border_radius=20,
        )

        grid = self._build_options_grid()

        btn_style = ft.ButtonStyle(
            bgcolor="#125563",
            color="#EBE8E1",
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=32),
            elevation=3,
            overlay_color=ft.Colors.with_opacity(0.1, "#FAF5EF"),
            animation_duration=200,
            text_style=ft.TextStyle(size=17, font_family="MPlus"),
        )

        previous_btn = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_LEFT,
            icon_size=32,
            tooltip="Geri",
            style=btn_style,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            height=64,
            width=64,
            on_click=lambda e: self._handle_move(-1),
        )
        replay_btn = ft.IconButton(
            icon=ft.Icons.REPLAY_ROUNDED,
            icon_size=26,
            tooltip="Tekrar oyna",
            style=btn_style,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            height=64,
            width=64,
            on_click=lambda e: self._handle_replay(),
        )
        next_btn = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_RIGHT,
            icon_size=32,
            tooltip="İleri",
            style=btn_style,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            height=64,
            width=64,
            on_click=lambda e: self._handle_move(1),
        )

        bottom_bar = ft.Container(
            height=100,
            bgcolor=ft.Colors.WHITE,
            content=ft.Row(
                [previous_btn, replay_btn, next_btn],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                spacing=12,
            ),
        )

        self.controls = [
            info_container,
            ft.Container(height=12),
            ft.Container(padding=ft.padding.symmetric(0, 30), content=grid),
            ft.Container(expand=True),
            bottom_bar,
        ]

        self.page.update()
        self._stagger_options_entrance()

    def _build_options_grid(self) -> ft.GridView:
        grid = ft.GridView(
            runs_count=2,
            child_aspect_ratio=1,
            spacing=14,
            run_spacing=14,
            expand=False,
            height=360,
        )
        self._tiles.clear()
        self._option_shells.clear()
        for i, letter in enumerate(self.options):
            color = self.option_colors[i % len(self.option_colors)]
            tile = self._option_tile(letter, color)
            shell = ft.Container(
                content=tile,
                opacity=0,
                scale=0.9,
                animate_opacity=self.ENTRANCE_MS,
                animate_scale=ft.Animation(self.ENTRANCE_MS),
            )
            self._option_shells.append(shell)
            grid.controls.append(shell)
        return grid

    def _stagger_options_entrance(self):
        for i, shell in enumerate(self._option_shells):
            shell.opacity = 1
            shell.scale = 1
            self.page.update()
            sleep(self.ENTRANCE_STAGGER_MS / 1000)

    def _option_tile(self, letter: str, color: str) -> ft.Container:
        txt = ft.Text(letter, size=82, font_family="MPlus Bold", color="#002746")
        cont = ft.Container(
            content=txt,
            bgcolor=color,
            border_radius=32,
            alignment=ft.alignment.center,
            aspect_ratio=1,
            ink=True,
            animate_scale=ft.Animation(150, "easeOut"),
            padding=10,
        )
        cont.on_click = lambda e, l=letter, tile=cont: self._on_click(l, tile)
        self._tiles.append(cont)
        return cont

    def _on_click(self, chosen: str, tile: ft.Container):
        self.elapsed = perf_counter() - self.start_time
        # --- İstatistik güncelle ---
        self.app.letter_stats["played"] += 1
        self.app.letter_stats["seconds"] += self.elapsed
        if chosen == self.app.current_letter:
            self.app.letter_stats["correct"] += 1

        for t in self._tiles:
            t.scale = 0.95
            t.disabled = True
            t.bgcolor = "#DBDBDB"

        self.correct = (chosen == self.app.current_letter)
        tile.scale = 1.03
        tile.bgcolor = "#34D399" if self.correct else "#F87171"

        self.page.update()

    def _handle_replay(self):
        self.rebuild()

    def _handle_move(self, _dif: int):
        current_index = self.letters.index(self.app.current_letter)
        next_index = current_index + _dif
        if 0 <= next_index < len(self.letters):
            self.app.current_letter = self.letters[next_index]
            self.rebuild()
        else:
            self.page.run_thread(self._send_summary)
            self.page.go("/alphabet_index")

    def _send_summary(self):
        try:
            user_id = self.page.client_storage.get("user_id")
        except:
            user_id = None

        try:
            add_action = self.app.utils.get("add_action")
            stats = self.app.letter_stats
            if stats["played"] > 0:
                correct_percent = (stats["correct"] / stats["played"]) * 100
                payload = ("which_letter", correct_percent, round(stats["seconds"], 1))
                if user_id and callable(add_action):
                    add_action(user_id, payload)

            self.app.letter_stats = {"played": 0, "correct": 0, "seconds": 0.0}
        except Exception as e:
            print(f"[DEBUG] summary error: {e}")
