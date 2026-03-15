import flet as ft

class MathsIndexPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/maths_index")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#FAF5EF"
        self.spacing = 20
        self.padding = 20

        self.controls = [
            self.app.get_index_element("Kaç Tane Kalır?", "modules/how-much/thumbnail.png", "/how_much"),
            self.app.get_index_element("Şekilleri Keşfet", "modules/name-shapes/thumbnail.png", "/name_shapes", fake=True),
        ]