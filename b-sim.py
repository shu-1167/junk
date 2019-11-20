import requests
# no module named 'requests' が出たら pip install requests
# import os

# プロキシの設定
# os.environ['http_proxy'] = 'http://127.0.0.1:8888'
# ログイン用メールアドレス
mailaddr = 'xxx@xxx.xx'
# ログイン用パスワード
password = 'xxxx'

s = requests.session()
r = s.get('http://2019.b-sim.net/shop')
# ログイン用トークンの抽出
token = r.text.find('hidden\" value=\"') + 15
token = r.text[token:r.text.find('\"', token)]

# ログイン時にPOSTするデータ
payload = {'_token': token, 'mail': mailaddr, 'password': password}
s.post('http://2019.b-sim.net/shop/login', data=payload)

# 在庫管理画面
r1 = s.get('http://2019.b-sim.net/shop/item/stock')
tr_pos = r1.text.find('</tr>')
# 売値の位置
price_pos = r1.text.find('right\">', tr_pos) + 7
# データが無くなるまでループ
while price_pos > 6:
    # 陳列数の位置
    num1_pos = r1.text.find('right\">', price_pos) + 7
    # 陳列数の抽出
    num1 = r1.text[num1_pos:r1.text.find('<', num1_pos)]
    # 在庫数の位置
    num2_pos = r1.text.find('right\">', num1_pos) + 7
    # 在庫数の抽出
    num2 = r1.text[num2_pos:r1.text.find('<', num2_pos)]
    if int(num1) < int(num2):
        # 商品編集URLの位置
        url_pos = r1.text.find('href=\"', num2_pos) + 6
        # 商品編集URLの抽出
        url = r1.text[url_pos:r1.text.find('\">', url_pos)]
        r2 = s.get(url)

        # URLから商品ID取得
        id = url[url.rfind('/') + 1:]
        # トークン取得
        token = r2.text.find('hidden\" value=\"') + 15
        token = r2.text[token:r2.text.find('\">', token)]
        # 商品名取得
        name = r2.text.find('name=\"name\"')
        name = r2.text.find('value=\"', name) + 7
        name = r2.text[name:r2.text.find('\">', name)]
        # 売値取得
        price = r1.text[price_pos:r1.text.find('<', price_pos)]
        # カテゴリ取得
        category_id = r2.text.find('name=\"category_id\"')
        category_id = r2.text.find('\" selected=\"selected\"', category_id)
        category_id = r2.text[category_id - 1:category_id]

        print('在庫ID:' + id + "  " + name)
        print(num1 + ' => ' + num2)

        # POSTする更新データ
        payload = {'_method': 'PUT',
                   '_token': token,
                   'id': id, 'name': name,
                   'price': price,
                   'show': num2,
                   'category_id': category_id,
                   'hold': 0}

        # 商品データ更新
        r3 = s.post('http://2019.b-sim.net/shop/item/stock/update',
                    data=payload)
        print(r3.reason + '\n')

    tr_pos = r1.text.find('</tr>', num2_pos)
    # 次の売値の位置。無い場合は-1+7=6が入る
    price_pos = r1.text.find('right\">', tr_pos) + 7
