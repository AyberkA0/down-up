import flet as ft

class DailyLifeIndexPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/daily_life_index")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#FAF5EF"
        self.spacing = 20
        self.padding = 20

        self.controls = [
            self.app.get_index_element("Diş Fırçalama", "modules/tooth-brushing/thumbnail.png", "/tooth_brushing"),
            self.app.get_index_element("Sağlıklı Beslen", "modules/healthy-foods/thumbnail.png", "/healthy_foods"),
        ]
