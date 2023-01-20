# 実験ａ: IoTシステム

動作させる際は，lineconfig.py に，アクセストークン及びチャンネルシークレットを記入してください．


## 依存ライブラリ

本システムは，ラズベリーパイ上で動作させることを想定しています．
おそらく確実に追加インストールする必要があるライブラリを，以下に示します．

|  ソースコード上表記  |  pip install上表記  |
| ----------------- | ----------------- |
|    selenium       |      selenium     |
|        bs4        |   beautifulsoup4  |
| webdriver_manager | webdriver_manager |
|      linebot      |    line-bot-sdk   |

python2系と3系が共存している可能性がある場合， `sudo pip3 install ○○` としてください．
そして，ラズパイ使用者はchromedriverをダウンロードするため，chromium-chromedriverをインストールする必要があります．
`sudo apt-get install chromium-chromedriver`
を実行してインストールしてください．chrome更新に合わせて再インストールする必要があると思われます．
また、chromiumとバージョンが合わない場合は
`sudo apt-get install chromium-browser`
を行ってください。