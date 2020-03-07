import requests
# no module named 'requests' が出たら pip install requests
from random import uniform
from time import sleep
from xml.sax.saxutils import unescape
from os import path
from getpass import getpass
# import warnings


# 初期値設定
# プロキシの設定
# environ['https_proxy'] = 'https://127.0.0.1:8888'
# warnings.simplefilter('ignore')
# 初期応募ページ(シリアル入力するページではない)
URL = ''
# UserAgentの偽装(chrome指定)
UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/80.0.3987.88 Safari/537.36'
# シリアルコードのファイル位置
PATH = 'serial.txt'


# 関数
def errchk(res):
    "httpステータスコードが400以上だと10秒待機し、Falseを返す"
    if res.status_code < 400:
        # エラーなし
        return True
    # エラーあり
    print(str(res.status_code) + ' ' + res.reason)
    print('10秒後、再試行します...')
    sleep(10)
    return False


def print_kv(txt, dbl=1.3):
    "キービジュアルを出力する"
    for i in range(int(len(txt) * dbl)):
        print('-', end='')
    print()
    print('     ' + txt)
    for i in range(int(len(txt) * dbl)):
        print('-', end='')
    print('\n')


def get_title(res_txt):
    "ページタイトルを取得し、返す"
    pos_title = res_txt.find('class="title-appli-general"')
    pos_title = res_txt.find('>', pos_title) + 1
    txt = res_txt[pos_title:res_txt.find('</', pos_title)]
    txt += ' - '
    pos_act = res_txt.find('class="this-page"')
    pos_act = res_txt.find('>', pos_act) + 1
    txt += res_txt[pos_act:res_txt.find('</', pos_act)]

    return txt


def untag(raw_txt):
    """HTML<span>タグを外します
    その他表示上不要なものを消します"""
    raw_txt = raw_txt\
        .replace('</span>', '')\
        .replace('&yen;', '\\')\
        .replace('\'>', '">')\
        .replace('<BR>', ' ')\
        .strip()
    txt = ''
    pos_start = 0
    pos_span = raw_txt.find('<span')
    while pos_span >= 0:
        txt += raw_txt[pos_start:pos_span]
        pos_start = raw_txt.find('">', pos_span) + 2
        pos_span = raw_txt.find('<span', pos_start)
    txt += raw_txt[pos_start:]
    return txt.strip()


def gethidden(res_txt):
    "hidden inputを取得(POSTするデータの取得)"
    payload = {}
    pos_input = res_txt.find('<input type="hidden"')
    while pos_input >= 0:
        pos_input_name = res_txt.find('name="', pos_input) + 6
        input_name = res_txt[pos_input_name:res_txt.find('"', pos_input_name)]
        pos_input_end = res_txt.find('>', pos_input_name)
        pos_input_value = res_txt.find('value="', pos_input, pos_input_end) + 7
        if pos_input_value >= 7:
            # valueがある
            input_value = \
                res_txt[pos_input_value:res_txt.find('"', pos_input_value)]
        else:
            # valueがない
            input_value = ''
        # payload(POSTデータ)の生成
        payload.setdefault(input_name, []).append(input_value)

        # 次のinput位置取得
        pos_input = res_txt.find('<input type="hidden"', pos_input_end)

    return payload


# URLが入ってるか確認
if URL == '':
    print('URLが指定されていません')
    print(path.basename(__file__) + ' ファイルを開いてURL変数にURLを追加してください')
    exit(1)

# シリアルコードを取得
try:
    with open(PATH) as f:
        l_serial = [s.strip() for s in f.readlines()]
except FileNotFoundError:
    print('ファイル \'' + PATH + '\' が見つかりません')
    print(' \'' + PATH + '\' に1行1シリアルずつ書いて保存してください')
    exit(1)

# セッション生成
s = requests.Session()
header = {'User-Agent': UA}
# 初回実行フラグ
is_first = True
# 応募完了シリアルリスト
success = []

print('1度選んだ選択は2度目以降も使用され、変更できません')
print('間違えた場合はスクリプト自体を初めからやり直してください\n')

while True:
    r1 = s.get(URL, headers=header)
    if errchk(r1):
        # エラーがなければ抜ける
        break
# textのそのまま(raw)を変数に代入
tr_r1 = r1.text
# text.lower()を頻繁に使うので変数に代入
t_r1 = tr_r1.lower()

pos_kv = tr_r1.find('class="kv-02">') + 14
# キービジュアルの有無を確認
if pos_kv >= 14:
    # キービジュアルを出力
    kv_txt_raw = tr_r1[pos_kv:t_r1.find('</div>', pos_kv)]
    kv_txt = kv_txt_raw.strip().replace('<br>', ' ').replace('\r\n', '')
    print_kv(kv_txt)

sleep(3 + uniform(0, 2))

# 会員登録等のボタンを回避
pos_btn_txt = tr_r1.find('class="btn-ticket')
pos_tkt_btn = tr_r1.rfind('class="ticket-area">', 0, pos_btn_txt) + 20
# 応募するチケット選択
l_tkt = []
while pos_tkt_btn >= 20:
    # シリアル入力URL
    pos_btn_url = t_r1.find('href="', pos_tkt_btn) + 6
    btn_url = tr_r1[pos_btn_url:t_r1.find('"', pos_btn_url)]
    # ボタンのテキスト
    pos_btn_txt = tr_r1.find('class="btn-ticket', pos_btn_url) + 17
    pos_btn_txt = t_r1.find('>', pos_btn_txt) + 1
    btn_txt = tr_r1[pos_btn_txt:t_r1.find('</a>', pos_btn_txt)]
    # チケット一覧リストに追加
    l_tkt.append({'url': btn_url, 'text': btn_txt})
    # 次のチケットを検索
    pos_tkt_btn = tr_r1.find('class="ticket-area">', pos_btn_txt) + 20

# 選択肢があるか確認
if len(l_tkt) > 1:
    for i, tkt in enumerate(l_tkt):
        print('    ' + str(i + 1) + ': ' + tkt['text'])
    print()
    ans = int(input('応募するチケットを選択してください(1～' + str(len(l_tkt)) + '): ').strip())
    # 入力チェック
    if ans < 1 or ans > len(l_tkt):
        print('1～' + str(len(l_tkt)) + 'の数値を入力してください')
        exit(1)
else:
    ans = 1

tkt_url = l_tkt[ans - 1]['url']
# シリアル入力ページ取得
while True:
    r2 = requests.get(tkt_url, headers=header)
    if errchk(r2):
        # エラーがなければ抜ける
        break

tr_r2 = r2.text
t_r2 = tr_r2.lower()

pos_kv = tr_r2.find('id="contents">') + 14
# キービジュアルの有無を確認
if pos_kv >= 14:
    # キービジュアルを出力
    pos_kv = t_r2.find('<h2>', pos_kv) + 4
    kv_txt_raw = tr_r2[pos_kv:t_r2.find('</h2>', pos_kv)]
    kv_txt = kv_txt_raw.strip().replace('<br>', ' ').replace('\r\n', '')
    print_kv(kv_txt)

# ページタイトル取得(エラー処理用)
pos_prev_title = t_r2.find('<title>') + 7
prev_title = tr_r2[pos_prev_title:t_r2.find('</title>', pos_prev_title)]

r2_payload = {}
serial_name = ''
# input(入力箇所)取得
pos_input = t_r2.find('<input')
while pos_input >= 0:
    pos_end_input = t_r2.find('>', pos_input)
    pos_name = t_r2.find('name="', pos_input) + 6
    name = tr_r2[pos_name:t_r2.find('"', pos_name)]
    pos_value = t_r2.find('value="', pos_input) + 7
    value = tr_r2[pos_value:t_r2.find('"', pos_value)]
    # シリアル入力欄か確認
    pos_holder = t_r2.find('placeholder="', pos_input, pos_end_input) + 13
    if pos_holder >= 13:
        holder = tr_r2[pos_holder:t_r2.find('"', pos_holder)]
        if holder == 'シリアルナンバー':
            serial_name = name
    r2_payload[name] = value

    pos_input = t_r2.find('<input', pos_end_input)

# シリアル入力欄が見つかったか確認
if serial_name == '':
    print('シリアルナンバー入力欄が見つかりませんでした')
    print('仕様変更等の可能性があります')
    exit(1)

# submitボタン探査
pos_btn = t_r2.find('<button')
while pos_btn >= 0:
    pos_end_btn = t_r2.find('</button>', pos_btn)
    pos_b_type = t_r2.find('type="', pos_btn, pos_end_btn) + 6
    b_type = tr_r2[pos_b_type:t_r2.find('"', pos_b_type)]
    if b_type == 'submit':
        pos_name = t_r2.find('name="', pos_btn) + 6
        name = tr_r2[pos_name:t_r2.find('"', pos_name)]
        pos_value = t_r2.find('value="', pos_btn) + 7
        value = tr_r2[pos_value:t_r2.find('"', pos_value)]
        r2_payload[name] = value
        break

    pos_btn = t_r2.find('<button', pos_end_btn)


for serial in l_serial:
    s.get(tkt_url, headers=header)
    sleep(3 + uniform(0, 2))
    # 送信データ生成
    payload = {}
    payload.update(r2_payload)
    payload[serial_name] = serial

    # シリアル送信
    while True:
        r3 = s.post(tkt_url, headers=header, data=payload)
        if errchk(r3):
            # エラーがなければ抜ける
            break

    tr_r3 = r3.text
    t_r3 = tr_r3.lower()
    # ページタイトル取得
    pos_new_title = t_r3.find('<title>') + 7
    new_title = tr_r3[pos_new_title:t_r3.find('</title>', pos_new_title)]
    # 前のタイトルと比較(エラー検出)
    if prev_title == new_title:
        pos_err = tr_r3.find('class="form__error"')
        while pos_err >= 0:
            pos_err_txt = tr_r3.find('class="varidation">', pos_err) + 19
            err_txt = tr_r3[pos_err_txt:t_r3.find('</p>', pos_err_txt)]
            # エラー文があるか確認
            if len(err_txt) > 0:
                print('シリアル' + str(l_serial.index(serial) + 1) +
                      '行目 : ' + err_txt)
                print('シリアルナンバー : ' + serial)
                break
            pos_err = tr_r3.find('class="form__error"', pos_err_txt)
        else:
            # 原因不明のエラー
            print('シリアル' + str(l_serial.index(serial) + 1) +
                  '行目 : 原因不明のエラーが発生しました。実際にwebページで操作して確認してください。')
            print('シリアルナンバー : ' + serial)
        continue

    print_kv(new_title, 1.5)

    sleep(3 + uniform(0, 2))
    # 次ページURLの取得
    pos_apply_txt = t_r3.find('>申込む<')
    if pos_apply_txt < 0:
        print('申込むボタンが見つかりませんでした。実際にwebページで操作して確認してください。')
    pos_apply_url = tr_r3.rfind('onclick=', 0, pos_apply_txt)
    pos_apply_url = t_r3.find('\'http', pos_apply_url) + 1
    apply_url = tr_r3[pos_apply_url:t_r3.find('\'', pos_apply_url)]

    # 不要なcookieの削除
    r_cookies = ['visited', 'sfsession', 'AWSELB', 'AWSELBCORS']
    for c in r_cookies:
        try:
            s.cookies.pop(c)
        except KeyError:
            pass
    # cookie差し替え
    # ループ2回目以降、KOJIN_SHIKIBETSUが2つになるため
    try:
        kojin = s.cookies.pop('KOJIN_SHIKIBETSU')
        k_cookie = {'KOJIN_SHIKIBETSU': kojin}
    except KeyError:
        pass

    while True:
        r4 = s.get(apply_url, headers=header, cookies=k_cookie)
        if errchk(r4):
            # エラーがなければ抜ける
            break

    tr_r4 = r4.text
    t_r4 = tr_r4.lower()
    # サービス停止中チェック
    if t_r4.find('サービス停止中') >= 0:
        print('サーバーのサービスが停止中です')
        print('時間をおいてから再度お試しください')
        break

    title_r4 = get_title(tr_r4)
    print_kv(title_r4, 2.5)

    payload = {}
    sleep(3 + uniform(0, 2))

    # hidden inputを取得(POSTするデータの取得)
    payload.update(gethidden(tr_r4))

    # ログインページのURL,POSTデータを取得
    pos_login_btn = tr_r4.find('class="login-bt"')
    pos_login_data = tr_r4.find('sChangeURL(', pos_login_btn)
    pos_login_data = t_r4.find('\'', pos_login_data) + 1
    login_data = tr_r4[pos_login_data:t_r4.find('\'', pos_login_data)]
    pos_login_page_url = t_r4.find('\'http', pos_login_data) + 1
    login_page_url = \
        tr_r4[pos_login_page_url:t_r4.find('\'', pos_login_page_url)]

    # POSTデータを入れ替え
    payload.pop('uji.anchorVerb')
    payload[login_data] = ''

    # ログインページへ
    while True:
        r5 = s.post(login_page_url, headers=header, data=payload)
        if errchk(r5):
            # エラーがなければ抜ける
            break

    tr_r5 = r5.text
    t_r5 = tr_r5.lower()
    # リダイレクトURLの取得
    pos_redirect_url = t_r5.find('<form')
    pos_redirect_url = t_r5.find('"http', pos_redirect_url) + 1
    redirect_url = tr_r5[pos_redirect_url:t_r5.find('"', pos_redirect_url)]
    # リダイレクト
    while True:
        r6 = s.post(redirect_url, headers=header)
        if errchk(r6):
            # エラーがなければ抜ける
            break
    print_kv('ログインページ', 3.5)
    sleep(3 + uniform(0, 2))

    payload = {}
    tr_r6 = r6.text
    t_r6 = tr_r6.lower()
    # ログイン情報の設定
    if is_first:
        r6_payload = {}
        mail = input('    メールアドレス: ')
        passwd = getpass('    パスワード: ')
        r6_payload = {'loginId': mail, 'loginPassword': passwd}
    payload.update(r6_payload)
    # 謎のtoken取得(これないと進まない)
    x_cltft_token = r6.headers['X-CLTFT-Token']

    # ↓ ここなくても多分動作します ↓ #
    # POSTするURL取得(API)
    pos_login_api = r6.text.find('ajaxPostForForm')
    pos_login_api = r6.text.find('+ \'', pos_login_api) + 3
    login_api = r6.text[pos_login_api:r6.text.find('\'', pos_login_api)]
    login_api_url = r6.url[:r6.url.find('/', 8)] + login_api
    header['X-CLTFT-Token'] = x_cltft_token
    # ログイン認証(ユーザー確認)
    r7 = s.post(login_api_url, headers=header, json=payload)
    d_r7 = r7.json()
    if not d_r7['isSuccess']:
        print('ログインに失敗しました')
        print(d_r7['msgs'][0]['msg'])
        exit(1)
    header.pop('X-CLTFT-Token')
    # ↑ ここなくても多分動作します ↑ #

    # POSTするデータ追加
    payload['op'] = 'nextPage'
    payload[x_cltft_token[:x_cltft_token.find('=')]] = \
        x_cltft_token[x_cltft_token.find('=') + 1:]
    # ログインURLの取り出し
    login_url = r6.url[:r6.url.find('?')]
    # ログイン
    while True:
        r8 = s.post(login_url, headers=header, data=payload)
        if errchk(r8):
            # エラーがなければ抜ける
            break

    tr_r8 = r8.text
    t_r8 = tr_r8.lower()
    title_r8 = get_title(tr_r8)
    print_kv(title_r8, 2.5)

    payload = {}
    sleep(3 + uniform(0, 2))

    # 選択肢一覧
    # [{'title','name','value':[],'text':[]}, ...]
    selections = []
    pos_selection = tr_r8.find('class="select-area"')
    pos_end_table = t_r8.find('</table>', pos_selection)
    pos_tr = t_r8.find('<tr>', pos_selection)
    pos_end_tr = t_r8.find('</tr>', pos_tr)
    pos_th = t_r8.find('<th>', pos_tr, pos_end_tr) + 4
    while pos_th >= 4:
        # 選択肢のタイトルの取得
        selection_title = tr_r8[pos_th:t_r8.find('</th>', pos_th)]\
            .replace('<br>', '').replace('\r\n', '')
        # 空欄でない場合、追加
        if selection_title != '':
            selections.append({'title': selection_title})
        pos_th = pos_th = t_r8.find('<th>', pos_th, pos_end_tr) + 4

    if is_first:
        ans_r8 = []
    # 第2希望以降の動作確認できていません
    # 希望選択肢(tr)
    pos_tr = t_r8.find('<tr>', pos_end_tr, pos_end_table) + 4
    while pos_tr >= 4:
        pos_end_tr = t_r8.find('</tr>', pos_tr)
        if is_first:
            pos_txt = t_r8.find('<div>', pos_tr) + 5
            txt = tr_r8[pos_txt:t_r8.find('</div>', pos_txt)]
            print(txt)

        # 項目別(select)
        r_count = 0
        pos_select = t_r8.find('<select', pos_tr, pos_end_tr)
        while pos_select >= 0:
            pos_end_select = t_r8.find('</select>', pos_select)
            pos_select_name = t_r8.find('name="', pos_select) + 6
            select_name = \
                tr_r8[pos_select_name:t_r8.find('"', pos_select_name)]
            selections[r_count]['name'] = select_name

            # 選択肢別(option)
            pos_option = t_r8.find('<option', pos_select_name, pos_end_select)
            while pos_option >= 0:
                pos_option_value = t_r8.find('value="', pos_option) + 7
                option_value = \
                    tr_r8[pos_option_value:t_r8.find('"', pos_option_value)]
                if option_value == '' or option_value == '001/0':
                    # 選択肢でないものは無視
                    pos_option = \
                        t_r8.find('<option', pos_option_value, pos_end_select)
                    continue
                selections[r_count].setdefault('value', [])\
                    .append(option_value)
                pos_option_txt = t_r8.find('>', pos_option_value) + 1
                option_txt = \
                    tr_r8[pos_option_txt:t_r8.find('</option>',
                                                   pos_option_txt)]
                selections[r_count].setdefault('text', []).append(option_txt)

                pos_option = \
                    t_r8.find('<option', pos_option_txt, pos_end_select)

            # 選択肢があるか確認
            if is_first:
                len_select = len(selections[r_count]['text'])
                if len_select > 1:
                    print()
                    for i, txt in enumerate(selections[r_count]['text']):
                        decode_txt = unescape(txt).replace('&nbsp;', ' ')
                        print('    ' + str(i + 1) + ': ' + decode_txt)
                    print()
                    ans_r8.append(int(input('応募する 【' +
                                            selections[r_count]['title'] +
                                            '】 を選択してください(1～' +
                                            str(len_select) + '): ').strip()))
                    # 入力チェック
                    if ans_r8[-1] < 1 or ans_r8[-1] > len_select:
                        print('1～' + str(len_select) + 'の数値を入力してください')
                        exit(1)
                else:
                    decode_title = unescape(selections[r_count]['title'])\
                        .replace('&nbsp;', ' ')
                    decode_txt = unescape(selections[r_count]['text'][0])\
                        .replace('&nbsp;', ' ')
                    print('    ' + decode_title + ' :' + decode_txt)
                    ans_r8.append(1)
                ans_r8[-1] -= 1
            payload[selections[r_count]['name']] = \
                selections[r_count]['value'][ans_r8[r_count]]

            r_count += 1
            pos_select = t_r8.find('<select', pos_select_name, pos_end_tr)

        pos_tr = t_r8.find('<tr>', pos_end_tr, pos_end_table) + 4

    # hidden inputを取得(POSTするデータの取得)
    payload.update(gethidden(tr_r8))

    # 送信先ページのURL,POSTデータを取得
    pos_enter_btn = tr_r8.find('class="enter-bt"')
    pos_enter_data = tr_r8.find('sChangeURL(', pos_enter_btn)
    pos_enter_data = t_r8.find('\'', pos_enter_data) + 1
    enter_data = tr_r8[pos_enter_data:t_r8.find('\'', pos_enter_data)]
    pos_enter_page_url = t_r8.find('\'http', pos_enter_data) + 1
    enter_page_url = \
        tr_r8[pos_enter_page_url:t_r8.find('\'', pos_enter_page_url)]

    # POSTデータを入れ替え
    payload.pop('uji.anchorVerb')
    payload[enter_data] = ''
    # 情報入力ページへ
    while True:
        r9 = s.post(enter_page_url, headers=header, data=payload)
        if errchk(r9):
            # エラーがなければ抜ける
            break

    sleep(3 + uniform(0, 2))

    tr_r9 = r9.text
    t_r9 = tr_r9.lower()

    # キービジュアルの出力
    pos_title = tr_r9.find('id="title"')
    pos_title = t_r9.find('<h1', pos_title)
    pos_title = t_r9.find('>', pos_title) + 1
    title = tr_r9[pos_title:t_r9.find('<', pos_title)]
    print_kv(title, 3)

    payload = {}
    # [{'name': '', 'value': [], 'text': [], 'sp': [bool, ]}, ...]
    selections = []
    # ラジオボタンを検索
    pos_radio = t_r9.find('type="radio"')
    while pos_radio >= 0:
        pos_radio_name = t_r9.find('name="', pos_radio) + 6
        radio_name = tr_r9[pos_radio_name:t_r9.find('"', pos_radio_name)]
        # selectionsのnameにあるか確認
        if radio_name not in [d.get('name') for d in selections]:
            selections.append({'name': radio_name})
            # selectionsの操作対象インデックス
            s_index = [d.get('name') for d in selections].index(radio_name)
            # 選択する物のタイトル取得
            if s_index == 0:
                # 1つ目のやつ
                pos_title = tr_r9.find('class="table-headline"')
            else:
                # 2つ目以降のやつ
                pos_title = tr_r9.find('class="table-headline"', pos_title)
            pos_title = t_r9.find('<span>', pos_title) + 6
            selections[s_index]['title'] = \
                tr_r9[pos_title:t_r9.find('</span>', pos_title)]

        # value取り出し
        pos_radio_value = t_r9.find('value="', pos_radio_name) + 7
        radio_value = tr_r9[pos_radio_value:t_r9.find('"', pos_radio_value)]
        selections[s_index].setdefault('value', []).append(radio_value)
        # 特殊フラグ
        selections[s_index].setdefault('sp', []).append(False)
        # text取り出し
        pos_radio_label = t_r9.find('<label', pos_radio_value)
        pos_radio_txt = t_r9.find('>', pos_radio_label) + 1
        radio_txt_raw = \
            unescape(tr_r9[pos_radio_txt:t_r9.find('</label>', pos_radio_txt)])
        radio_txt = unescape(radio_txt_raw).replace('&yen;', '\\')
        # spanタグが含まれているか
        if radio_txt_raw.find('</span>') >= 0:
            # styleのdisplayが含まれているか
            if radio_txt.find('display') >= 0:
                l_txt = []
                # 1項目ずつ取り出し
                if radio_txt[-7:] != '</span>':
                    selections[s_index]['sp'][len(
                        selections[s_index]['sp']) - 1] = True
                    pos_conv_txt_end = radio_txt.rfind('">') + 2
                else:
                    pos_conv_txt_end = 1
                pos_conv_txt = radio_txt.find('">') + 2
                while pos_conv_txt != pos_conv_txt_end and pos_conv_txt >= 2:
                    l_txt.append(radio_txt[
                        pos_conv_txt:radio_txt.find('<', pos_conv_txt)])
                    pos_conv_txt = radio_txt.find('">', pos_conv_txt) + 2
                if radio_txt[-7:] != '</span>':
                    # 最後の部分だけ加工
                    pos_start = radio_txt.rfind('>', 0, pos_conv_txt - 1) + 1
                    txt = untag(radio_txt[pos_start:])
                    l_txt.append(txt)
                radio_txt = l_txt
            else:
                selections[s_index]['sp'][len(
                    selections[s_index]['sp']) - 1] = True
                # タグの除去
                radio_txt = untag(radio_txt)
        selections[s_index].setdefault('text', []).append(radio_txt)

        # 次のラジオボタンを検索
        pos_radio = t_r9.find('type="radio"', pos_radio_txt)

    if is_first:
        ans_r9 = []
        print('現在このスクリプトはコンビニ支払い/コンビニ受け取りのみ対応しています')
        print('コンビニはファミマ/セブンどちらでも可')
    # [bool, 'コンビニ名頭4文字']
    conv_select = [False, '']
    # 指定項目分ループ
    for row, select in enumerate(selections):
        if is_first:
            # 選択肢があるか確認
            len_select = len(select['text'])
            if len_select > 1:
                print()
                for i, txt in enumerate(select['text']):
                    # 前の選択によって変わる場合(listの時)
                    if type(txt) is list:
                        if conv_select[0]:
                            bld_txt = \
                                [s for s in txt if conv_select[1] in s][0]
                        else:
                            bld_txt = txt[0]
                        txt = bld_txt + txt[len(txt) - 1]
                    print('    ' + str(i + 1) + ': ' + str(txt))
                print()
                ans_r9.append(int(input('【' + select['title'] +
                                        '】を選択してください(1～' +
                                        str(len_select) + '): ').strip()))
                # 入力チェック
                if ans_r9[-1] < 1 or ans_r9[-1] > len_select:
                    print('1～' + str(len_select) + 'の数値を入力してください')
                    exit(1)
            else:
                print('    ' + select['title'] + ' :' + str(select['text'][0]))
                ans_r9.append(1)
            ans_r9[-1] -= 1
        payload[select['name']] = select['value'][ans_r9[row]]
        # コンビニ受取の場合、表示変更用
        if select['sp'][ans_r9[row]] and \
                type(select['text'][ans_r9[row]] is str):
            conv_select = [True, select['text'][ans_r9[row]][:4]]

    # hidden inputを取得(POSTするデータの取得)
    payload.update(gethidden(tr_r9))

    # 送信先ページPOSTデータを取得
    pos_enter_btn = tr_r9.find('class="enter-bt"')
    pos_enter_data = tr_r9.find('getToken(\'', pos_enter_btn) + 10
    enter_data = tr_r9[pos_enter_data:t_r9.find('\'', pos_enter_data)]

    # POSTデータを入れ替え
    payload.pop('uji.anchorVerb')
    payload[enter_data] = ''
    # 確認ページへ
    while True:
        r10 = s.post(r9.url, headers=header, data=payload)
        if errchk(r10):
            # エラーがなければ抜ける
            break

    tr_r10 = r10.text
    t_r10 = tr_r10.lower()
    # リダイレクトURLの取得
    pos_re_url = tr_r10.find('id="instruction-text"')
    pos_re_url = t_r10.find('href="', pos_re_url) + 6
    re_url = tr_r10[pos_re_url:t_r10.find('"', pos_re_url)]
    # リダイレクト
    while True:
        r11 = s.get(re_url, headers=header)
        if errchk(r11):
            # エラーがなければ抜ける
            break

    tr_r11 = r11.text
    t_r11 = tr_r11.lower()
    title_r11 = get_title(tr_r11)
    print_kv(title_r11, 2.5)

    sleep(3 + uniform(0, 2))
    payload = {}

    # 確認項目の取得
    pos_table_head = tr_r11.find('class="table-headline"')
    while pos_table_head >= 0:
        pos_end_table = t_r11.find('</table>', pos_table_head)
        # breakdownクラスは無視
        pos_class = tr_r11.rfind('class="', 0, pos_table_head)
        if t_r11.find('breakdown', pos_class, pos_table_head) >= 0:
            pos_table_head = \
                t_r11.find('class="table-headline"', pos_end_table)
            continue
        pos_title = t_r11.find('<span>', pos_table_head) + 6
        title = tr_r11[pos_title:t_r11.find('</', pos_title)]
        print(title)

        # 行(tr)ごとにループ
        pos_tr = t_r11.find('<tr>', pos_title, pos_end_table)
        while pos_tr >= 0:
            # th, td内の文字を取得
            pos_th = t_r11.find('<th>', pos_tr) + 4
            head = tr_r11[pos_th:t_r11.find('</th>', pos_th)]
            print('    ' + head + ': ', end='')
            pos_td = t_r11.find('<td>', pos_th) + 4
            txt = tr_r11[pos_td:t_r11.find('</td>', pos_td)]
            # strongタグがあるか確認
            pos_strong = txt.find('<strong>') + 8
            if pos_strong >= 8:
                # あった場合、strongタグ内の文字だけ取得
                txt = txt[pos_strong:txt.find('</', pos_strong)]
            print(untag(txt))

            pos_tr = t_r11.find('<tr>', pos_td, pos_end_table)

        pos_table_head = tr_r11.find('class="table-headline"', pos_end_table)

    if is_first:
        ans_r11 = []
    # 質問項目の確認
    pos_enq = tr_r11.find('class="enq-info"')
    if pos_enq >= 0:
        pos_end_enq = t_r11.find('</div', pos_enq)
        pos_field = t_r11.find('<fieldset>', pos_enq)
        r_count = 0
        # 質問項目ごとにループ
        while pos_field >= 0:
            question = {'name': '', 'value': [], 'max': -1}
            pos_end_field = t_r11.find('</fieldset', pos_field)
            if is_first:
                # 質問タイトル
                pos_strong = t_r11.find('<strong>', pos_field) + 8
                pos_end_strong = t_r11.find('</strong', pos_strong)
                print('\n' + tr_r11[pos_strong:pos_end_strong])
                # 質問文
                pos_q = pos_end_strong + 9
                pos_end_q = t_r11.find('</legend', pos_end_strong)
                q = untag(tr_r11[pos_q:pos_end_q])
                print('  ' + q + '\n')
            pos_table = t_r11.find('<table', pos_field)
            pos_end_table = t_r11.find('</table', pos_table)
            pos_td = t_r11.find('<td>', pos_table, pos_end_table) + 4
            # 選択肢分ループ
            while pos_td >= 4:
                pos_end_td = t_r11.find('</td>', pos_td)
                pos_input = t_r11.find('input', pos_td, pos_end_td)
                if pos_input >= 0:
                    pos_in_type = t_r11.find('type="', pos_input) + 6
                    in_type = t_r11[pos_in_type:t_r11.find('"', pos_in_type)]
                    # name属性
                    pos_name = t_r11.find('name="', pos_input) + 6
                    question['name'] = t_r11[
                        pos_name:t_r11.find('"', pos_name)]
                    # value属性
                    pos_value = t_r11.find('value="', pos_input) + 7
                    question['value'].append(
                        t_r11[pos_value:t_r11.find('"', pos_value)])
                    pos_txt = t_r11.find('>', pos_input) + 1

                    if is_first and in_type == 'radio':
                        # input type=radio
                        print('    ' + str(len(question['value'])) + ': ' +
                              tr_r11[pos_txt:t_r11.find(
                                  '</', pos_txt)].strip())
                    elif in_type == 'text':
                        # input type=text
                        pos_max = t_r11.find('maxlength="', pos_input) + 11
                        if pos_max >= 11:
                            question['max'] = \
                                int(tr_r11[pos_max:t_r11.find('"', pos_max)])
                else:
                    # inputがない
                    if is_first:
                        print('    ' + tr_r11[pos_td:pos_end_td].strip())

                pos_td = t_r11.find('<td>', pos_td, pos_end_table) + 4

            if is_first:
                print()
                if in_type == 'radio':
                    # input type=radio
                    len_q = len(question['value'])
                    ans_r11.append(int(input('回答を選択してください(1～' +
                                             str(len_q) + '): ')))
                    # 入力チェック
                    if ans_r11[-1] < 1 or ans_r11[-1] > len_q:
                        print('1～' + str(len_q) + 'の数値を入力してください')
                        exit(1)
                    ans_r11[-1] -= 1
                elif in_type == 'text':
                    # input type=text
                    if question['max'] >= 0:
                        ans_r11.append(input('回答を入力してください(' +
                                             str(question['max']) + '文字以下): '))
                        # 入力チェック
                        if len(ans_r11[-1]) > question['max']:
                            print(question['max'] + '文字以下で入力してください')
                            exit(1)
                    else:
                        ans_r11.append(input('回答を入力してください: '))
                    question['value'] = [ans_r11[-1]]
                    ans_r11[-1] = 0

            # POSTデータへ追加
            payload[question['name']] = question['value'][ans_r11[r_count]]\
                .encode(encoding='shift-jis')
            r_count += 1

            pos_field = t_r11.find('<fieldset>', pos_end_field)

    # hidden inputを取得(POSTするデータの取得)
    payload.update(gethidden(tr_r11))

    # 送信先ページのURL,POSTデータを取得
    pos_enter_btn = tr_r11.find('class="enter-bt"')
    pos_enter_data = tr_r11.find('sChangeURL(', pos_enter_btn)
    pos_enter_data = t_r11.find('\'', pos_enter_data) + 1
    enter_data = tr_r11[pos_enter_data:t_r11.find('\'', pos_enter_data)]
    pos_enter_page_url = t_r11.find('\'http', pos_enter_data) + 1
    enter_page_url = \
        tr_r11[pos_enter_page_url:t_r11.find('\'', pos_enter_page_url)]

    # POSTデータを入れ替え
    payload.pop('uji.anchorVerb')
    payload[enter_data] = ''

    # js部分の動作
    pos_if = tr_r11.find('if("' + enter_data + '" ==')
    if pos_if >= 0:
        pos_line = t_r11.find('{', pos_if)
        pos_end_if = t_r11.find('}', pos_line)
        pos_end_line = t_r11.find(';', pos_if, pos_end_if) + 1
        js = {}
        # 行ごとにループ
        while pos_end_line >= 1:
            pos_entry = t_r11.find('["', pos_line, pos_end_line) + 2
            if pos_entry >= 2:
                pos_end_entry = t_r11.find('"]', pos_entry)
                entry = tr_r11[pos_entry:pos_end_entry]
                pos_attr = t_r11.find('.', pos_end_entry) + 1
                pos_end_attr = t_r11.find('=', pos_attr)
                attr = tr_r11[pos_attr:pos_end_attr]
                pos_data = t_r11.find('"', pos_end_attr) + 1
                data = tr_r11[pos_data:t_r11.find('"', pos_data)]

                # 既存のpayloadを変更
                if entry in payload:
                    payload.pop(entry)
                js.setdefault(attr, []).append(data)

            pos_line = pos_end_line
            pos_end_line = t_r11.find(';', pos_end_line, pos_end_if) + 1

        payload.update(dict(zip(js['name'], js['value'])))

    # 最終確認
    if is_first:
        print('\n\n以上の内容で申し込みます')
        ans = input('よろしいですか？(y/n): ').lower()
        print()
        if ans != 'y':
            print('中止します')
            print('申し込み処理はしていません')
            exit(1)

    # 申し込み
    r12 = s.post(enter_page_url, headers=header, data=payload)
    if r12.status_code >= 400:
        # エラー発生
        print('申し込み時にエラーが発生しました')
        print('処理を中断します')
        break

    title_r12 = get_title(r12.text)
    # 前ページと同じか確認
    if title_r11 == title_r12:
        print('申し込みに失敗しました')
        break
    print_kv(title_r12, 2.5)
    print('申し込みました!')
    success.append(serial)

    try:
        # 必要なcookieだけ取り出し
        kojin = s.cookies.pop('KOJIN_SHIKIBETSU')
        # cookie削除
        s.cookies.clear()
        # cookieを戻す
        pos_domain = r1.url.find('://') + 3
        domain = r1.url[pos_domain:r1.url.find('/', pos_domain)]
        cookie_kojin = requests.cookies.create_cookie(domain=domain,
                                                      name='KOJIN_SHIKIBETSU',
                                                      value=kojin)
        s.cookies.set_cookie(cookie_kojin)
    except KeyError:
        # KOJIN_SHIKIBETSUがない
        s.cookies.clear()

    # 初回フラグを無効化
    is_first = False

l_srl = len(l_serial)
l_suc = len(success)
if l_srl == l_suc:
    # 正常終了時
    print('\n  全てのシリアルの応募が完了しました!')
    exit(0)

# break及び一部シリアルの応募に失敗した際の処理
print('\n  ' + str(l_srl) + '個中 ' + str(l_suc) + '個のシリアル応募が完了しました')
print('応募できたシリアル:')
for s in success:
    print('    ' + str(l_serial.index(s) + 1) + ': ' + s)
exit(1)
