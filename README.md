# HTMLの雛型生成ツール

趣味のゲーム制作のため、Wordpressでブログサイトを複数立ち上げたことがあったのですが、いい加減HTMLで毎回同じようなテンプレートを生成するのに疲れて作ったツールです。自分用のツールなので、メンテナンスも不具合対応もするつもりはありません。

タイトルにあるひな形生成ツールなので、HTMLページの生成...と言っても大したことはしません。また、ページのレイアウトは、2017~8頃のWordpressの標準テーマを意識したもので、最近のデザインのトレンドにはちょっと追いついていない感じもします。

実際、行っているのはボックスレイアウト、タイポグラフィ、グーグルフォントのリンク挿入、CSS、Javascriptのリンク挿入などの操作をjinjaテンプレートを利用して自動化しているだけです。レイアウトに関してはCSSも生成するので、マージン関連でしくじってCSSをポチポチいじりながら「むきーっ」となる事態を防止できるというのが、主な目的だった気がします。

## 使い方

ツールとしては完成していません。よって、makehtml.pyのメイン関数に直接、ページの要件を記述して実行する形になります。サンプルとして、makehtml.pyの抜粋を下記に示します。

```
if __name__ == '__main__':
    page = Page()
    page.add_style(CSS('css/style.css'))
    page.add_script(Script('js/script.js'))
    page.add_menu(Menu("Item1", 'menu-1', 'menu-item', 'http://example.com/menu'))
    page.add_menu(Menu("Item2", 'menu-2', 'menu-item', 'http://example.com/menu'))
    page.add_menu(Menu("Item3", 'menu-3', 'menu-item', 'http://example.com/menu'))
    page.add_font('<link href="https://fonts.googleapis.com/css?family=Roboto&display=swap" rel="stylesheet">')

    CSSGenerator().make()
    html_maker = HTMLGenerator()
    html_maker.make_html('test-article', page=page, post=Post())
    html_maker.make_html('post-list', page=page, posts=[Post(_class='post post-list')]*3)
    html_maker.make_html('post-grid', page=page, posts=[Post(_class='post post-grid')]*6)
```

面倒くさいですね。本当は設定ファイルを介して、これらの設定を行うようにしたかったのですが、そこまでする意味がなかったのでスクリプトにハードコードして利用しています。一応、メインに記述されている処理の説明をします。

Pageクラスは、Webページの雛型の記述を保持するクラスです。サイトである程度共通になるheadタグの内容、ナビゲーションメニューの項目、グーグルフォントの記述などをPageクラスで指定します。

CSSGeneratorくらすも、単にsassコンパイラを呼び出して、cssファイルを生成するだけの簡単なものです。

HTMLGeneratorクラスは、設定されたPageクラスのインスタンスの内容を参照して、実際のHTMLを生成します。make_htmlの第一引数は、templatesフォルダ内にあるjinjaテンプレートの名称を指定します。このクラスも、実はただjinjaのrender_templateを呼び出して、ファイルを書きだしているだけです。ただし、冒頭にある通り、このツールはWordpressっぽいブログサイトの雛型を作るのが目的なので、「投稿」とか「検索結果」に相当する領域は、ページ全体のテンプレートから分離されており、HTML生成時にはめ込むようになっています。

というわけで、このツールはPythonのスクリプトというより、よく使うHTMLのレイアウトをjinjaテンプレート化してストックする…というのが目的のツールであり、スクリプトはおまけのようなものだったりします。

# ライセンス

特に決めていません。再配布する価値のあるプログラムでもないですので…ただ、ご使用は自由です。実際、レイアウトはよく似ているけど、デザインがちょっと違う…というHTMLを大量に作りたい場合には、結構役立つのではないかなぁ、と思います。何度も、同じようなHTMLをコーディングしていると気づいたら、さっそくjinjaテンプレート化して、templatesフォルダに突っ込むことで、ツールが生成できるHTMLのバリエーションを広げることもできますし…。

