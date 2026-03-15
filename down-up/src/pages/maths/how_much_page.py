import asyncio
import flet as ft
from random import choice, shuffle, randint
from time import perf_counter
import threading

ASSET_DIR = "modules/how-much"

class HowMuchPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/how_much")
        self.page = page
        self.app = getattr(page, "app", None)
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.padding = 0
        self.bgcolor = "#CEEFFF"
        self._locked = False
        self.option_buttons = []

        # tur süresi
        self.start_time = 0.0

        self._setup_round_state()

        self.app.play_sound(f"{ASSET_DIR}/{self.change}")

        self.info_button = ft.IconButton(
            icon=ft.Icons.VOLUME_UP_ROUNDED,
            icon_size=48,
            icon_color="#0E444D",
            on_click=lambda e: self.app.play_sound(f"{ASSET_DIR}/{self.change}"),
        )
        self.info_text = ft.Text(self.prompt_text, max_lines=2, expand=True, size=18, color="#0E444D")
        self.info_container = ft.Container(
            content=ft.Row([self.info_button, self.info_text]),
            margin=ft.Margin(0, 30, 0, 0),
            scale=0.9,
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
            border_radius=20,
            animate_opacity=300,
            opacity=1.0,
        )

        self.current_image = ft.Image(src=f"{ASSET_DIR}/{self.current}", fit=ft.ImageFit.FIT_WIDTH, scale=0.7)
        self.current_image_holder = ft.Container(
            content=self.current_image,
            top=0,
            opacity=1.0,
            scale=1,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
        )
        image_stack = ft.Container(
            content=ft.Stack(
                alignment=ft.alignment.center,
                controls=[
                    ft.Image(src=f"{ASSET_DIR}/bg.png", fit=ft.ImageFit.FIT_WIDTH),
                    self.current_image_holder,
                ],
            ),
        )

        def make_option_btn(val: int) -> ft.Container:
            c = ft.Container(
                width=64,
                height=52,
                bgcolor="#FFFFFF",
                border_radius=15,
                alignment=ft.alignment.center,
                content=ft.Text(str(val), size=20, weight=ft.FontWeight.W_600, color="#0E444D"),
                animate=ft.Animation(250, "easeOut"),
                animate_scale=ft.Animation(250, "easeOut"),
                shadow=ft.BoxShadow(blur_radius=6, spread_radius=1, color=ft.Colors.with_opacity(0.1, "#000")),
                on_click=lambda e, v=val: self.on_option_click_value_button(v, c),
            )
            return c

        self.options_row = ft.Row(
            controls=[make_option_btn(v) for v in self.options],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=0,
            opacity=1,
            animate_opacity=ft.Animation(300, "easeInOut"),
            visible=True,
        )
        self.option_buttons = list(self.options_row.controls)

        self.finish_btn = ft.FilledButton(
            text="Bitir",
            style=self.app.button_style,
            height=50,
            width=self.page.width // 1.5 if self.page.width else 320,
            animate_opacity=ft.Animation(300, "easeOut"),
            animate_scale=ft.Animation(300, "easeOut"),
            scale=0.8,
            opacity=0,
            disabled=True,
            visible=True,
            on_click=lambda e: self.page.go("/maths_index"),
        )
        self.replay_btn = ft.IconButton(
            icon=ft.Icons.REPLAY_ROUNDED,
            icon_size=20,
            tooltip="Tekrar oyna",
            opacity=0,
            disabled=True,
            style=self.app.button_style,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            height=50,
            width=50,
            on_click=self._handle_replay,
        )

        self.actions_row = ft.Row(
            controls=[self.finish_btn, self.replay_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            visible=False,
        )

        bottom_bar = ft.Container(
            height=120,
            bgcolor="#EBF8FF",
            content=ft.Stack(alignment=ft.alignment.center, controls=[self.options_row, self.actions_row]),
            border=ft.Border(ft.BorderSide(width=3, color="#C9DABC"), None, None, None),
        )

        self.controls = [
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    ft.SafeArea(content=self.info_container, top=True, bottom=False),
                    ft.Container(expand=True),
                    image_stack,
                    ft.SafeArea(content=bottom_bar, top=False, bottom=True),
                ],
            )
        ]

        self.start_time = perf_counter()

    def _setup_round_state(self):
        changes = ["-1a.mp3","-1p.mp3","-2a.mp3","-2p.mp3","-3a.mp3","-3p.mp3","-4a.mp3","-4p.mp3"]
        currents = ["1a-3p.png","1a-4p.png","2a-3p.png","2a-4p.png","3a-1p.png","3a-2p.png","3a-3p.png","4a-1p.png","4a-2p.png"]
        def parse_counts(s):
            a = int(s.split("-")[0][0])
            p = int(s.split("-")[1][0])
            return {"a": a, "p": p}
        def all_pairs_with_answers():
            pairs = []
            for ch in changes:
                cr = ch.removesuffix(".mp3")
                t = cr[-1]
                dif = int(cr[:-1])
                for cur in currents:
                    counts = parse_counts(cur.removesuffix(".png"))
                    if counts[t] + dif >= 0:
                        ans = counts[t] + dif
                        pairs.append((cur, ch, t, dif, ans))
            return pairs
        pairs = all_pairs_with_answers()
        target = choice([0, 1, 2, 3])
        cand = [p for p in pairs if p[4] == target]
        self.current, self.change, _type, dif, self.answer = choice(cand)
        current_raw = self.current.removesuffix(".png")
        def answer():
            for i in current_raw.split("-"):
                if _type in i:
                    return int(i[0]) + dif
            return -1
        self.answer = answer()
        max_val = 5
        window = 3
        pos = randint(0, window-1)
        base = max(0, min(max_val - window, self.answer - pos))
        self.options = [base + i for i in range(window)]
        shuffle(self.options)
        is_decrease = self.change.startswith('-')
        is_apple = self.change[2] == "a"
        self.prompt_text = (
            f"Bu {'sepetten' if is_decrease else 'sepete'} "
            f"{self.change[1]} {'elma' if is_apple else 'armut'} "
            f"{'yenilirse' if is_decrease else 'eklenirse'} kaç "
            f"{'elma' if is_apple else 'armut'} {'kalır' if is_decrease else 'olur'}?"
        )

    def _build_page(self):
        self._setup_round_state()

        self.app.play_sound(f"{ASSET_DIR}/{self.change}")
        self.info_button.on_click = lambda e: self.app.play_sound(f"{ASSET_DIR}/{self.change}")

        self.info_text.value = self.prompt_text
        self.current_image.src = f"{ASSET_DIR}/{self.current}"
        def make_option_btn(val: int) -> ft.Container:
            c = ft.Container(
                width=64,
                height=52,
                bgcolor="#FFFFFF",
                border_radius=15,
                alignment=ft.alignment.center,
                content=ft.Text(str(val), size=20, weight=ft.FontWeight.W_600, color="#0E444D"),
                animate=300,
                animate_scale=300,
                shadow=ft.BoxShadow(blur_radius=6, spread_radius=1, color=ft.Colors.with_opacity(0.15, "#000")),
                on_click=lambda e, v=val: self.on_option_click_value_button(v, c),
            )
            return c
        self.options_row.controls = [make_option_btn(v) for v in self.options]
        self.option_buttons = list(self.options_row.controls)
        self.options_row.visible = True
        self.options_row.opacity = 0.0
        self.finish_btn.disabled = True
        self.finish_btn.visible = True
        self.finish_btn.opacity = 0.0
        self.finish_btn.scale = 0.8
        self.replay_btn.disabled = True
        self.replay_btn.visible = True
        self.replay_btn.opacity = 0.0
        self.replay_btn.scale = 0.8
        self.actions_row.visible = False
        self._locked = False
        self.info_container.opacity = 0.0
        self.current_image_holder.opacity = 0.0
        self.current_image_holder.scale = 0.92
        self.info_text.update()
        self.current_image.update()
        self.options_row.update()
        self.finish_btn.update()
        self.replay_btn.update()
        self.actions_row.update()
        self.info_container.update()
        self.current_image_holder.update()

        self.start_time = perf_counter()

        async def _enter_anim():
            await asyncio.sleep(0.05)
            self.info_container.opacity = 1.0
            self.info_container.update()
            await asyncio.sleep(0.06)
            self.current_image_holder.opacity = 1.0
            self.current_image_holder.scale = 1.0
            self.current_image_holder.update()
            await asyncio.sleep(0.08)
            self.options_row.opacity = 1.0
            self.options_row.update()
        self.page.run_task(_enter_anim)

    def _handle_replay(self, e=None):
        async def _anim():
            self.replay_btn.disabled = True
            self.replay_btn.scale = 0.9
            self.replay_btn.opacity = 0.0
            self.replay_btn.update()
            await asyncio.sleep(0.3)
            self.actions_row.visible = False
            self.actions_row.update()
            self._build_page()
        self.page.run_task(_anim)

    def on_option_click_value_button(self, value: int, btn: ft.Container):
        if self._locked:
            return
        self._locked = True
        for b in self.option_buttons:
            b.on_click = None

        is_correct = (value == self.answer)
        round_seconds = perf_counter() - self.start_time

        threading.Thread(target=self._send_round_result, args=(is_correct, round_seconds), daemon=True).start()

        btn.scale = 1.1
        btn.bgcolor = "#34D399" if is_correct else "#F87171"
        btn.border = ft.border.all(0, ft.Colors.TRANSPARENT)
        btn.update()

        async def _transition():
            await asyncio.sleep(2)
            self.options_row.opacity = 0.0
            self.options_row.update()
            await asyncio.sleep(0.25)
            self.options_row.visible = False
            self.options_row.update()
            self.actions_row.visible = True
            self.actions_row.update()
            await asyncio.sleep(0.05)
            if is_correct:
                self.finish_btn.visible = True
                self.finish_btn.disabled = False
                self.finish_btn.opacity = 1.0
                self.finish_btn.scale = 1.0
                self.finish_btn.update()
                await asyncio.sleep(0.22)
                self.replay_btn.visible = True
                self.replay_btn.disabled = False
                self.replay_btn.opacity = 1.0
                self.replay_btn.scale = 1.0
                self.replay_btn.update()
            else:
                self.finish_btn.visible = False
                self.finish_btn.disabled = True
                self.finish_btn.opacity = 0.0
                self.finish_btn.scale = 0.8
                self.finish_btn.update()
                self.replay_btn.visible = True
                self.replay_btn.disabled = False
                self.replay_btn.opacity = 0.0
                self.replay_btn.scale = 0.85
                self.replay_btn.update()
                await asyncio.sleep(0.05)
                self.replay_btn.opacity = 1.0
                self.replay_btn.scale = 1.2
                self.replay_btn.update()
        self.page.run_task(_transition)

    def _send_round_result(self, is_correct: bool, seconds: float):
        try:
            user_id = self.page.client_storage.get("user_id")
        except:
            user_id = None

        try:
            add_action = self.app.utils.get("add_action")
        except:
            add_action = None

        try:
            if user_id and callable(add_action):
                payload = ("how_much", 1 if is_correct else 0, round(seconds, 1))
                add_action(user_id, payload)
        except Exception as e:
            print(f"[DEBUG] how_much send error: {e}")
