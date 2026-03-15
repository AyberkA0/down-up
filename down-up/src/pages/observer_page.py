import flet as ft
from flet_barcode_scanner import BarcodeScanner, BarcodeFormat, DetectionMode, CameraFacing
import json, io, base64, qrcode

STORAGE_KEY = "observer_items"

class ObserverPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/")
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.padding = 20
        self.bgcolor = "#FAF5EF"

        self.items = self._load_items()

        self.user_id_tf = ft.TextField(label="Kullanıcı ID", hint_text="QR okut ya da elle yaz", dense=True, expand=True)
        self.user_id_tf.on_change = self._validate

        self.name_tf = ft.TextField(label="Yerel İsim", hint_text="Sadece bu cihazda kullanılacak", dense=True, expand=True)
        self.name_tf.on_change = self._validate

        self.scan_btn = ft.IconButton(icon=ft.Icons.QR_CODE_SCANNER)
        self.scan_btn.on_click = lambda e: self.scanner.start()

        self.add_btn = ft.FilledButton("Ekle", icon=ft.Icons.ADD, disabled=True)
        self.add_btn.on_click = self._add_item

        self.show_my_qr_btn = ft.OutlinedButton("Benim QR Kodum", icon=ft.Icons.QR_CODE)
        self.show_my_qr_btn.on_click = self._show_my_qr

        self.list_column = ft.Column(spacing=8, expand=True)

        self.scanner = BarcodeScanner(
            camera_facing=CameraFacing.BACK,
            detection_mode=DetectionMode.ONCE,
            formats=[BarcodeFormat.QR],
            torch=False,
            auto_close=True,
            overlay_title="Kameraya QR kodu gösterin",
            on_result=self._on_scan_result,
        )
        self.page.overlay.append(self.scanner)

        self.qr_dialog = ft.AlertDialog(modal=True, title=ft.Text("QR Kodun"), actions=[ft.TextButton("Kapat", on_click=self._close_qr_dialog)])

        self._rebuild_list_controls()

        self.controls = [
            ft.Container(
                padding=12,
                border_radius=16,
                bgcolor=ft.Colors.GREY_100,
                content=ft.Column(
                    [
                        ft.Text("Çalışma Takibi", size=30, font_family="MPlus Bold", color="#0E444D"),
                        ft.Text("Öğrencilerin gelişimlerini izle!", size=18, font_family="MPlus", color="#0E444D"),
                        ft.Container(height=12),
                        ft.Row([self.user_id_tf, self.scan_btn], spacing=10),
                        ft.Row([self.name_tf], spacing=10),
                        ft.Row([self.add_btn, self.show_my_qr_btn], spacing=10),
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            ft.Text("Kayıtlar", size=16, weight=ft.FontWeight.W_600),
            self.list_column,
        ]

    def _toast(self, text):
        self.page.snack_bar = ft.SnackBar(ft.Text(text))
        self.page.snack_bar.open = True
        self.page.update()

    def _load_items(self):
        try:
            data = self.page.client_storage.get(STORAGE_KEY)
            return json.loads(data) if data else []
        except Exception:
            return []

    def _save_items(self):
        self.page.client_storage.set(STORAGE_KEY, json.dumps(self.items, ensure_ascii=False))

    def _rebuild_list_controls(self):
        self.list_column.controls.clear()
        if not self.items:
            self.list_column.controls.append(
                ft.Container(
                    bgcolor=ft.Colors.GREY_100,
                    padding=14,
                    border_radius=12,
                    content=ft.Text("Henüz kayıt yok.", size=14, color=ft.Colors.GREY_700),
                )
            )
        else:
            for idx, it in enumerate(self.items):
                self.list_column.controls.append(
                    ft.Card(
                        elevation=1,
                        surface_tint_color=ft.Colors.TRANSPARENT,
                        content=ft.Container(
                            padding=12,
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(it.get("name", ""), size=16, weight=ft.FontWeight.W_600),
                                            ft.Text(it.get("user_id", ""), size=13, selectable=True, color=ft.Colors.GREY_700),
                                        ],
                                        tight=True,
                                        spacing=2,
                                    ),
                                    ft.Row(
                                        [
                                            ft.IconButton(icon=ft.Icons.CONTENT_COPY, tooltip="Kullanıcı ID kopyala", on_click=lambda e, uid=it.get("user_id", ""): self._copy_uid(uid)),
                                            ft.IconButton(icon=ft.Icons.DELETE_OUTLINED, tooltip="Sil", on_click=lambda e, i=idx: self._delete_item(i)),
                                        ],
                                        spacing=4,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ),
                    )
                )

    def _validate(self, e=None):
        uid_ok = bool(self.user_id_tf.value.strip())
        name_ok = bool(self.name_tf.value.strip())
        self.add_btn.disabled = not (uid_ok and name_ok)
        self.add_btn.update()

    def _on_scan_result(self, e: ft.ControlEvent):
        raw = ""
        try:
            payload = json.loads(e.data) if e.data else {}
            raw = payload.get("rawValue") or payload.get("raw", "") or ""
        except Exception:
            raw = (e.data or "").strip()
        if raw:
            self.user_id_tf.value = raw
            self._toast("QR okutuldu")
        self._validate()
        self.page.update()

    def _add_item(self, e):
        uid = self.user_id_tf.value.strip()
        nm = self.name_tf.value.strip()
        if not uid or not nm:
            return
        existing_idx = next((i for i, it in enumerate(self.items) if it.get("user_id") == uid), None)
        if existing_idx is not None:
            self.items[existing_idx]["name"] = nm
        else:
            self.items.append({"user_id": uid, "name": nm})
        self._save_items()
        self.user_id_tf.value = ""
        self.name_tf.value = ""
        self._rebuild_list_controls()
        self._toast("Kayıt eklendi")
        self._validate()
        self.page.update()

    def _delete_item(self, index: int):
        try:
            self.items.pop(index)
            self._save_items()
            self._rebuild_list_controls()
            self.page.update()
        except Exception:
            pass

    def _copy_uid(self, uid: str):
        self.page.set_clipboard(uid)
        self._toast("Kullanıcı ID kopyalandı")

    def _clear_all(self, e):
        if not self.items:
            return
        def do_close(_=None):
            dlg.open = False
            self.page.update()
        def do_clear(_=None):
            self.items.clear()
            self._save_items()
            self._rebuild_list_controls()
            dlg.open = False
            self.page.update()
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Tüm kayıtlar silinsin mi?"),
            content=ft.Text("Bu işlem yerel kayıtların tamamını kaldırır."),
            actions=[ft.TextButton("Vazgeç", on_click=do_close), ft.TextButton("Sil", on_click=do_clear)],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _show_my_qr(self, e):
        uid = self.page.client_storage.get("user_id") or self.user_id_tf.value.strip()
        if not uid:
            self._toast("QR üretmek için bir Kullanıcı ID gerekli")
            return

        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(uid)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        img_control = ft.Image(src_base64=b64, width=240, height=240, fit=ft.ImageFit.CONTAIN)
        uid_text = ft.Text(uid, size=12, selectable=True, color=ft.Colors.GREY_700)

        qr_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("QR Kodun"),
            content=ft.Column([img_control, uid_text], tight=True, spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[ft.TextButton("Kapat", on_click=lambda ev: self.page.close(qr_dialog))]
        )

        self.page.open(qr_dialog)


    def _close_qr_dialog(self, e):
        self.qr_dialog.open = False
        self.page.update()
