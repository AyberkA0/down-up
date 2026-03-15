import flet as ft
from flet_flip_card import FlipCard, FlipCardSide
from random import shuffle
from time import sleep, perf_counter  # <- süre ölçümü için eklendi

ASSET_DIR = "modules/memory-cards"

class MemoryCardsPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/memory_cards")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.padding = 0
        self.bgcolor = "#FDCB84"
        self.levels = [(6, 3), (8, 4), (12, 4)]
        self.level_index = 0
        self.SPACING = 8
        self.FLIP_MS = 300
        self.LEVEL_AR = 2
        self.ENTRANCE_MS = 220
        self.ENTRANCE_STAGGER_MS = 40
        self._busy = False

        # süre değişkeni
        self.level_start = 0.0
        self.elapsed = 0.0

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
                        "Kartlara tıkla ve aynı olan kartları ortaya çıkar!",
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
            bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
            border_radius=20,
        )

        self.grid_holder = ft.Container(
            padding=12,
            margin=ft.Margin(0, 10, 0, 0),
            expand=True,
            animate_opacity=300,
            animate_scale=ft.Animation(250),
            opacity=1,
            scale=1,
        )

        self.next_btn = ft.FilledButton(
            text="İleri",
            opacity=0,
            disabled=True,
            style=self.app.button_style,
            height=50,
            width=self.page.width // 1.5 if self.page.width else 320,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            scale=1,
            on_click=self._handle_next,
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

        self.progress_bar_container = ft.Container(
            content=ft.Container(
                bgcolor="#55AFAD",
                height=24,
                width=5,
                border_radius=12,
                animate_size=300,
            ),
            bgcolor="#B4D9D1",
            height=24,
            border_radius=12,
            width=self.page.width,
            alignment=ft.alignment.center_left,
            padding=0,
            scale=0.85,
            opacity=1,
            animate_opacity=300,
        )
        self.progress_fill = self.progress_bar_container.content

        self.buttons_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
            controls=[self.next_btn, self.replay_btn],
        )

        self.bottom_bar = ft.Container(
            height=100,
            bgcolor="#FDEDD4",
            content=ft.Stack(
                alignment=ft.alignment.center,
                controls=[
                    self.progress_bar_container,
                    self.buttons_row,
                ],
            ),
            border=ft.Border(
                ft.BorderSide(width=1, color=ft.Colors.with_opacity(0.7, "#B5B0AB")),
                None,
                None,
                None,
            ),
        )

        self.level_labels = ["Kolay", "Orta", "Zor"]
        self.level_active_colors = ["#5CBAA2", "#FFB43D", "#F87F64"]
        self.level_inactive_colors = ["#5CBAA2", "#FFB43D", "#F87F64"]

        self.level_ctrs = []
        self.level_inners = []

        for i, label in enumerate(self.level_labels):
            inner = ft.Container(
                bgcolor=self.level_inactive_colors[i],
                border_radius=10,
                alignment=ft.alignment.center,
                animate_scale=ft.Animation(150),
                content=ft.Text(label, size=18, color="#0E444D", weight=ft.FontWeight.W_600),
                on_click=lambda e, idx=i: self._on_level_click(idx),
                border=ft.border.all(3, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            )
            outer = ft.Container(
                content=inner,
                aspect_ratio=self.LEVEL_AR,
                border_radius=10,
                expand=True,
            )
            self.level_ctrs.append(outer)
            self.level_inners.append(inner)

        self.level_buttons_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10,
            controls=self.level_ctrs,
        )
        self.level_buttons_wrap = ft.Container(
            content=self.level_buttons_row,
            margin=24,
        )

        background = ft.Container(
            expand=True,
            image=ft.DecorationImage(
                src=f"{ASSET_DIR}/bg.png",
                fit=ft.ImageFit.FIT_WIDTH,
                repeat=ft.ImageRepeat.REPEAT_Y,
            ),
        )
        foreground = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                info_container,
                self.grid_holder,
                self.level_buttons_wrap,
                self.bottom_bar,
            ],
        )
        self.controls = [
            ft.Stack(
                expand=True,
                controls=[background, ft.SafeArea(content=foreground)],
            )
        ]

        self._apply_level(self.level_index)

    def _apply_level(self, idx: int):
        self.level_index = idx
        self.CARD_COUNT, self.COL_COUNT = self.levels[idx]
        self.ROW_COUNT = self.CARD_COUNT // self.COL_COUNT
        self._busy = False
        self.wrong_attempts = 0  # her level başında sıfırla
        self.elapsed = 0.0
        self.level_start = perf_counter()  # süreyi başlat

        self.all_names = ["ant", "bear", "bird", "duck", "fish", "frog", "horse", "monkey", "star", "turtle"]
        shuffle(self.all_names)
        deck = self.all_names[: self.CARD_COUNT // 2] * 2
        shuffle(deck)
        self.deck = deck
        self.open_cards: list[FlipCard] = []
        self.matched_pairs = 0
        self.total_pairs = self.CARD_COUNT // 2
        self.cards: list[FlipCard] = []
        self.card_shells: list[ft.Container] = []

        self.grid_holder.scale = 0.98
        self.grid_holder.opacity = 0
        self.page.update()

        grid = self._build_grid()
        self.grid_holder.content = grid
        self._hide_action_buttons()
        self.progress_bar_container.opacity = 1
        self.progress_fill.width = 5
        self.next_btn.text = "Bitir" if self.level_index == len(self.levels) - 1 else "İleri"
        self._refresh_level_buttons()

        self.grid_holder.scale = 1
        self.grid_holder.opacity = 1
        self.page.update()

        self._stagger_cards_entrance()

    def _handle_next(self, _):
        if self.level_index < len(self.levels) - 1:
            self._on_level_click(self.level_index + 1)
        else:
            self.page.go("/memory_index")

    def _handle_replay(self, _):
        self._apply_level(self.level_index)

    def _show_action_buttons(self):
        self.next_btn.disabled = False
        self.replay_btn.disabled = False
        self.next_btn.opacity = 1
        self.replay_btn.opacity = 1
        self.next_btn.scale = 1
        self.replay_btn.scale = 1

    def _hide_action_buttons(self):
        self.next_btn.disabled = True
        self.replay_btn.disabled = True
        self.next_btn.opacity = 0
        self.replay_btn.opacity = 0
        self.next_btn.scale = 0.8
        self.replay_btn.scale = 0.8

    def _update_progress(self):
        if self.total_pairs <= 0:
            return
        ratio = self.matched_pairs / self.total_pairs
        bar_w = self.progress_bar_container.width or self.page.width or 320
        self.progress_fill.width = max(5, int(bar_w * ratio))

    def _on_level_click(self, idx: int):
        if idx == self.level_index and self.grid_holder.content is not None:
            self.level_inners[idx].scale = 1.06
            self.page.update()
            sleep(0.08)
            self.level_inners[idx].scale = 1.0
            self.page.update()
            return
        for i, inn in enumerate(self.level_inners):
            inn.scale = 0.96 if i != idx else 1.08
        self.page.update()
        sleep(0.1)
        for i, inn in enumerate(self.level_inners):
            inn.scale = 1.0
        self.page.update()
        self._apply_level(idx)

    def _refresh_level_buttons(self):
        for i, inner in enumerate(self.level_inners):
            active = i == self.level_index
            inner.bgcolor = self.level_active_colors[i] if active else self.level_inactive_colors[i]
            inner.scale = 1.0 if active else 0.98
            inner.border = ft.border.all(3, ft.Colors.with_opacity(0.5, ft.Colors.WHITE)) if active else ft.border.all(3, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))

    def _make_card(self, name: str) -> ft.Control:
        back = ft.Container(
            expand=True,
            aspect_ratio=0.8,
            image=ft.DecorationImage(src=f"{ASSET_DIR}/card.png", fit=ft.ImageFit.COVER),
            border=ft.border.all(5, ft.Colors.WHITE),
            border_radius=12,
            alignment=ft.alignment.center,
        )
        front = ft.Container(
            expand=True,
            aspect_ratio=0.8,
            border=ft.border.all(5, ft.Colors.WHITE),
            border_radius=12,
            alignment=ft.alignment.center,
            padding=4,
            content=ft.Image(src=f"{ASSET_DIR}/{name}.png"),
            bgcolor="#30AA8F",
        )
        card = FlipCard(
            front=front,
            back=back,
            initial_side=FlipCardSide.BACK,
            duration=self.FLIP_MS,
        )
        card.data = {"name": name, "matched": False, "open": False}
        def on_face_tap(_):
            self._on_card_tap(card)
        back.on_click = on_face_tap
        shell = ft.Container(
            card,
            expand=True,
            opacity=0,
            scale=0.9,
            animate_opacity=self.ENTRANCE_MS,
            animate_scale=ft.Animation(self.ENTRANCE_MS),
        )
        self.cards.append(card)
        self.card_shells.append(shell)
        return shell

    def _build_grid(self) -> ft.Container:
        cards_controls = [self._make_card(name) for name in self.deck]
        rows = []
        for r in range(self.ROW_COUNT):
            row_cards = cards_controls[r * self.COL_COUNT: r * self.COL_COUNT + self.COL_COUNT]
            rows.append(
                ft.Row(
                    controls=row_cards,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=self.SPACING,
                )
            )
        return ft.Container(
            padding=16,
            content=ft.Column(
                controls=rows,
                spacing=self.SPACING,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )

    def _stagger_cards_entrance(self):
        for i, shell in enumerate(self.card_shells):
            shell.opacity = 1
            shell.scale = 1
            self.page.update()
            sleep(self.ENTRANCE_STAGGER_MS / 1000)

    def _open_card(self, card: FlipCard):
        if not card.data["open"]:
            card.show_front()
            card.data["open"] = True
            self.open_cards.append(card)

    def _close_card(self, card: FlipCard):
        if card.data["open"] and not card.data["matched"]:
            card.show_back()
            card.data["open"] = False
            if card in self.open_cards:
                self.open_cards.remove(card)

    def _match_cards(self, a: FlipCard, b: FlipCard):
        a.data["matched"] = True
        b.data["matched"] = True
        if a in self.open_cards:
            self.open_cards.remove(a)
        if b in self.open_cards:
            self.open_cards.remove(b)
        self.matched_pairs += 1
        self._update_progress()
        if self.matched_pairs >= self.total_pairs:
            self.finish()

    def _on_card_tap(self, card: FlipCard):
        if self._busy:
            return
        self._busy = True
        try:
            if card.data["matched"]:
                return
            if len(self.open_cards) == 2:
                a, b = self.open_cards[0], self.open_cards[1]
                if a.data["name"] != b.data["name"]:
                    self._close_card(a)
                    self._close_card(b)
                    self.page.update()
                    self.wrong_attempts += 1
                    return
            if card.data["open"]:
                return
            self._open_card(card)
            if len(self.open_cards) == 2:
                a, b = self.open_cards[0], self.open_cards[1]
                if a is b:
                    return
                if a.data["name"] == b.data["name"]:
                    self._match_cards(a, b)
            sleep(self.FLIP_MS / 1000)
            self.page.update()
        finally:
            self._busy = False

    def finish(self):
        self.elapsed = perf_counter() - self.level_start

        self.progress_bar_container.opacity = 0
        self._show_action_buttons()
        self.page.update()

        self.page.run_thread(self.set_data)

    def set_data(self):
        try:
            user_id = self.page.client_storage.get("user_id")
        except:
            user_id = None
        try:
            add_action = self.app.utils.get("add_action")
            if user_id and callable(add_action):
                payload = ("memory_cards", self.wrong_attempts, round(self.elapsed, 1), self.level_labels[self.level_index])
                add_action(user_id, payload)
        except Exception as e:
            print(f"[DEBUG] add_action error: {e}")
