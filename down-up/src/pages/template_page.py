import flet as ft

class TemplatePage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/template")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#FAF5EF"
        self.padding = 20

        self.controls = [
            ft.Text("TemplatePage()")
        ]