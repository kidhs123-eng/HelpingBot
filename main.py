import os
import base64
import tkinter as tk
import pyautogui
from groq import Groq
import pynput
from pyperclip import copy
import io
import re
import threading
import keyboard
import ctypes
import ctypes.wintypes
import base64
from io import BytesIO
from PIL import Image





#--------------------------------------------------------

#Написать pip install -r requirements.txt

#--------------------------------------------------------

# Для винды!!!!!!!
def remove_shadow_and_animation(root):
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

    DWMWA_TRANSITIONS_FORCEDISABLED = 3
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_TRANSITIONS_FORCEDISABLED,
        ctypes.byref(ctypes.c_int(1)),
        ctypes.sizeof(ctypes.c_int)
    )
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, 11, ctypes.byref(ctypes.c_int(0)), 4
    )


def get_compressed_screenshot_base64(screenshot, width=1024, quality=60):

    if screenshot.mode != "RGB":
        screenshot = screenshot.convert("RGB")

    screenshot.thumbnail((width, width), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    screenshot.save(buffer, format="JPEG", quality=quality, optimize=True)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    res = f"data:image/jpeg;base64,{img_str}"
    print(len(res), res)
    return f"data:image/jpeg;base64,{img_str}"

client = Groq(api_key=os.getenv("GROQ"))

def image_to_data_url(img):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{data}"

def clean_markdown(text):
    text = re.sub(r'[#*_`~$]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def ask_groq(image_data_url):
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": "Ты отвечаешь на вопросы с картинок. Правила: никогда не повторяй вопрос в ответе. Отвечай ВСЕГДА на том же языке, на котором написан вопрос. Если вопрос с вариантами ответа — пиши ТОЛЬКО букву или само слово, ничего больше. Если вопрос открытый — отвечай кратко, 1-2 предложения, без объяснений и вступлений. Никогда не используй символы форматирования: #, *, _, $, ~, `."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url}
                    }
                ]
            }
        ],
        temperature=0,
        max_completion_tokens=1024,
        top_p=1,
        stream=False
    )
    result = completion.choices[0].message.content
    return clean_markdown(result)


class HelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Helper")
        self.root.geometry("350x350")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.2)



        self.text = tk.Text(
            root,
            wrap="word",
            font=("Arial", 12),
            relief="flat",
            bg=root.cget("bg"),
            state="disabled",
            padx=10,
            pady=10
        )
        self.text.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(root, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.set_text("Нажми Ctrl+Shift+X")

        # self.listener = keyboard.GlobalHotKeys({
        #     '<cmd>+<shift>+x': self.scan_and_ask
        # })
        # self.listener.start()



        # Для винды!!!!!!!
        keyboard.add_hotkey('ctrl+shift+x', self.scan_and_ask)

        self.root.update()
        remove_shadow_and_animation(root)

    def set_text(self, msg):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", msg)
        self.text.config(state="disabled")

    def scan_and_ask(self):

        threading.Thread(target=self.do_scan, daemon=True).start()

    def do_scan(self):


        self.root.after(0, lambda: self.set_text("Analyzing..."))
        try:
            screenshot = pyautogui.screenshot()
            result = ask_groq(get_compressed_screenshot_base64(screenshot))
            self.root.after(0, lambda: self.set_text(f"Ответ:\n{result}"))
            copy(result)
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda: self.set_text(f"Ошибка:\n{err}"))




if __name__ == "__main__":
    root = tk.Tk()
    app = HelperApp(root)

    root.mainloop()