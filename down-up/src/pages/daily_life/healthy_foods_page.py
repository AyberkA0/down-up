import flet as ft
import time
import asyncio
from random import randint, sample, shuffle

ASSET_DIR = "modules/healthy-foods"

class DraggableLerpControl(ft.Container):
    _instances: list["DraggableLerpControl"] = []
    _last_update = 0.0

    def __init__(
        self,
        page: ft.Page,
        child: ft.Control,
        *,
        width: int,
        height: int,
        bottom_reserved: int = 0,
        lerp_speed: float = 0.10,
        start_left: float = 0.0,
        start_top: float = 0.0,
    ):
        super().__init__(content=None, width=width, height=height)
        self.page = page
        self._w = int(width)
        self._h = int(height)
        self.left = float(start_left)
        self.top = float(start_top)
        self._bottom_reserved = int(max(0, bottom_reserved))
        self._lerp_speed = float(lerp_speed)

        self._mouse_x = float(start_left)
        self._mouse_y = float(start_top)
        self._paused = False

        self.opacity = 1.0
        self.scale = 1.0
        self.animate_opacity = ft.Animation(250, curve="easeOut")
        self.animate_scale = ft.Animation(250, curve="easeOut")

        self._inner = child
        self.on_release = None

        self.default_x = float(start_left)
        self.default_y = float(start_top)

        self.content = ft.GestureDetector(
            content=self._inner,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
        )

        self._vx = 0.0
        self._vy = 0.0
        self._accel = 60.0
        self._damping = 15.0

        DraggableLerpControl._instances.append(self)

    def set_position(self, x: float, y: float, sync_target: bool = True):
        self.left = float(x)
        self.top = float(y)
        if sync_target:
            self._mouse_x = float(x)
            self._mouse_y = float(y)
        self._vx = 0.0
        self._vy = 0.0
        try:
            self.update()
        except:
            pass

    def set_default(self, x: float, y: float):
        self.default_x = float(x)
        self.default_y = float(y)

    def return_to_default(self):
        self._vx = 0.0
        self._vy = 0.0
        self._mouse_x = self.default_x
        self._mouse_y = self.default_y

    def pause_lerp(self, paused: bool):
        self._paused = bool(paused)

    def _bounds(self):
        max_x = max(0.0, float((self.page.width or 0) - self._w))
        max_y = max(0.0, float((self.page.height or 0) - self._h - self._bottom_reserved))
        return max_x, max_y

    def _on_pan_update(self, e):
        if self.page.views[-1].kid_image.src != f"{ASSET_DIR}/eat.png":
            self.page.views[-1].kid_image.src = f"{ASSET_DIR}/eat.png"
            self.page.views[-1].kid_image.update()

        self._mouse_x += e.delta_x
        self._mouse_y += e.delta_y
        max_x, max_y = self._bounds()
        self._mouse_x = min(max(0.0, self._mouse_x), max_x)
        self._mouse_y = min(max(0.0, self._mouse_y), max_y)

    def _on_pan_end(self, e):
        try:
            self.page.views[-1].kid_image.src = f"{ASSET_DIR}/idle.png"
            self.page.views[-1].kid_image.update()
            if callable(self.on_release):
                self.on_release(self)
        except:
            pass

    @classmethod
    def global_tick(cls, dt: float):
        now = time.perf_counter()
        if now - cls._last_update < 1 / 30:
            return
        cls._last_update = now

        for inst in list(cls._instances):
            try:
                if inst._paused:
                    continue
                dx = inst._mouse_x - inst.left
                dy = inst._mouse_y - inst.top
                ax = inst._accel * dx - inst._damping * inst._vx
                ay = inst._accel * dy - inst._damping * inst._vy
                inst._vx += ax * dt
                inst._vy += ay * dt
                inst.left += inst._vx * dt
                inst.top += inst._vy * dt
                bx, by = inst._bounds()
                inst.left = min(max(0.0, inst.left), bx)
                inst.top = min(max(0.0, inst.top), by)
                inst.update()
            except:
                pass


class ScatterBoard(ft.Stack):
    def __init__(self, p, width: int, height: int, item_size: int = 60, margin: int = 10, host_stack: ft.Stack | None = None, origin_x: int = 0, origin_y: int = 0):
        super().__init__(expand=True)
        self.p = p
        self.width = width
        self.height = height
        self.item_size = item_size
        self.margin = margin
        self.items: list[ft.Control] = []
        self.host_stack = host_stack
        self.origin_x = origin_x
        self.origin_y = origin_y

    def add_item(self, item: ft.Control):
        x, y = self._random_position(self._current_positions())
        ax = self.origin_x + x
        ay = self.origin_y + y
        if hasattr(item, "set_position"):
            item.set_position(ax, ay, sync_target=True)
        else:
            item.left = ax
            item.top = ay
        if hasattr(item, "set_default"):
            item.set_default(ax, ay)
        if isinstance(item, ft.Container):
            item.animate_position = ft.Animation(300, curve="easeOut")
        self.items.append(item)
        if self.host_stack is not None:
            self.host_stack.controls.append(item)
        else:
            self.controls.append(item)

    def _current_positions(self):
        return [(getattr(c, "left", 0) - self.origin_x, getattr(c, "top", 0) - self.origin_y) for c in self.items]

    def _random_position(self, existing_positions):
        max_x = self.width - self.item_size
        max_y = self.height - self.item_size

        for _ in range(50):
            x = randint(0, max_x)
            y = randint(0, max_y)
            overlap = False
            for ex, ey in existing_positions:
                if not (
                    x + self.item_size + self.margin < ex or
                    ex + self.item_size + self.margin < x or
                    y + self.item_size + self.margin < ey or
                    ey + self.item_size + self.margin < y
                ):
                    overlap = True
                    break
            if not overlap:
                return x, y

        if self.items:
            removed = self.items.pop(randint(0, len(self.items) - 1))
            if getattr(removed, "is_good", False):
                self.p.remaining_good -= 1
            if self.host_stack and removed in self.host_stack.controls:
                self.host_stack.controls.remove(removed)
            elif removed in self.controls:
                self.controls.remove(removed)

        return randint(0, max_x), randint(0, max_y)


class HealthyFoodsPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/healthy_foods")
        self.app = page.app
        self.page = page
        self.bgcolor = "#FFE5EB"
        self.padding = 0

        self.start_time = time.perf_counter()
        self.bad_attempts = 0
        self.remaining_good = 0
        self.elapsed = 0

        total_w = self.page.window.width
        total_h = self.page.window.height
        top_area_height = int((total_h - self.padding * 2) * 0.35)
        shuffle_row_height = 60
        board_height = max(120, top_area_height - shuffle_row_height)
        board_width = max(240, int(total_w - self.padding * 2))

        overlay = ft.Stack(expand=True, clip_behavior=ft.ClipBehavior.NONE)

        foods_data = {}
        for i in range(1, 27):
            foods_data[f"{ASSET_DIR}/good/good {i}.png"] = True
        for i in range(1, 18):
            foods_data[f"{ASSET_DIR}/bad/bad {i}.png"] = False

        food_items = list(foods_data.items())
        shuffle(food_items)
        foods_dict = dict(sample(food_items, k=8))

        self.remaining_good = sum(1 for v in foods_dict.values() if v)

        origin_x = int((total_w - board_width) / 2)
        origin_y = 0
        board = ScatterBoard(
            p=self,
            width=board_width,
            height=board_height,
            item_size=60,
            margin=15,
            host_stack=overlay,
            origin_x=origin_x,
            origin_y=origin_y,
        )

        for k in foods_dict.keys():
            board_item = DraggableLerpControl(
                page=page,
                child=ft.Container(
                    border_radius=8,
                    content=ft.Image(src=k),
                    width=50,
                    height=50
                ),
                width=board.item_size,
                height=board.item_size,
                bottom_reserved=0,
                lerp_speed=0.9,
            )
            board_item.is_good = foods_dict[k]
            board_item.on_release = lambda it, threshold=(top_area_height + 10): self.handle_drop(it, threshold)
            board.add_item(board_item)

        top_half = ft.Container(
            padding=20,
            height=top_area_height,
            content=ft.Column([ft.Container(width=board_width, height=board_height, alignment=ft.alignment.center)]),
        )

        self.kid_image = ft.Image(src=f"{ASSET_DIR}/idle.png", fit=ft.ImageFit.FIT_WIDTH, expand=True)
        bottom_half = ft.Container(expand=True, content=self.kid_image, height=shuffle_row_height, alignment=ft.alignment.center)

        self.finish_btn = ft.FilledButton(
            text="Bitir",
            style=self.app.button_style,
            height=50,
            width=self.page.width // 1.5 if self.page.width else 320,
            animate_opacity=300,
            animate_scale=300,
            scale=0.8,
            opacity=0,
            disabled=True,
            visible=True,
            on_click=self.on_complete_click,
        )

        self.actions_row = ft.Row(
            controls=[self.finish_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            visible=True,
        )

        self.complete_bar = ft.Container(
            height=85,
            bgcolor="#EAD5DA",
            content=ft.Stack(alignment=ft.alignment.center, controls=[self.actions_row]),
            border=ft.Border(ft.BorderSide(width=3, color="#DBC6CB"), None, None, None),
            visible=True,
            animate_opacity=300,
            animate_size=300,
        )

        column = ft.Column([top_half, bottom_half, self.complete_bar], expand=True, spacing=0)
        root = ft.Stack([column, overlay], expand=True)
        self.controls = [root]

        async def motion_loop():
            while True:
                DraggableLerpControl.global_tick(1 / 30)
                await asyncio.sleep(1 / 30)

        page.run_task(motion_loop)

    def on_complete_click(self, e):
        self.page.run_thread(self.set_data)
        self.page.go("/daily_life_index")

    async def _delayed_remove(self, item):
        await asyncio.sleep(0.28)
        for container in self.controls:
            if isinstance(container, ft.Stack) and len(container.controls) == 2 and isinstance(container.controls[1], ft.Stack):
                overlay = container.controls[1]
                if item in overlay.controls:
                    overlay.controls.remove(item)
                    overlay.update()

    def handle_drop(self, item: ft.Control, y_threshold_abs: float):
        h = getattr(item, "height", 60)
        if (item.top + h * 0.5) >= y_threshold_abs:
            if getattr(item, "is_good", False):
                item.opacity = 0.0
                item.scale = 0.3
                try:
                    item.update()
                except:
                    pass
                self.remaining_good -= 1
                if self.remaining_good <= 0:
                    self.elapsed = time.perf_counter() - self.start_time
                    self._show_actions()
                self.page.run_task(lambda: self._delayed_remove(item))
            else:
                if hasattr(item, "return_to_default"):
                    item.return_to_default()
                if self.remaining_good > 0:
                    self.bad_attempts += 1

    def _show_actions(self):
        self.complete_bar.visible = True
        self.complete_bar.opacity = 0.0
        self.complete_bar.update()

        async def _anim():
            await asyncio.sleep(0.05)
            self.complete_bar.opacity = 1.0
            self.complete_bar.height = 120
            self.complete_bar.update()
            await asyncio.sleep(0.1)
            self.finish_btn.disabled = False
            self.finish_btn.opacity = 1.0
            self.finish_btn.scale = 1.0
            self.finish_btn.update()

        self.page.run_task(_anim)

    def set_data(self):
        try:
            user_id = self.page.client_storage.get("user_id")
        except Exception as e:
            user_id = None
            print(f"[DEBUG] user_id okunamadı: {e}")

        try:
            add_action = self.app.utils.get("add_action")
            seconds = round(float(time.perf_counter() - self.start_time), 1)
            if user_id and callable(add_action):
                add_action(user_id, ("healthy_foods", self.bad_attempts, seconds))
        except Exception as e:
            print(f"[DEBUG] add_action çağrısı sırasında hata: {e}")
