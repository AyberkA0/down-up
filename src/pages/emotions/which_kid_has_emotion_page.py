import flet as ft
from random import shuffle, sample
from time import sleep, perf_counter

# --- Constants ---
ASSET_DIR = "modules/which-kid-has-emotion"

class WhichKidHasEmotionPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/which_kid_has_emotion")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#F6E8FF"
        self.padding = 0

        self.ENTRANCE_MS = 220
        self.ENTRANCE_STAGGER_MS = 40

        self.color_pool = [
            "#FE939B", "#FEE557", "#CAFFB7", "#FFA5F0",
            "#B8F0D7", "#FEB157", "#CDB3FF", "#83BCF1"
        ]
        self.bg_colors = {
            "#FE939B": "#FFC3C7", 
            "#FEE557": "#FFF5BA", 
            "#CAFFB7": "#E8FFE1", 
            "#FFA5F0": "#FFC9F5",
            "#B8F0D7": "#E1FFF2", 
            "#FEB157": "#FFEAD1", 
            "#CDB3FF": "#DECAFF", 
            "#83BCF1": "#D0E8FF",
        }

        self.emotions = ["neseli", "uzgun", "korkmus", "ofkeli", "sasirmis", "utanmis", "tiksinmis"]
        self.tr_labels = {
            "neseli": "neşeli",
            "uzgun": "üzgün",
            "korkmus": "korkmuş",
            "ofkeli": "öfkeli",
            "sasirmis": "şaşkın",
            "utanmis": "utanmış",
            "tiksinmis": "tiksinmiş",
        }

        self.current_index = 0
        self.target = self.emotions[self.current_index]

        self.option_colors: list[str] = []
        self.options: list[str] = []
        self._tiles: list[ft.Container] = []
        self._option_shells: list[ft.Container] = []

        self.start_time = 0.0
        self.elapsed = 0.0
        self.correct = False

        # Global stats
        if not hasattr(self.app, "emotion_stats"):
            self.app.emotion_stats = {"played": 0, "correct": 0, "seconds": 0.0}

        self.rebuild()

    def rebuild(self):
        self.start_time = perf_counter()
        self.correct = False

        self.target = self.emotions[self.current_index]
        self.app.play_sound(f"{ASSET_DIR}/{self.target}.mp3")

        self.option_colors = sample(self.color_pool, k=4)
        others = [e for e in self.emotions if e != self.target]
        self.options = [self.target] + sample(others, k=3)
        shuffle(self.options)

        info_container = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.VOLUME_UP_ROUNDED,
                        icon_size=48,
                        icon_color="#0E444D",
                        on_click=lambda e: self.app.play_sound(f"{ASSET_DIR}/{self.target}.mp3"),
                    ),
                    ft.Text(
                        f"Hangi resimdeki çocuk {self.tr_labels[self.target]}?",
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
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
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
            border=ft.Border(ft.BorderSide(3, "#FCF7FF"), None, None, None),
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

        for i, emo in enumerate(self.options):
            color = self.option_colors[i % len(self.option_colors)]
            tile = self._option_tile(emo, color)

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
        for shell in self._option_shells:
            shell.opacity = 1
            shell.scale = 1
            self.page.update()
            sleep(self.ENTRANCE_STAGGER_MS / 1000)

    def _option_tile(self, emo: str, color: str) -> ft.Container:
        img = ft.Image(src=f"{ASSET_DIR}/{emo}.png", fit=ft.ImageFit.FIT_HEIGHT)
        cont = ft.Container(
            content=img,
            bgcolor=self.bg_colors[color],
            border=ft.border.all(4, color),
            border_radius=20,
            alignment=ft.alignment.bottom_center,
            aspect_ratio=1,
            ink=True,
            animate_scale=ft.Animation(150, "easeOut"),
            padding=ft.Padding(0, 10, 0, 0),
        )
        cont.on_click = lambda e, chosen=emo, tile=cont: self._on_click(chosen, tile)
        self._tiles.append(cont)
        return cont

    def _on_click(self, chosen: str, tile: ft.Container):
        self.elapsed = perf_counter() - self.start_time

        self.app.emotion_stats["played"] += 1
        self.app.emotion_stats["seconds"] += self.elapsed
        if chosen == self.target:
            self.app.emotion_stats["correct"] += 1

        for t in self._tiles:
            t.scale = 0.95
            t.disabled = True
            t.bgcolor = "#DBDBDB"
            t.border = None
            if t != tile:
                t.content.opacity = 0.7

        self.correct = (chosen == self.target)
        tile.scale = 1.03
        tile.bgcolor = "#34D399" if self.correct else "#F87171"

        self.page.update()

    def _handle_replay(self):
        self.rebuild()

    def _handle_move(self, diff: int):
        next_index = self.current_index + diff
        if 0 <= next_index < len(self.emotions):
            self.current_index = next_index
            self.rebuild()
        else:
            self.page.run_thread(self._send_summary)
            self.page.go("/emotions_index")

    def _send_summary(self):
        print("debug")
        try:
            user_id = self.page.client_storage.get("user_id")
        except:
            user_id = None

        try:
            add_action = self.app.utils.get("add_action")
            stats = self.app.emotion_stats
            if stats["played"] > 0:
                correct_percent = (stats["correct"] / stats["played"]) * 100
                payload = ("which_kid_has_emotion", correct_percent, round(stats["seconds"], 1))
                if user_id and callable(add_action):
                    add_action(user_id, payload)

            self.app.emotion_stats = {"played": 0, "correct": 0, "seconds": 0.0}
        except Exception as e:
            print(f"[DEBUG] summary error: {e}")
