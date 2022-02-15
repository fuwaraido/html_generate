
import html
import sass
import os

from html5print import HTMLBeautifier
from html5print import CSSBeautifier
from jinja2 import evalcontextfilter, Environment, FileSystemLoader
from bs4 import BeautifulSoup
from datetime import datetime

#
# HTML Generate
#
# Wordpress形式のHTMLテンプレートを生成する。プロジェクト形式は下記の通り：
# sass-template/ - ここには、Wordpressサイト生成用のsassのひな型が入っている。
# sass/ - ここには、ボックス要素のスタイルなどを生成するためのsassが入っている。
# sass/style.sass - 個別のサイトのスタイルを指定するために用いるsassファイル（ユーザー定義）。
# このファイルは空でもよい。その場合、sass/_variables.scssのデフォルト値でサイトが生成される。
# css/style.css - 自動生成される。
# templates/ - Wordpress形式のサイトを生成するためのjinjaテンプレートが入っている。
# makehtml.py - スクリプト本体
#

THEME_TEMPLATE_DIR='./templates'

class CSS:

    def __init__(self, url):
        self.type = 'text/css'
        self.url = url

class Script:

    def __init__(self, url):
        self.type = 'text/javascript'
        self.url = url
        self.async_or_defer = ''

#
# TODO: google font対応
#
GOOGLE_FONT_URL='https://fonts.googleapis.com/css2?'
FONT_WEIGHTS={
    'light': 300,
    'regular': 400,
    'semi-bold': 600,
    'bold': 700,
    'extra-bold': 800}

class Font:

    def __init__(self, font_family, font_weight, is_italic=False):
        self.font_family = font_family
        if isinstance(font_weight, str):
            self.font_weight = FONT_WEIGHTS[font_weight]
        else:
            self.font_weight = font_weight
        self.is_italic = is_italic

#
# コンパイル済みフォント情報の例
# {'Open Sans': {'italic': [200, 400], 'non-italic': [200, 400]},
#  'Roboto': {'non-italic': [200, 400]},
#  'Noto Sans': {'italic': [400], 'non-italic': [400]}}
class GoogleFontURL:

    # GoogleFontのクエリを生成する
    def generate_query(self, fonts):
        return self.font_query(self.compile_fonts(fonts))

    # Fontオブジェクトのコンパイル
    def compile_fonts(self, fonts):
        font_infos = {}
        for f in fonts:
            if f.font_family not in font_infos:
                font_infos[f.font_family] = {}
            if f.is_italic:
                if 'italic' not in font_infos[f.font_family]:
                    font_infos[f.font_family]['italic'] = []
                font_infos[f.font_family]['italic'].append(f.font_weight)
            else:
                if 'non-italic' not in font_infos[f.font_family]:
                    font_infos[f.font_family]['non-italic'] = []
                font_infos[f.font_family]['non-italic'].append(f.font_weight)
        return font_infos

    # 辞書に格納されたフォント情報から、フォントファミリーをキーとしてクエリパラメータを生成
    def font_params(self, font_info):
        if 'italic' in font_info:
            if 'non-italic' in font_info:
                if font_info['italic'] == [400] and font_info['non-italic'] == [400]:
                    return 'ital@0;1'
                non_ital = ['0,' + str(i) for i in font_info['non-italic']]
            else:
                non_ital = []
            ital = ['1,' + str(i) for i in font_info['italic']]       
            return 'ital,wght@' + ';'.join(non_ital + ital)
        else:
            return 'wght@' + ';'.join([str(i) for i in font_info['non-italic']])

    # 辞書に格納されたフォント情報から、GoogleFontのクエリ生成
    def font_query(self, font_infos):
        queries = []
        for family in font_infos:
            params = self.font_params(font_infos[family])
            queries.append('+'.join(family.split(' ')) + ':' + params)
        return GOOGLE_FONT_URL + '&'.join(queries + ['display=swap'])

class Menu:

    def __init__(self, label, id, _class, url):
        self.label = label
        self.id = id
        self._class = _class
        self.url = url

class Page:

    def __init__(self):
        self.scripts = {'head':[],'body':[],'footer':[]}
        self.styles = {'head':[], 'body':[], 'footer':[]}
        self.fonts = []
        self.site_url = 'http://example.com'
        self.site_name = 'website'
        self.title = 'Title'
        self.year_from = 2001
        self.year_to = 2019
        self.charset = 'utf-8'
        self.lang = 'ja-JP'
        self.has_side_nav = False
        self.has_secondary = True
        self.main_navigation = []
        self.wrap_navigation = False

    def add_font(self, font_tag):
        self.fonts += [font_tag]

    def add_menu(self, menu):
        self.main_navigation += [menu]

    def add_script(self, script, location='head'):
        self.scripts[location] += [script]

    def add_style(self, style, location='head'):
        self.styles[location] += [style]

class Post:

    def __init__(self, **kwargs):
        self.id = 'post-1'
        self._class = kwargs['_class'] if '_class' in kwargs else 'post'
        self.title = 'Title'
        self.excerpt = 'This is excerpt of this post'
        self.published = datetime.now()

class HTMLGenerator:

    def __init__(self):
        self.theme_template_dir = THEME_TEMPLATE_DIR        
        self.env = self.init_environment()

    def init_environment(self):
        file_loader = FileSystemLoader(self.theme_template_dir)
        env = Environment(loader=file_loader)
        env.filters['quote'] = lambda s: '"{}"'.format(s)
        env.filters['esc'] = lambda s: html.escape(s)
        env.filters['date'] = lambda d: d.strftime('%Y/%m/%d')
        return env

    def make_html(self, template_name, **kwargs):
        template = self.env.get_template(template_name + '.jinja')
        html = template.render(**kwargs)
        soup = BeautifulSoup(html, 'html.parser')
        with open(template_name + '.html', 'w', encoding='utf-8', newline='\n') as f:
            f.write(HTMLBeautifier.beautify(soup.prettify('utf-8'), 4))

SASS_TEMPLATES = [
    'variables',
    'typography',
    'box'
]

#
# SASSのテンプレートを生成する
#
# ./sass/ディレクトリ内の_box.sass, _typography.sass, _variables.sassを生成する。
# これはHTML及びCSSの生成に不可欠なものではなく、デフォルト値を埋めるために使っている。
# 現在のデザインテンプレートは、エリアとしてprimary, secondary, widgets, post...などの
# 「ボックス」を利用しているが、この論理的なレイアウト自体を変更したい場合、sass-template/variables.jinja
# を変更する。ただし、その場合、templates以下のjinjaテンプレートも併せて変更する必要があるので注意すること。
# そこまで根本的なデザインの変更が無く、見た目のみを変えたいだけなら、自動生成されたsass/style.scssの修正で十分。
#
class SASSGenerator:

    def __init__(self):
        pass

    def make(self):
        file_loader = FileSystemLoader('sass-template')
        env = Environment(loader=file_loader)
        for template_name in SASS_TEMPLATES:
            self.make_one(env, template_name)

    def make_one(self, env, template_name):        
        template = env.get_template(template_name + '.jinja')
        with open('sass/_' + template_name + '.scss', 'w') as f:
            f.write(template.render())

#
# SASSからCSSを生成する
#
# 直下にcssディレクトリが存在しない場合、ディレクトリを作成する。
# マージンやレイアウト、タイポグラフィを変更したい場合、sass/style.sassを修正すると、
# sass/_variables.scssの値をオーバーライドするので、スタイルの見た目をコントロールできる。
#
class CSSGenerator:

    def __init__(self):
        self.filename = 'sass/style.scss'

    def make(self):
        # if there is no "css" directory, create one
        if not os.path.isdir('./css'):
            if os.path.exists('./css'):
                raise Exception('a file named css exists in a directory. please move or delete this file!')
            else:
                os.mkdir('css')
        # compile sass and write it in css/style.css
        with open(self.filename) as f:
            css = sass.compile(string=f.read())
            with open('css/style.css', 'w') as f:
                f.write(css)

#
# サンプルのテンプレートを生成するテストコード
#
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


       
