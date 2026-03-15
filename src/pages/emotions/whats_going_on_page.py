import flet as ft
from random import choice, sample, shuffle

ASSET_DIR = "modules/whats-going-on"


class WhatsGoingOnPage(ft.View):
    HILIGHT_BG = "#0E444D"
    HILIGHT_FG = "white"

    def __init__(self, page: ft.Page):
        super().__init__(route="/whats_going_on")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#FAF5EF"
        self.padding = 20

        self.levels = {
            "1.png": ["Üzgün", "Yağmurda ıslandı", "Şemsiyemi paylaşırım"],
            "2.png": ["Üzgün", "Balonu uçtu", "Yakalamasına yardım ederim"],
            "3.png": ["Neşeli", "Pastasını üfledi", "Alkışlarım"],
            "4.png": ["Üzgün", "Dondurması düştü", "Dondurma veririm"],
            "6.png": ["Neşeli", "Ödül aldı", "Tebrik ederim"],
            "7.png": ["Üzgün", "Oyuncağı kırıldı", "Oyuncaklarımı paylaşırım"],
            "8.png": ["Üzgün", "Yere düştü", "Yardım çağırırım"],
        }

        self.current_img, self.correct_answers = self._pick_level()

        self.emotion_value = None
        self.event_value = None
        self.reaction_value = None

        self.app.play_sound(f"{ASSET_DIR}/info-audio.mp3")

        self._build_ui()

    def _default_style(self):
        return ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            text_style=ft.TextStyle(size=14, overflow="ellipsis"),
        )

    def _build_ui(self):
        subtitle = ft.Text("Resme iyi bak, sonra tahmin et:", size=18, color="#0E444D")

        self.image_control = ft.Image(src=f"{ASSET_DIR}/{self.current_img}", fit=ft.ImageFit.FIT_WIDTH)

        emotion_options = self._make_options(
            self.correct_answers[0],
            ["Üzgün", "Neşeli", "Şaşkın", "Öfkeli", "Korkmuş", "Tiksinmiş"],
            3,
        )
        self.emotion_row = self._make_row(emotion_options, "emotion")

        event_options = self._make_options(self.correct_answers[1], [v[1] for v in self.levels.values()], 4)
        half = len(event_options) // 2
        self.event_rows = [
            self._make_row(event_options[:half], "event"),
            self._make_row(event_options[half:], "event"),
        ]

        reaction_options = self._make_options(self.correct_answers[2], [v[2] for v in self.levels.values()], 2)
        self.reaction_row = self._make_row(reaction_options, "reaction")

        self.result_icon = ft.Icon(ft.Icons.INFO, size=20, color="white")
        self.result_text = ft.Text("", color="white", size=16, weight=ft.FontWeight.W_600, expand=True)
        self.result_bar = ft.Container(
            visible=False,
            bgcolor="#2E7D32",
            padding=12,
            border_radius=12,
            content=ft.Row(
                [
                    self.result_icon,
                    self.result_text,
                    ft.IconButton(icon=ft.Icons.CLOSE, icon_color="white", on_click=lambda e: self._hide_result()),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self.next_btn = ft.ElevatedButton("Kontrol Et", on_click=self.check_answers, bgcolor="#0E444D", color="white", style=self.app.button_style)
        retry_btn = ft.OutlinedButton("Tekrar Oyna", on_click=self.retry, style=self.app.button_style)

        self.controls = [
            subtitle,
            ft.Container(content=self.image_control, alignment=ft.alignment.center, padding=0, bgcolor="#CEEFFF", border_radius=12),
            ft.Text("Duygu seç:", weight=ft.FontWeight.BOLD),
            self.emotion_row,
            ft.Text("Olay seç:", weight=ft.FontWeight.BOLD),
            *self.event_rows,
            ft.Text("Tepki seç:", weight=ft.FontWeight.BOLD),
            self.reaction_row,
            self.result_bar,
            ft.Row([self.next_btn, retry_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        ]

    def _pick_level(self):
        img, answers = choice(list(self.levels.items()))
        return img, answers

    def _make_options(self, correct, pool, count):
        seen = set()
        uniq = []
        for p in pool:
            if p not in seen:
                seen.add(p)
                uniq.append(p)
        others = [o for o in uniq if o != correct]
        k = min(count - 1, len(others))
        opts = [correct] + sample(others, k)
        while len(opts) < count and others:
            cand = choice(others)
            if cand not in opts:
                opts.append(cand)
        shuffle(opts)
        return opts

    def _buttons_from_options(self, options, group):
        btns = []
        for opt in options:
            btns.append(
                ft.ElevatedButton(
                    text=opt,
                    data={"group": group, "value": opt},
                    expand=1,
                    on_click=self._on_select,
                    style=self._default_style(),
                )
            )
        return btns

    def _make_row(self, options, group):
        return ft.Row(self._buttons_from_options(options, group), spacing=10)

    def _group_rows(self, group: str):
        return {
            "emotion": [self.emotion_row],
            "event": self.event_rows,
            "reaction": [self.reaction_row],
        }[group]

    def _on_select(self, e: ft.ControlEvent):
        group = e.control.data["group"]
        value = e.control.data["value"]
        if getattr(self, f"{group}_value") is not None:
            return
        setattr(self, f"{group}_value", value)

        rows = self._group_rows(group)
        for row in rows:
            for btn in row.controls:
                if btn.text == value:
                    btn.style = ft.ButtonStyle(
                        bgcolor=self.HILIGHT_BG,
                        color=self.HILIGHT_FG,
                        shape=ft.RoundedRectangleBorder(radius=12),
                        text_style=ft.TextStyle(size=14, overflow="ellipsis"),
                    )
                btn.disabled = True
                btn.update()

        self._hide_result()
        self.page.update()

    def check_answers(self, _):
        if self.emotion_value is None or self.event_value is None or self.reaction_value is None:
            self._show_result("Lütfen üç seçimi de yap.", "#F9A825", ft.Icons.WARNING)
            return

        if [self.emotion_value, self.event_value, self.reaction_value] == self.correct_answers:
            self._show_result("Doğru! Yeni görsel yüklendi. 🎉", "#2E7D32", ft.Icons.CHECK_CIRCLE)
            self.current_img, self.correct_answers = self._pick_level()
            self._rebuild_for_current_level()
        else:
            self._show_result("Yanlış! Tekrar dene.", "#C62828", ft.Icons.CANCEL)

    def retry(self, _):
        self._rebuild_for_current_level()

    def _rebuild_for_current_level(self):
        self.image_control.src = f"{ASSET_DIR}/{self.current_img}"
        self.image_control.update()

        self.emotion_value = self.event_value = self.reaction_value = None

        em_opts = self._make_options(
            self.correct_answers[0],
            ["Üzgün", "Neşeli", "Şaşkın", "Öfkeli", "Korkmuş", "Tiksinmiş"],
            3,
        )
        self.emotion_row.controls.clear()
        self.emotion_row.controls.extend(self._buttons_from_options(em_opts, "emotion"))
        for b in self.emotion_row.controls:
            b.disabled = False
            b.style = self._default_style()
        self.emotion_row.update()

        ev_opts = self._make_options(self.correct_answers[1], [v[1] for v in self.levels.values()], 4)
        half = len(ev_opts) // 2
        left, right = ev_opts[:half], ev_opts[half:]

        self.event_rows[0].controls.clear()
        self.event_rows[0].controls.extend(self._buttons_from_options(left, "event"))
        for b in self.event_rows[0].controls:
            b.disabled = False
            b.style = self._default_style()
        self.event_rows[0].update()

        self.event_rows[1].controls.clear()
        self.event_rows[1].controls.extend(self._buttons_from_options(right, "event"))
        for b in self.event_rows[1].controls:
            b.disabled = False
            b.style = self._default_style()
        self.event_rows[1].update()

        re_opts = self._make_options(self.correct_answers[2], [v[2] for v in self.levels.values()], 2)
        self.reaction_row.controls.clear()
        self.reaction_row.controls.extend(self._buttons_from_options(re_opts, "reaction"))
        for b in self.reaction_row.controls:
            b.disabled = False
            b.style = self._default_style()
        self.reaction_row.update()

        self._hide_result()
        self.page.update()

    def _show_result(self, text: str, color: str, icon: str):
        self.result_text.value = text
        self.result_icon.name = icon
        self.result_bar.bgcolor = color
        self.result_bar.visible = True
        self.result_text.update()
        self.result_icon.update()
        self.result_bar.update()
        self.page.update()

    def _hide_result(self):
        if self.result_bar.visible:
            self.result_bar.visible = False
            self.result_bar.update()
            self.page.update()
