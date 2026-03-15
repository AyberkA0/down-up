import json
import random
import uuid
import flet as ft

# Unicode sembollerini kullanıyoruz (▲ ■ ▬ ●)
SHAPE_CHARS = {
    "triangle": "▲",
    "square": "■",
    "rectangle": "▬",
    "circle": "●",
}

PALETTE = ["#FF5A5F", "#2ECC71", "#3498DB", "#9B59B6", "#E67E22", "#16A085"]

class NameShapesPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/name_shapes")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#FAF5EF"
        self.padding = 16

        # Oyun durumu
        self.game_over = False
        self.total_items = 0
        self.placed_correct = 0
        self.nodes_by_id: dict[str, ft.Control] = {}

        # Başlık & reset
        self.title = ft.Text("Şekilleri doğru kutulara sürükle", size=20, color="#0E444D")
        self.reset_btn = ft.TextButton("Yeniden başlat", on_click=lambda e: self._setup_game())

        # Üst alan (rastgele saçılmış şekiller)
        self.play_area_height = 320
        self.play_area = ft.Container(
            height=self.play_area_height,
            expand=True,
            bgcolor="#FFF",
            border_radius=16,
            padding=8,
            border=ft.border.all(2, "#EDE6DD"),
            content=ft.Stack(expand=True),
        )

        # Alt hedef kutuları
        self.targets_row = self._build_targets_row()

        # Sayfa düzeni
        self.controls = [
            ft.Row([self.title, self.reset_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=10),
            self.play_area,
            ft.Container(height=12),
            self.targets_row,
        ]

        self._setup_game()

    # ---------------- OYUN KURULUMU ----------------
    def _setup_game(self):
        self.game_over = False
        self.placed_correct = 0
        self.nodes_by_id.clear()

        counts = {"triangle": 3, "square": 3, "rectangle": 3, "circle": 3}
        items = [shape for shape, n in counts.items() for _ in range(n)]
        random.shuffle(items)
        self.total_items = len(items)

        stack_controls: list[ft.Control] = []
        # üst alan genişliği tahmini; sol sınır için küçük bir tampon
        area_w = (self.page.width or 640) - 64

        for shape in items:
            node_id = str(uuid.uuid4())
            draggable = self._make_draggable(shape, node_id)

            left = max(0, random.randint(0, int(area_w)))
            top = max(0, random.randint(0, self.play_area_height - 64))

            # 🔑 Stack içinde konumlandırma: Container'a left/top veriyoruz
            stack_controls.append(
                ft.Container(
                    content=draggable,
                    left=left,
                    top=top,
                    width=64,
                    height=64,
                    alignment=ft.alignment.center,
                )
            )
            self.nodes_by_id[node_id] = draggable

        self.play_area.content = ft.Stack(controls=stack_controls, expand=True)
        self.page.update()

    # ---------------- DRAGGABLE / TARGET ----------------
    def _make_shape_view(self, shape: str, size: int = 44) -> ft.Container:
        return ft.Container(
            content=ft.Text(SHAPE_CHARS[shape], size=size, color=random.choice(PALETTE)),
            alignment=ft.alignment.center,
            width=64,
            height=64,
        )

    def _make_draggable(self, shape: str, node_id: str) -> ft.Draggable:
        data = {"type": shape, "id": node_id}
        return ft.Draggable(
            group="shapes",
            data=json.dumps(data),
            content=self._make_shape_view(shape),
            content_when_dragging=self._make_shape_view(shape, size=44),
            content_feedback=self._make_shape_view(shape, size=48),
        )

    def _build_targets_row(self) -> ft.Row:
        def bin_box(label: str, accept_type: str, emoji: str) -> ft.Container:
            def on_accept(e):
                if self.game_over:
                    return
                try:
                    payload = json.loads(e.data) if isinstance(e.data, str) else e.data
                except Exception:
                    payload = {"type": None, "id": None}

                dropped_type = payload.get("type")
                node_id = payload.get("id")

                if dropped_type == accept_type:
                    node = self.nodes_by_id.get(node_id)
                    if node and node.visible is not False:
                        node.visible = False
                        self.placed_correct += 1
                        print(f"Doğru! {self.placed_correct}/{self.total_items}")
                        if self.placed_correct == self.total_items:
                            self.game_over = True
                            print("KAZANDIN 🎉")
                    self.page.update()
                else:
                    self.game_over = True
                    print(f"YANLIŞ! Oyun bitti. Beklenen: {accept_type}, gelen: {dropped_type}")

            target = ft.DragTarget(
                group="shapes",
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(emoji, size=26),
                            ft.Text(label, size=16, color="#0E444D"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    bgcolor="#FFF",
                    border_radius=16,
                    padding=12,
                    height=100,
                    alignment=ft.alignment.center,
                    border=ft.border.all(2, "#EDE6DD"),
                ),
                on_accept=on_accept,
            )
            return ft.Container(content=target, expand=True)

        return ft.Row(
            controls=[
                bin_box("Üçgen", "triangle", "▲"),
                bin_box("Kare", "square", "■"),
                bin_box("Dikdörtgen", "rectangle", "▬"),
                bin_box("Daire", "circle", "●"),
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
