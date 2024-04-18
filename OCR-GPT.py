from tkinter import Tk, Toplevel, Canvas, messagebox
import tkinter as tk
import pyautogui as pag
from PIL import ImageGrab, Image
import io
from google.cloud import vision
import os
import openai
from pystray import Icon, Menu, MenuItem
from pynput.keyboard import Key, Listener
import time
import json
import threading
import requests
import datetime
import sys


class OCR_GPT:

    def __init__(self,
                 credential_path="google_api_key_path",
                 openai_key="openai_api_key",
                 pb_key="push_bullet_api_key"):

        if hasattr(sys, "_MEIPASS"):
            self.dir_path = os.path.dirname(sys.executable) # Pythonインタープリタのパス
        else:
            self.dir_path = os.path.dirname(__file__)

        self.w, self.h = pag.size() # スクリーンサイズ

        # キーの入力状況を記録
        self.alt_l_key = False
        self.c_key = False

        self.load_config(credential_path, openai_key, pb_key)



    # 設定項目の読み込み
    def load_config(self, c_path, o_key, p_key):
    
        status = 0
        try:
            cfg_path = os.path.join(self.dir_path, 'config.json')
            f_in = open(cfg_path, "r",encoding="utf-8")
            config = json.load(f_in)

            if c_path == "google_api_key_path":
                self.credential_path = config['credential_path']
            else:
                self.credential_path = c_path

            if o_key == "openai_api_key":
                self.openai_key = config['openai_key']
            else:
                self.openai_key = o_key

            if p_key == "push_bullet_api_key":
                self.pb_key = config['pb_key']
            else:
                self.pb_key = p_key

            self.sleep_time = config['sleep_time']
            self.min_drag = config['min_drag'] # ドラッグ判定される最小のマウス移動距離
            self.radio_button = config['radio_button'] # 設定ウィンドウのラジオボタン
            self.txt_order = config['txt_order'] # ChatGPTに対する命令

            # push bullet にプッシュ通知を行う場合はTrue
            if config['pb_push'] == 1:
                self.pb_push = True
            else:
                self.pb_push = False

            # 選択時にボックスを表示させない場合はTrue
            if config['rect_off'] == 1:
                self.rect_off = True
            else:
                self.rect_off = False

            if self.radio_button == 0:
                self.order1 = "質問に対する回答を日本語で出力しなさい"
            elif self.radio_button == 1:
                self.order1 = "意味を日本語で出力しなさい"
            elif self.radio_button == 2:
                self.order1 = "日本語に翻訳しなさい"
            elif self.radio_button == 3:
                self.order1 = "英語に翻訳しなさい"
            elif self.radio_button == 4:
                self.order1 = self.txt_order
            
            status = 1
        
        except:
            status = 0
            self.create_config()
        
        if status == 0:
            self.error_window("設定ファイルが見つかりません", True)



    # 設定ファイルの更新
    def save_config(self, 
                    c_path = "google_api_key_path",
                    o_key = "openai_api_key", 
                    p_key = "push_bullet_api_key"):

        status = 0
        try:
            cfg_path = os.path.join(self.dir_path, 'config.json')
            f_in = open(cfg_path, "r",encoding="utf-8")
            config = json.load(f_in)

            if c_path == "google_api_key_path":
                config["credential_path"] = self.credential_path
            else:
                config["credential_path"] = c_path

            if o_key == "openai_api_key":
                config["openai_key"] = self.openai_key
            else:
                config["openai_key"] = o_key

            if p_key == "push_bullet_api_key":
                config["pb_key"] = self.pb_key
            else:
                config["pb_key"] = p_key
            
            config["radio_button"] = self.radio_button
            if self.radio_button == 4:
                config["txt_order"] = self.txt_order

            if self.radio_button == 0:
                self.order1 = "質問に対する回答を日本語で出力しなさい"
            elif self.radio_button == 1:
                self.order1 = "意味を日本語で出力しなさい"
            elif self.radio_button == 2:
                self.order1 = "日本語に翻訳しなさい"
            elif self.radio_button == 3:
                self.order1 = "英語に翻訳しなさい"
            elif self.radio_button == 4:
                self.order1 = self.txt_order

            if self.pb_push:
                config["pb_push"] = 1
            else:
                config["pb_push"] = 0
            if self.rect_off:
                config["rect_off"] = 1
            else:
                config["rect_off"] = 0
            
            f_out = open(cfg_path, 'w', encoding="utf-8")
            json.dump(config, f_out, ensure_ascii=False, indent=2, sort_keys=False, separators=(',', ': '))

            status = 1
        
        except:
            status = 0

        if status == 0:
            self.error_window("設定ファイルの更新に失敗しました", False)



    # 設定ファイルが見つからない場合に新規作成
    def create_config(self):

        cfg_path = os.path.join(self.dir_path, 'config.json')
        f_out = open(cfg_path, "a", encoding="utf-8")

        template = {"credential_path":"", "pb_key":"", "openai_key":"", "sleep_time":5, "min_drag": 50, 
                    "radio_button": 1, "pb_push": 1, "rect_off": 0, "txt_order": ""}
        json.dump(template, f_out, ensure_ascii=False, indent=2, sort_keys=False, separators=(',', ': '))



    # エラーウィンドウ作成
    def error_window(self, message, shutdown):

        ret = messagebox.showerror('エラー', message)
        if ret == "ok" or ret == None:
            if shutdown:
                os._exit(0)



    # 実行
    def run(self):

        task_thread1 = threading.Thread(target=self.tasktray_run)
        task_thread1.start()
        self.key_detect()
        task_thread1.join()



    # タスクトレイ上で実行
    def tasktray_run(self):

        def quit_app():
            icon.stop()
            os._exit(0)

        def set_app():
            if self.setting_open:
                return
            self.setting_open = True
            threading.Thread(target=self.settings).start()

        self.setting_open = False

        try:
            img_path = os.path.join(self.dir_path, 'iconimg.ico')
        except:
            self.error_window("iconimg.icoが見つかりません", True)

        image = Image.open(img_path)
        menu = Menu(MenuItem('Quit', quit_app), MenuItem('Settings', set_app))
        icon = Icon(name='test', icon=image, title='OCR-GPT', menu=menu)
        icon.run()



    # 設定画面の構成
    def settings(self):

        def button1enter(event):
            self.radio_button = radio1.get()
            if self.radio_button == 4:
                self.txt_order = txtb1.get()
                self.order1 = self.txt_order
            self.credential_path = txtb2.get()
            self.openai_key = txtb3.get()
            self.pb_key = txtb4.get()
            self.pb_push = check1.get()
            self.rect_off = check2.get()
            self.save_config()
            
            self.setting_open = False
            root.destroy()

        def on_closing():
            self.setting_open = False
            root.destroy()

        root = tk.Tk()
        root.geometry("600x400") # ウィンドウサイズ
        root.resizable(width=False, height=False)
        root.title("設定")
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        static1 = tk.Label(text=u'動作を選択してください')
        static1.place(x=25, y=15)
        static2 = tk.Label(text=u'GCPキーのファイル名(***.json)')
        static2.place(x=15, y=220)
        static3 = tk.Label(text=u'OpenAIのapiキー')
        static3.place(x=15, y=275)
        static4 = tk.Label(text=u'Pushbulletのapiキー')
        static4.place(x=15, y=330)
        static5 = tk.Label(text=u'Push通知に切り替え')
        static5.place(x=420, y=70)
        static6 = tk.Label(text=u'矩形表示オフ')
        static6.place(x=420, y=100)

        radio1 = tk.IntVar()
        radio1.set(self.radio_button)

        rdo0 = tk.Radiobutton(root, value=0, variable=radio1, text='対話  :  入力に対する回答を日本語で出力')
        rdo0.place(x=60, y=40)
        rdo1 = tk.Radiobutton(root, value=1, variable=radio1, text='検索  :  意味を日本語で出力')
        rdo1.place(x=60, y=70)
        rdo2 = tk.Radiobutton(root, value=2, variable=radio1, text='和訳  :  入力を日本語に翻訳')
        rdo2.place(x=60, y=100)
        rdo3 = tk.Radiobutton(root, value=3, variable=radio1, text='英訳  :  入力を英語に翻訳')
        rdo3.place(x=60, y=130)
        rdo4 = tk.Radiobutton(root, value=4, variable=radio1, text='命令を指定  :  入力された命令を実行')
        rdo4.place(x=60, y=160)

        check1 = tk.BooleanVar()
        check2 = tk.BooleanVar()
        check1.set(self.pb_push)
        check2.set(self.rect_off)
        pb_check = tk.Checkbutton(variable=check1)
        rect_check = tk.Checkbutton(variable=check2)
        pb_check.place(x=390, y=70)
        rect_check.place(x=390, y=100)

        button1 = tk.Button(text=u'OK',width=10)
        button1.place(x=440,y=320)
        button1.bind("<Button-1>",button1enter) # 設定項目確定

        txtb1 = tk.Entry(width=40)
        txtb1.place(x=100, y=188)
        txtb1.insert(0,self.txt_order)
        txtb2 = tk.Entry(width=35)
        txtb2.place(x=40, y=250)
        txtb2.insert(0,self.credential_path)
        txtb3 = tk.Entry(width=35)
        txtb3.place(x=40, y=305)
        txtb3.insert(0,self.openai_key)
        txtb4 = tk.Entry(width=35)
        txtb4.place(x=40, y=360)
        txtb4.insert(0,self.pb_key)
        
        root.attributes('-topmost', True)
        root.focus_force()
        root.mainloop()



    # キーが押された際のリスナーを作成
    def key_detect(self):
        with Listener(
            on_press=self.k_press,
            on_release=self.k_release) as listener:
            listener.join()



    def k_press(self, key):

        try:
            if key == Key.alt_l:
                self.alt_l_key = True
        except:
            pass
        try:
            if key.char == 'c':
                self.c_key = True
        except:
            pass
        if self.c_key and self.alt_l_key:
            self.focus_mode() # alc + c の同時押しで、選択モード起動
            self.alt_l_key = False
            self.c_key = False
            time.sleep(1) # インターバル
            


    def k_release(self, key):

        try:
            if key == Key.alt_l:
                self.alt_l_key = False
        except:
            pass
        try:
            if key.char == 'c':
                self.c_key = False
        except:
            pass

    

    # 画面選択モード
    def focus_mode(self):

        # マウスダウン -> 選択の開始
        def start_point_get(event):
            global start_x, start_y

            if not self.rect_off:
                Canvas1.create_rectangle(event.x,
                                        event.y,
                                        event.x + 1,
                                        event.y + 1,
                                        outline="red",
                                        tag="rect1")
            start_x, start_y = event.x, event.y

        # マウスホールド -> ドラッグ
        def rect_drawing(event):

            if event.x < 0:
                end_x = 0
            else:
                end_x = min(self.w, event.x)
            if event.y < 0:
                end_y = 0
            else:
                end_y = min(self.h, event.y)

            if not self.rect_off:
                Canvas1.coords("rect1", start_x, start_y, end_x, end_y)

        # マウスリリース -> 選択の解除
        def release_action(event):
            global start_x, start_y

            if not self.rect_off:
                start_x, start_y, end_x, end_y = Canvas1.coords("rect1")
                Canvas1.delete("rect1")
            else:
                end_x, end_y = event.x, event.y
            root.destroy()
            if (end_x-start_x>self.min_drag or end_y-start_y>self.min_drag):
                # tmpss.png で選択範囲のSSを保存
                ImageGrab.grab(bbox=(start_x+1, start_y+1, end_x, end_y)).save("tmpss.png")
                
                self.text_search()
        
        def exit_root(e):
            root.destroy()


        if self.credential_path=="" or self.openai_key=="":
            self.error_window("タスクトレイの設定画面から、Googleとopenaiのapiキーを入力してください", False)
        else:
            transparent_color = 'white'

            root = Tk()
            root.attributes('-alpha', 0.01)
            root.attributes('-topmost', True)
            root.attributes('-fullscreen', True)

            top = Toplevel(root)
            top.attributes('-transparentcolor', transparent_color)
            top.attributes('-topmost', True)
            top.attributes('-fullscreen', True)

            Canvas1 = Canvas(top, bg=transparent_color, highlightthickness=0)
            Canvas1.pack(fill='both', expand=True)

            root.focus_set()

            root.bind('<Button-1>', start_point_get)
            root.bind('<B1-Motion>', rect_drawing)
            root.bind('<ButtonRelease-1>', release_action)
            root.bind('<Escape>', exit_root) # Escキーで選択の中断

            root.mainloop()



    def text_search(self):

        ocr_res = self.google_ocr()
        if not ocr_res:
            return
        
        response = self.openai_api()
        


    # 画像からテキストの読み込み
    def google_ocr(self, img_name="tmpss.png"):
        
        fullpath = os.path.join(self.dir_path, self.credential_path)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = fullpath

        try:
            client = vision.ImageAnnotatorClient()
        except:
            self.error_window("Google apiキーが見つかりません", False)
            return False

        with io.open(img_name, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        response = client.document_text_detection(image=image)

        texts = response.text_annotations
        self.ocr_str = texts[0].description

        if response.error.message:
            self.error_window("OCRに失敗しました", False)
            return False
        else:
            return texts[0].description
        
        

    # テキストをChatGPTに入力
    def openai_api(self, order="order", body="body"):

        openai.api_key = self.openai_key

        if order == "order":
            input1 = self.order1
        else:
            input1 = order

        if body == "body":
            input2 = self.ocr_str
        else:
            input2 = body

        try:
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": input1},
                {"role": "user", "content": input2},
                ],
            )
        except:
            self.error_window("openaiのapiキーが誤っています", False)
            return None
        
        self.response = response['choices'][0]['message']['content']
        self.output_res()

        return self.response



    # 結果の出力
    def output_res(self):

        # push bullet で通知を行う
        if self.pb_push:
            try:
                dt_now = datetime.datetime.now()
                url = "https://api.pushbullet.com/v2/pushes"
                title = f"OCR-GPT({dt_now.date()}/{dt_now.hour}:{dt_now.minute})"
                body = f"指示： {self.order1}\n入力: {self.ocr_str}\n出力: {self.response}"
                headers = {"content-type": "application/json", "Authorization": 'Bearer '+ self.pb_key}
                data_send = {"type": "note", "title": title, "body": body}
                _r = requests.post(url, headers=headers, data=json.dumps(data_send))
            except:
                self.error_window("Pushbulletのapiキーが間違っています", False)

        # デスクトップウィンドウで通知を行う
        else:
            messagebox.showinfo('出力', f"指示： {self.order1}\n入力: {self.ocr_str}\n出力: {self.response}")


if __name__=="__main__":

    instance = OCR_GPT()
    instance.run()