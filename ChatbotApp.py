from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.progressbar import MDProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from chatbot_core import ChatbotCore
import os
import sys

# Set the app icon (use consistent file format, either .ico or .png)
Window.icon = 'icon.ico'

# Define the function for resource paths (useful for PyInstaller)
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ChatbotApp(MDApp):
    def build(self):
        # Optional: If using resource_path, set app icon using it
        self.icon = resource_path("icon.ico")  # Use the same icon as Window.icon
        self.chatbot = ChatbotCore()

        # Set the primary palette and hue for the theme
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "800"  # Dark shade of green
        self.title = "SILVER.Ai"

        # Root Layout
        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)

        # Welcome Message
        self.welcome_label = MDLabel(
            text="Welcome to the AI Chatbot!",
            halign="center",
            valign="middle",
            font_style="H4",
            size_hint_y=None,
            height=50,
        )
        layout.add_widget(self.welcome_label)

        # Chat Display
        self.chat_display = MDScrollView(size_hint=(1, 0.7))
        self.chat_label = MDLabel(
            text="",
            size_hint_y=None,
            height=1000,
            valign="top",
            padding=(10, 10),
        )
        self.chat_label.bind(texture_size=self._update_label_height)  # Bind to update height dynamically
        self.chat_display.add_widget(self.chat_label)
        layout.add_widget(self.chat_display)

        # Input and Send Button Layout
        self.input_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.1), padding=(5, 5), spacing=5)

        # Input Field with Border
        self.input_field = MDTextField(
            hint_text="Type your message...",
            multiline=False,
            mode='rectangle',  # Add a border to the text field
            height='48dp',  # Ensure the height matches the send button
            line_color_focus=(0, 0.5, 0, 1),  # Dark green line color when focused
            on_text_validate=self.handle_input  # Bind Enter key to handle_input
        )
        self.input_layout.add_widget(self.input_field)

        # Send Button
        self.send_button = MDRaisedButton(
            text="Send", height='48dp', size_hint_x=None, width=100, on_release=self.handle_input,
            md_bg_color=(0, 0.5, 0, 1)  # Dark green background
        )
        self.input_layout.add_widget(self.send_button)

        layout.add_widget(self.input_layout)

        # Loading Indicator (Progress Bar)
        self.loading_indicator = MDProgressBar(
            size_hint=(1, None), height='4dp', opacity=0, color=(0, 0.5, 0, 1)  # Dark green loading bar
        )
        layout.add_widget(self.loading_indicator)

        return layout

    def _update_label_height(self, instance, value):
        instance.height = value[1]
        self.chat_display.scroll_to(self.chat_label)  # Scroll to the latest message and keep it there

    def show_loading(self):
        self.loading_indicator.opacity = 1
        self.input_layout.opacity = 0
        # Start loading bar animation
        self.loading_indicator.value = 0
        Clock.schedule_interval(self.increment_loading, 0.1)

    def hide_loading(self):
        self.loading_indicator.opacity = 0
        self.input_layout.opacity = 1
        # Stop loading bar animation
        Clock.unschedule(self.increment_loading)

    def handle_input(self, instance):
        user_message = self.input_field.text.strip()
        if not user_message:
            return

        # Hide welcome message after user enters a message
        self.welcome_label.opacity = 0

        # Display user's message
        self.chat_label.text += f"\nYou: {user_message}"
        self.input_field.text = ""

        # Show loading indicator and hide input layout
        self.show_loading()

        # Schedule response processing
        Clock.schedule_once(lambda dt: self.process_response(user_message), 3)

    def process_response(self, user_message):
        try:
            ai_response = self.chatbot.get_response(user_message)
            self.chat_label.text += f"\nSilver: {ai_response}"
        except Exception as e:
            ai_response = "Error occurred!"
            print(f"Error in get_response: {e}")

        self.hide_loading()
        self.chat_label.height = max(1000, self.chat_label.texture_size[1])
        self.chat_display.scroll_to(self.chat_label)

    def increment_loading(self, dt):
        if self.loading_indicator.value >= 100:
            Clock.unschedule(self.increment_loading)
            self.loading_indicator.value = 0  # Reset loading bar
        else:
            self.loading_indicator.value += (100 / 30)  # 30 intervals for 3 seconds

if __name__ == "__main__":
    ChatbotApp().run()