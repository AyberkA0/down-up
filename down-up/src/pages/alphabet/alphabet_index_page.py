import flet as ft

class AlphabetIndexPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/alphabet_index")
        self.app = page.app
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.bgcolor = "#FAF5EF"
        self.spacing = 20
        self.padding = 20

        self.controls = [
            self.app.get_index_element("Alfabe Avı", "modules/which-letter/thumbnail.png", "/which_letter"),
        ]