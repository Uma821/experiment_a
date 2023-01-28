# 実験ａ: IoTシステム

動作させる際は，lineconfig.py に，アクセストークン及びチャンネルシークレットを記入してください．


## 依存ライブラリ

本システムは，ラズベリーパイ上で動作させることを想定しています．
おそらく確実に追加インストールする必要があるライブラリを，以下に示します．

|  ソースコード上表記  |  pip install上表記  |
| ----------------- | ----------------- |
|     selenium      |      selenium     |
|        bs4        |   beautifulsoup4  |
| webdriver_manager | webdriver_manager |
|      linebot      |    line-bot-sdk   |
|     pykakasi      |      pykakasi     |

python2系と3系が共存している可能性がある場合， `sudo pip3 install ○○` としてください．
そして，ラズパイ使用者はchromedriverをダウンロードするため，chromium-chromedriverをインストールする必要があります．
`sudo apt-get install chromium-chromedriver`
を実行してインストールしてください．chrome更新に合わせて再インストールする必要があると思われます．
また、chromiumとバージョンが合わない場合は
`sudo apt-get install chromium-browser`
を行ってください。

また，I2C16x2LCDを接続するため，I2Cの準備を行ってください．ラズパイのI2Cがenabledになっているかどうか確認してください．
さらに実行時に `smbus.SMBus(1)`の行にエラーが発生した場合は， `sudo apt-get install python-smbus` と `sudo apt-get install i2c-tools`を実行してみてください．

接続機器のアドレスがわからない場合は `i2cdetect -y 1` で確認してください．

SPIについてもラズパイがenabledになっているか確認してください．

Ngrokも使用しますので､ インストールしましょう｡

```
$ wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz
$ tar -xzvf ngrok-v3-stable-linux-arm.tgz
$ sudo mv ngrok /usr/local/bin/
$ ngrok version
ngrok version 3.1.1
```
の流れでインストールして､そしてngrokサイトからアカウントを作成し自分のAuthtokenを `ngrok config add-authtoken <token>` の形式で入力して設定しておきます｡

## 動作環境

ngrok==3.1.1
Python==3.9.2
Flask==1.0.2
line-bot-sdk==1.8.0
urllib3==1.23


## 実行方法

まず､main.pyを動作させましょう｡
現在サーバーをローカルの8080ポートに建てているので､別ターミナルから
`ngrok http 8080`
を実行します｡これで外部に公開されるURL(https://........ngrok.io)が表示されるので､
これをLINEの公式アカウントのWebhook URLに設定してください｡

ここまで行けば､うまく動いているはずです！


