import flet as ft

class EmotionsIndexPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/emotions_index")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#FAF5EF"
        self.spacing = 20
        self.padding = 20

        self.controls = [
            self.app.get_index_element("Duyguları Tanı", "modules/which-kid-has-emotion/thumbnail.png", "/which_kid_has_emotion"),
            self.app.get_index_element("Ne Oldu Burada?", "modules/whats-going-on/thumbnail.png", "/whats_going_on"),
        ]