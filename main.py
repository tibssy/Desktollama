from typing import Any, List, Optional, Union

import flet as ft
import textwrap
import ollama
import asyncio



class DropdownMenu(ft.PopupMenuButton):
    def __init__(
            self,
            color: Optional[str] = '#cccccc',
            bgcolor: Optional[str] = '#282828',
            items: list = None,
            value: Optional[str] = 'Select Model'
    ):
        super().__init__()
        self.color = color
        self.bgcolor = bgcolor
        self.value = value
        self.selected_text = self.create_selected_text()
        self.content = self.create_content()
        self.items = self.create_items(items)
        self.shape = ft.RoundedRectangleBorder(6)
        self.elevation = 8

    def create_selected_text(self) -> ft.Text:
        return ft.Text(value=self.value, color=self.color, weight=ft.FontWeight.W_700)

    def create_content(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    self.selected_text,
                    ft.Icon(name=ft.icons.ARROW_DROP_DOWN, color=self.color, size=26)
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=4,
            ),
            bgcolor=self.bgcolor,
            height=30,
            border_radius=6,
            alignment=ft.alignment.center_left,
            padding=ft.padding.only(left=12, right=6)
        )

    def create_items(self, items) -> list:
        if items is None:
            return []
        return [
            self.create_popup_menu_item(item) for item in items
        ]

    def create_popup_menu_item(self, item: str) -> ft.PopupMenuItem:
        return ft.PopupMenuItem(
            content=ft.Row(
                controls=[
                    ft.Icon(name=ft.icons.SMART_TOY_OUTLINED, color=self.color, size=22),
                    ft.Text(item, weight=ft.FontWeight.W_700, color=self.color)
                ]
            ),
            height=30,
            on_click=self.update_button
        )

    def update_button(self, e) -> None:
        self.value = e.control.content.controls[1].value
        self.selected_text.value = self.value
        self.update()


class Tabs(ft.Tabs):
    def __init__(self):
        super().__init__()
        self.selected_index = 0
        self.scrollable = True
        self.unselected_label_color = '#fab86c'
        self.tab_alignment = ft.TabAlignment.START_OFFSET
        self.animation_duration = 400
        self.indicator_tab_size = True
        self.indicator_border_radius = 4
        self.label_color = '#282828'
        self.divider_color = '#282828'
        self.divider_height = 50
        self.indicator_padding = ft.padding.symmetric(horizontal=2, vertical=5)
        self.indicator_border_side = ft.BorderSide(
            width=30,
            color='#fab86c',
        )
        self.tabs = [
            ft.Tab(
                content=ft.Text("This is the settings tab")
            )
        ]

    def add_tab(self, e):
        self.tabs.append(ChatTab(title=f'New Chat'))
        self.selected_index = len(self.tabs) - 1
        self.update()

    def close_tab(self, tab):
        self.tabs.remove(tab)
        self.selected_index = len(self.tabs) - 1
        self.update()

    def duplicate_tab(self, tab):
        self.tabs.insert(self.selected_index + 1, ChatTab('copy'))
        self.selected_index += 1
        self.update()

    def settings(self, e):
        self.selected_index = 0
        self.update()


class ChatTab(ft.Tab):
    def __init__(self, title=None):
        super().__init__()
        self.tab_title = title
        self.tab_content = self._create_tab_content()
        self.content = self._create_chat_content()

    def _create_tab_content(self):
        icon = ft.Icon(name=ft.icons.WECHAT_OUTLINED, size=20)
        text = ft.Text(
            value=textwrap.shorten(self.tab_title, width=20, placeholder="..."),
            weight=ft.FontWeight.W_600
        )
        return ft.Container(
            content=ft.Row(controls=[icon, text]),
            padding=ft.padding.only(right=12)
        )

    def _create_chat_content(self):
        chat_header = self._create_chat_header()
        chat_history = self._create_chat_history()
        chat_input = self._create_chat_input()

        return ft.Container(
            content=ft.Column(
                controls=[chat_header, chat_history, chat_input]
            ),
            padding=ft.padding.only(left=20, top=10, right=20, bottom=20),
            bgcolor='#404040'
        )

    def _create_chat_header(self):
        duplicate_button = self._create_icon_button(
            icon=ft.icons.CONTROL_POINT_DUPLICATE,
            tooltip='Duplicate',
            on_click=lambda e: self._handle_duplicate()
        )
        close_button = self._create_icon_button(
            icon=ft.icons.CLOSE,
            tooltip='Close',
            on_click=lambda e: self._handle_close()
        )

        model_dropdown = DropdownMenu(
            color='#282828',
            bgcolor='#fab86c',
            items=sorted(i['name'] for i in ollama.list().get('models'))
        )

        buttons_row = ft.Row(controls=[duplicate_button, close_button])

        return ft.Row(
            controls=[
                model_dropdown,
                ft.Text('page'),
                buttons_row
            ],
            height=30,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def _create_chat_history(self):
        return ft.ListView(
            expand=True,
            padding=60,
            spacing=20,
            auto_scroll=True,
            divider_thickness=1
        )

    def _create_chat_input(self):
        return ft.CupertinoTextField(
            color='#fdb975',
            bgcolor='#272727',
            focused_bgcolor='#333333',
            max_lines=6,
            border=ft.border.all(width=0, color='#222222'),
            border_radius=6,
            shift_enter=True,
            suffix=self._create_send_button(),
            shadow=ft.BoxShadow(
                blur_radius=6,
                color='#000000',
                offset=ft.Offset(0, 1),
            ),
            # on_submit=self.submit_message
        )

    def _create_send_button(self):
        return ft.IconButton(
            icon=ft.icons.SEND,
            splash_color='green',
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
            ),
            # on_click=self.submit_message
        )

    def _create_icon_button(self, icon, tooltip, on_click):
        """Helper to create an icon button with consistent style."""
        return ft.IconButton(
            icon=icon,
            padding=0,
            tooltip=tooltip,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(6)
            ),
            on_click=on_click
        )

    def _handle_duplicate(self):
        if self.parent:
            self.parent.duplicate_tab(self)

    def _handle_close(self):
        if self.parent:
            self.parent.close_tab(self)


class DesktollamaApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.tabs = Tabs()
        self.setup_page()

    def setup_page(self):
        self.page.title = 'Desktollama'
        self.page.padding = 0
        self.page.spacing = 0
        self.page.theme = ft.Theme(color_scheme_seed='#fab86c')
        self.page.overlay.append(self.create_overlay_container())

        self.page.add(
            ft.Container(
                self.tabs,
                expand=True,
                bgcolor="#282828",
            )
        )

    def create_overlay_container(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    self.create_icon_button(ft.icons.SETTINGS_APPLICATIONS, "Settings", self.tabs.settings),
                    self.create_icon_button(ft.icons.ADD_BOX, "New Chat", self.tabs.add_tab),
                ],
                spacing=2
            ),
            bgcolor='#282828',
            width=84,
            height=46,
            padding=0,
        )

    def create_icon_button(self, icon: str, tooltip: str, on_click) -> ft.IconButton:
        return ft.IconButton(
            icon=icon,
            icon_size=40,
            tooltip=tooltip,
            hover_color='#00000000',
            focus_color='#00000000',
            highlight_color='#6cfa6d',
            padding=0,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(6)
            ),
            on_click=on_click
        )


def main(page: ft.Page):
    DesktollamaApp(page)


ft.app(main)
