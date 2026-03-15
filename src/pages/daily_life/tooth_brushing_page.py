import flet as ft
import threading
import time
from random import randint

ASSET_DIR = "modules/tooth-brushing"

class ToothBrushingPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/tooth_brushing")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.padding = 0
        self.bgcolor = "#D0EADF"

        # istatistik için sayaçlar
        self.start_time = time.perf_counter()
        self.elapsed = 0.0
        self.bad_attempts = 0  # bu oyunda yok, ama payload sabit kalsın diye eklendi

        self.brush_left = 0
        self.brush_top = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.current_angle = 0
        self.target_angle = 0

        self.lerp_speed = 0.1
        self.rotate_speed = 0.04

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
                        "Diş fırçasını ekrana sürükle ve dişlerini fırçala!",
                        max_lines=2,
                        expand=True,
                        size=18,
                        color="#0E444D",
                    )
                ]
            ),
            margin=ft.Margin(0, 30, 0, 0),
            scale=0.9,
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
            border_radius=20,
        )

        self.brush_img = ft.Image(
            src=f"{ASSET_DIR}/brush.png",
            width=100,
            height=100,
            rotate=self.current_angle
        )

        self.brush_detector = ft.GestureDetector(
            content=self.brush_img,
            on_pan_update=self.on_brush_move
        )

        self.brush_container = ft.Container(
            content=self.brush_detector,
            left=self.brush_left,
            top=self.brush_top,
            width=200,
            height=100,
        )

        self.boy_clean = ft.Container(
            content=ft.Image(src=f"{ASSET_DIR}/boy.png"),
            alignment=ft.alignment.center,
            expand=True,
            padding=0,
        )

        self.boy_dirty = ft.Container(
            content=ft.Image(src=f"{ASSET_DIR}/boy-dirty.png"),
            alignment=ft.alignment.center,
            expand=True,
            padding=0,
        )

        self.bg = ft.Image(src=f"{ASSET_DIR}/bg.png")
        self.bottom = ft.Image(src=f"{ASSET_DIR}/bottom.png")

        self.progress_bar_container = ft.Container(
            content=ft.Container(
                bgcolor="#55AFAD",
                height=24,
                width=5,
                border_radius=12,
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

        self.next_btn = ft.FilledButton(
            text="İleri",
            opacity=0,
            disabled=True,
            style=self.app.button_style,
            height=50,
            width=self.page.width // 1.5,
            animate_opacity=300,
            animate_scale=ft.Animation(300),
            scale=0.8,
            # burada set_data + yönlendirme bağlandı
            on_click=self.on_next_click,
        )

        self.bubble_layer = ft.Stack([])

        self.canvas = ft.Stack(
            controls=[
                self.boy_clean,
                self.boy_dirty,
                self.bubble_layer,
                self.brush_container,
            ],
            expand=True
        )

        self.controls = [
            ft.Stack(
                controls=[
                    self.bg,
                    info_container,
                ]
            ),
            ft.Stack(
                controls=[
                    ft.Container(
                        content=self.canvas,
                        left=0,
                        top=0,
                        right=0,
                        bottom=130,
                    ),
                    ft.Container(
                        content=ft.Stack(
                            [
                                self.bottom,
                                ft.Container(
                                    content=self.progress_bar_container,
                                    expand=True,
                                    alignment=ft.alignment.center,
                                    bottom=50,
                                    left=0,
                                    right=0
                                ),
                                ft.Container(
                                    content=self.next_btn,
                                    expand=True,
                                    alignment=ft.alignment.center,
                                    bottom=35,
                                    left=0,
                                    right=0
                                ),
                            ]
                        ),
                        left=0,
                        right=0,
                        bottom=0,
                        alignment=ft.alignment.center,
                        expand=True
                    ),
                ],
                expand=True
            )
        ]

        threading.Thread(target=self.rotate_brush_loop, daemon=True).start()
        threading.Thread(target=self.lerp_loop, daemon=True).start()

    def update_progress_bar(self):
        clean_ratio = 1 - self.boy_dirty.opacity
        self.progress_fill.width = self.progress_bar_container.width * clean_ratio
        self.progress_fill.update()

        if clean_ratio >= 1:
            self.progress_bar_container.opacity = 0
            self.progress_bar_container.update()

            self.next_btn.disabled = False
            self.next_btn.opacity = 1
            self.next_btn.scale = 1
            self.next_btn.update()

    def on_brush_move(self, e: ft.DragUpdateEvent):
        self.mouse_x += e.delta_x
        self.mouse_y += e.delta_y

        BOTTOM_HEIGHT = 420
        canvas_right = self.page.width - self.brush_container.width
        canvas_bottom = self.page.height - self.brush_container.height - BOTTOM_HEIGHT

        self.mouse_x = min(max(0, self.mouse_x), canvas_right)
        self.mouse_y = min(max(0, self.mouse_y), canvas_bottom)

        self.target_angle = max(-15, min(15, e.delta_x * 0.4))

        if randint(0, 15) == 12:
            bubble = ft.Image(
                src=f"{ASSET_DIR}/bubble.png",
                width=30,
                left=self.brush_left + self.brush_container.width - self.brush_container.width // 5 + randint(-25, 25),
                top=self.brush_top + self.brush_container.height // 2 + randint(-15, 15),
                opacity=1,
            )
            self.bubble_layer.controls.append(bubble)
            self.page.update()
            threading.Thread(target=self.fade_and_remove, args=(bubble,), daemon=True).start()

            if self.boy_dirty.opacity > 0:
                self.boy_dirty.opacity = max(0, self.boy_dirty.opacity - 0.01)
                self.boy_dirty.update()
                self.update_progress_bar()

    def rotate_brush_loop(self):
        while True:
            self.current_angle += (self.target_angle - self.current_angle) * self.rotate_speed
            self.brush_img.rotate = self.current_angle
            try:
                self.brush_img.update()
            except:
                pass
            time.sleep(1 / 90)

    def lerp_loop(self):
        while True:
            self.brush_left = self.brush_left + (self.mouse_x - self.brush_left) * self.lerp_speed
            self.brush_top = self.brush_top + (self.mouse_y - self.brush_top) * self.lerp_speed

            self.brush_container.left = self.brush_left
            self.brush_container.top = self.brush_top

            try:
                self.brush_container.update()
            except:
                pass

            time.sleep(1 / 90)

    def fade_and_remove(self, bubble: ft.Image):
        step = 24
        for _ in range(step):
            if bubble in self.bubble_layer.controls:
                try:
                    bubble.opacity = max(0, bubble.opacity - 1 / step)
                    bubble.update()
                    time.sleep(1 / step)
                except:
                    pass

        if bubble in self.bubble_layer.controls:
            try:
                self.bubble_layer.controls.remove(bubble)
                self.page.update()
            except:
                pass

    # --- yeni eklenenler ---
    def on_next_click(self, e):
        self.page.run_thread(self.set_data)
        self.page.go("/daily_life_index")

    def set_data(self):
        # tekrar gönderimi engelle
        if getattr(self, "_stats_sent", False):
            return
        self._stats_sent = True

        duration = time.perf_counter() - self.start_time

        try:
            user_id = self.page.client_storage.get("user_id")
        except Exception as e:
            user_id = None
            print(f"[DEBUG] user_id okunamadı: {e}")

        try:
            add_action = None
            if hasattr(self.app, "utils") and isinstance(self.app.utils, dict):
                add_action = self.app.utils.get("add_action")

            if not user_id:
                print("[DEBUG] user_id yok, action gönderilmeyecek")
                return
            if not callable(add_action):
                print("[DEBUG] add_action util’i bulunamadı veya çağrılabilir değil")
                return

            payload = ("tooth_brushing", -1, round(duration, 1))
            status = add_action(user_id, payload)
            print(f"[DEBUG] add_action status={status}")
        except Exception as e:
            print(f"[DEBUG] set_data sırasında hata: {e}")
