<div id="top"></div>

## 使用技術
<p style="display: inline">
  <img src="https://img.shields.io/badge/-OpenAI-412991.svg?logo=openai&style=flat&logoColor=white">  <img src="https://img.shields.io/badge/-GoogleCloud-4285F4.svg?logo=googlecloud&style=flat&logoColor=white">  
  <img src="https://img.shields.io/badge/-PushBullet-4AB367.svg?logo=pushbullet&style=flat&logoColor=white">
</p>

## 目次

1. [使用方法](#使用方法)
2. [実行ファイルの作成](#実行ファイルの作成)


## OCR-ChatGPT

Windowsスクリーン上で、ドラッグで選択した範囲の画面からテキストを抽出し、ChatGPTに入力するアプリ。  
ChatGPTに与える命令も指定することができ、翻訳から回答の作成まで状況に合わせて変更可能。  
ChatGptからの出力は、ウィンドウで通知、PushBulletへのプッシュ通知、の2択から選択できる。  
**このアプリの最大のメリットは、画像内のテキストに対しても、スクリーン上での範囲選択という簡単な操作でChatGptへのテキスト入力を行える点。**  
文字の抽出には、GoogleVisionApi、ChatGptへの入力出力には、OpenaiApiを使用。  

  
使用イメージ  
※著作者：<a href="https://jp.freepik.com/free-vector/flat-design-order-sign-template-design_32819551.htm#fromView=search&page=2&position=32&uuid=12975173-1155-4ddb-86dc-0ca1bc099bfd">Freepik</a>  

<img src="https://github.com/Aburaya5123/OCR-ChatGPT/assets/166899082/c1971c96-54c6-499b-b5d8-90b0ec0a984e" width=395>
<img src="https://github.com/Aburaya5123/OCR-ChatGPT/assets/166899082/7a056e11-0c91-4501-bc16-d14460c22e21" width=370>


https://github.com/Aburaya5123/OCR-ChatGPT/assets/166899082/83466e21-b7dd-4a97-a0cc-b93a92a63a15  

※ Wikipedia - https://en.wikipedia.org/wiki/The_Cask



##  使用方法

1. OCR-GPT.pyを実行する前に、同じディレクトリ内に"iconimg.ico"と"config.json"、GoogleCloudのApiキー(.json)を配置する。  
2. OCR-GPT.pyの実行後、タスクトレイアイコンにあるSetting項目から、先程のGoogleCLoudApiキーのファイル名とOpenAIのApiキーを入力する。  
3. 入力を完了させた後、alc + C キーを同時押しで画面選択モードに切り替わるので、ドラッグで画面選択を行う。  
※入力テキストの文字数によっては、出力までに数秒かかる場合がある。  

<img src="https://github.com/Aburaya5123/OCR-ChatGPT/assets/166899082/35725bc4-9536-4173-bc82-b8b570ec48ba" width=370>

・"push通知に切り替え"に✓を入れ、PushBulletのApiキーが入力されていた場合、PushBulletに出力され、通知ウィンドウは作成されない。  
・矩形表示に✓を入れると、画面選択時に選択範囲が赤いボックスで囲われて表示される。  



##  実行ファイルの作成

Pyinstallerを使用することで、実行ファイル(.exe)を作成することが可能。  

手順  
1. Pyinsatllerのインストール (サポートはここで確認 https://pyinstaller.org/en/stable/)  
  `pip install pyinstaller`
2. 作業フォルダに移動し、変換を実行。  
   `cd C:\python_env`  
   `pyinstaller OCR-GPT.py --onefile --noconsole --icon=iconimg.ico`  

distフォルダに出力された.exeファイルは、"iconimg.ico"と"config.json"、GoogleCloudのApiキー(.json)と同じディレクトリに配置。  
