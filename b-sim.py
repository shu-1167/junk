from requests import Session
# no module named 'requests' が出たら pip install requests
from argparse import ArgumentParser
# import os

# プロキシの設定
# os.environ['http_proxy'] = 'http://127.0.0.1:8888'
# ログイン用メールアドレス
MAILADDR = 'xxx@xxx.xx'
# ログイン用パスワード
PASSWORD = 'xxxx'
# URLの頭部分
URL = 'http://example.net/'

# オプション引数を受け取る
# 指定しなかった場合、-sと-dどちらも指定した状態(全ての機能)になります
parser = ArgumentParser()
# -d 陳列されていない商品を商品陳列する(ついでに保留解除もします)
parser.add_argument('-d', '--display', action='store_true',
                    help='display products that are not displayed')
# -s 商品を入荷します(確認のプロンプトが出ます)
parser.add_argument('-s', '--stock', action='store_true',
                    help='purchasing products')
# -y -s指定時の確認のプロンプトをスルーして入荷します
# 非推奨ですが自動化したい際などにはご利用ください
parser.add_argument('-y', action='store_true',
                    help='(not recommend) with -s, assume that the answer \
                    tos yes/no questions is \'yes\'')
args = parser.parse_args()

# 引数による処理分岐のフラグ作成
# 変数の初期化
should_display = False
should_stock = False
if args.display:
    # 陳列する
    should_display = True
if args.stock:
    # 入荷する
    should_stock = True
if not args.display and not args.stock:
    # 引数無指定時、-d,-sどちらのオプションも処理
    should_display = True
    should_stock = True
if not args.stock and args.y:
    # -sオプション無指定時に-yオプションがある場合、エラー
    parser.error('you can\'t specify \'-y\' without specifying option \'-s\'')
s = Session()
r = s.get(URL + 'shop')
# ログイン用トークンの抽出
token = r.text.find('hidden\" value=\"') + 15
token = r.text[token:r.text.find('\"', token)]

# ログイン時にPOSTするデータ
payload = {'_token': token, 'mail': MAILADDR, 'password': PASSWORD}
r = s.post(URL + 'shop/login', data=payload)

if r.url != URL + 'shop/main':
    # ログインできなかった
    print('ログインに失敗しました')
    print('ファイル内のメールアドレス及びパスワードを確認してください')
    quit(-1)

# 在庫管理画面
r1 = s.get(URL + 'shop/item/stock')
if should_display:
    tr_pos = r1.text.find('</tr>')
    # 売値の位置
    price_pos = r1.text.find('right\">', tr_pos) + 7
    # 陳列処理
    # データが無くなるまでループ
    while price_pos > 6:
        # 在庫IDの位置
        ident_pos = r1.text.find('<td>', tr_pos) + 4
        # 在庫IDの抽出
        ident = r1.text[ident_pos:r1.text.find('<', ident_pos)]
        # 陳列数の位置
        num1_pos = r1.text.find('right\">', price_pos) + 7
        # 陳列数の抽出
        num1 = r1.text[num1_pos:r1.text.find('<', num1_pos)]
        # 在庫数の位置
        num2_pos = r1.text.find('right\">', num1_pos) + 7
        # 在庫数の抽出
        num2 = r1.text[num2_pos:r1.text.find('<', num2_pos)]
        if int(num1) < int(num2):
            # 陳列数が在庫数より少ない場合、陳列する
            # 商品編集URLの位置
            url_pos = r1.text.find('href=\"', num2_pos) + 6
            # 商品編集URLの抽出
            url = r1.text[url_pos:r1.text.find('\">', url_pos)]
            r2 = s.get(url)

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

            print('在庫ID:' + ident + "  " + name)
            print(num1 + ' => ' + num2)

            # POSTする更新データ
            payload['_method'] = 'PUT'
            payload['_token'] = token
            payload['id'] = ident
            payload['name'] = name
            payload['price'] = price
            payload['show'] = num2
            payload['category_id'] = category_id
            payload['hold'] = 0

            # 商品データ更新
            r2 = s.post(URL + 'shop/item/stock/update',
                        data=payload)
            print(r2.reason + '\n')

        tr_pos = r1.text.find('</tr>', num2_pos)
        # 次の売値の位置。無い場合は-1+7=6が入る
        price_pos = r1.text.find('right\">', tr_pos) + 7


if should_stock:
    # 入荷処理
    # 商品一覧辞書作成
    # {key:{name:商品名, stock:在庫数, target:目標数,
    #       thres:閾値, diff:差分(注文数)}}
    data = dict()
    tr_pos = r1.text.find('</tr>')
    # 売値の位置
    price_pos = r1.text.find('right\">', tr_pos) + 7
    # データが無くなるまでループ
    while price_pos > 6:
        # 売値の抽出
        price = r1.text[price_pos:r1.text.find('<', price_pos)]
        # 在庫IDの位置
        ident_pos = r1.text.find('<td>', tr_pos) + 4
        # 商品IDの位置
        ident_pos = r1.text.find('<td>', ident_pos) + 4
        # 商品IDの抽出
        ident = r1.text[ident_pos:r1.text.find('<', ident_pos)]
        # 商品名の位置
        name_pos = r1.text.find('<td>', ident_pos) + 4
        # 商品名の抽出
        name = r1.text[name_pos:r1.text.find('</td>', name_pos)]
        # 陳列数の位置
        num1_pos = r1.text.find('right\">', price_pos) + 7
        # 在庫数の位置
        num2_pos = r1.text.find('right\">', num1_pos) + 7
        # 在庫数の抽出
        num2 = r1.text[num2_pos:r1.text.find('<', num2_pos)]
        # 辞書に商品を追加
        data[ident] = dict()
        data[ident]['stock'] = int(num2)
        data[ident]['name'] = name
        # 売値を卸値に変換
        price = int(price) // 2
        # 卸値に応じて目標数と閾値を設定
        if price <= 5000:
            # 5000円以下
            # 閾値(これ以下になったら注文する)
            data[ident]['thres'] = 6
            # 目標値(この数になるように注文する)
            data[ident]['target'] = 12
        elif price <= 10000:
            # 10000円以下
            data[ident]['thres'] = 4
            data[ident]['target'] = 8
        elif price <= 20000:
            # 20000円以下
            data[ident]['thres'] = 3
            data[ident]['target'] = 5
        elif price > 20000:
            # 20001円以上
            data[ident]['thres'] = 2
            data[ident]['target'] = 4

        tr_pos = r1.text.find('</tr>', num2_pos)
        # 次の売値の位置。無い場合は-1+7=6が入る
        price_pos = r1.text.find('right\">', tr_pos) + 7

    # 注文履歴を取得
    r1 = s.get(URL + 'shop/item/order/details')
    tr1_pos = r1.text.find('</tr>')
    # 注文履歴詳細ページのURLの位置
    href_pos = r1.text.find('href=\"', tr1_pos) + 6
    # 注文履歴データが無くなるまでループ
    while href_pos > 5:
        # 状態の前、注文内容の最後の位置
        a_pos = r1.text.find('</a>', href_pos)
        # 状態の始端位置
        start_status_pos = r1.text.find('center\">', a_pos) + 8
        # 状態の終端位置
        stop_status_pos = r1.text.find('</td>', start_status_pos)
        if '入荷済み' not in r1.text[start_status_pos:stop_status_pos]:
            # 入荷済みじゃない時の処理
            # 注文履歴詳細ページのURLの抽出
            url = r1.text[href_pos:r1.text.find('\">', href_pos)]
            r2 = s.get(url)

            # 一つ目のテーブル終端の位置
            thead_pos = r2.text.find('</thead>')
            tr2_pos = r2.text.find('</tr>', thead_pos)
            # 商品IDの位置
            ident_pos = r2.text.find('center\">', tr2_pos) + 8
            # 商品データが無くなるまでループ
            while ident_pos > 7:
                # 商品IDの抽出
                ident = r2.text[ident_pos:r2.text.find('<', ident_pos)]
                # 卸価格の終端(なぜか卸価格だけdivで囲まれてるのを利用)
                price_pos = r2.text.find('</div>', ident_pos)
                # 数量の位置
                quantity_pos = r2.text.find('right\">', price_pos) + 7
                # 数量の抽出
                quantity = r2.text[quantity_pos:
                                   r2.text.find('<', quantity_pos)]

                # dataに入荷予定数を追加
                data[ident]['stock'] += int(quantity)

                tr2_pos = r2.text.find('</tr>', quantity_pos)
                # 次の商品IDの位置。無い場合は-1+8=7が入る
                ident_pos = r2.text.find('center\">', tr2_pos) + 8

        tr1_pos = r1.text.find('</tr>', stop_status_pos)
        # 次のURLの位置。無い場合は-1+6=5が入る
        href_pos = r1.text.find('href=\"', tr1_pos) + 6

    payload = dict()
    payload['_token'] = token
    payload['id[]'] = list()
    payload['num[]'] = list()
    # 商品の種類分ループ
    for key in data.keys():
        # 目標値と在庫の差分を計算
        data[key]['diff'] = data[key]['target'] - data[key]['stock']
        if data[key]['stock'] <= data[key]['thres']:
            payload['id[]'].append(int(key))
            payload['num[]'].append(data[key]['diff'])

    if len(payload['id[]']) <= 0:
        # payloadが空(注文する商品がない)場合、終了
        print('仕入れが必要な商品がありません')
        quit()

    # カートに入れる
    s.post(URL + 'shop/item/order/add', data=payload)
    while True:
        # 編集処理用の無限ループ
        # 清算ポチ1回目
        r1 = s.post(URL + 'shop/item/order/confirm', data=payload)

        print('\n以下の商品を注文します\n')
        print(' 商品ID | 注文数 |\t小計\t|\t商品名')
        print('--------+--------+--------------+-----------------------------')

        tr_pos = r1.text.find('</tr>')
        # 番号の位置
        num_pos = r1.text.find('<td>', tr_pos) + 4
        # 商品データが無くなるまでループ
        while num_pos > 3:
            # 番号の抽出
            num = r1.text[num_pos:r1.text.find('<', num_pos)]
            # なぜか応答の番号は+1されてるため、-1する
            num = str(int(num) - 1)
            # 単価の位置
            price_pos = r1.text.find('right\">', num_pos) + 7
            # 数量の位置
            order_pos = r1.text.find('right\">', price_pos) + 7
            # 数量の抽出
            order = r1.text[order_pos:r1.text.find('<', order_pos)]
            # 小計の位置
            sub_pos = r1.text.find('right\">', order_pos) + 7
            # 小計の抽出
            sub = r1.text[sub_pos:r1.text.find('<', sub_pos)]

            # 送信時と応答時の数量が一致しているか
            if data[num]['diff'] == int(order):
                # 確認出力
                print('  ' + num + '\t|   ' + order +
                      '\t |   ' + sub + '\t|  ' + data[num]['name'])
            else:
                # 一致しなかった。仕様変更orバグの可能性あり
                print('\n注文時と確認応答の数量が一致していない商品がありました')
                print('完全性維持のため、処理を中止します')
                print('注文処理はされていません')
                quit(-1)

            tr_pos = r1.text.find('</tr>', sub_pos)
            # 次の番号の位置。無い場合は-1+4=3が入る
            num_pos = r1.text.find('<td>', tr_pos) + 4

        print('--------------------------------------------------------------')
        # 商品代金小計の位置
        sub_pos = r1.text.find('right\">', tr_pos) + 7
        # 商品代金小計の抽出
        sub = r1.text[sub_pos:r1.text.find('<', sub_pos)]
        sub = sub[sub.find('：') + 1:]
        # 送料の位置
        ship_pos = r1.text.find('right\">', sub_pos) + 7
        # 送料の抽出
        ship = r1.text[ship_pos:r1.text.find('<', ship_pos)]
        ship = ship[ship.find('：') + 1:]
        # 合計金額の位置
        total_pos = r1.text.find('right\">', ship_pos) + 7
        # 合計金額の抽出
        total = r1.text[total_pos:r1.text.find('<', total_pos)]
        total = total[total.find('：') + 1:]

        # 金額の表示
        print('商品代金小計：\t' + sub)
        print('送料：\t\t' + ship)
        print('---------------------------------')
        print('合計金額：\t' + total)
        # 確認の入力
        if not args.y:
            # 引数-yが指定されていない場合
            # y/nの入力
            ans = input('続行しますか？ [e/Y/n] ')

            if ans.strip().lower() == "y":
                # 'Y'or'y'の場合、続行
                break
            elif ans.strip().lower() == "e":
                # 'E'or'e'の場合、編集
                product_id = input('商品ID: ').strip()
                count = input('個数:').strip()
                # 入力された値が数値か
                if not product_id.isdecimal() or not count.isdecimal():
                    print("数字のみ入力可能です")
                    continue
                # 在庫管理にある商品か
                try:
                    data[product_id]
                except KeyError:
                    # ない商品が選ばれた
                    print('在庫管理画面に無い商品が指定されました')
                    print('変更はありません')
                    continue
                # 変更する必要があるか
                # 数量の変更があるか or 数量が同じでもpayloadにあるか
                if data[product_id]['diff'] != int(count) or \
                   product_id not in payload['id[]']:
                    # 編集する商品一覧
                    if 'edit_dict' not in locals():
                        # 無ければ作成
                        edit_dict = dict()
                    edit_dict[product_id] = int(count)
                    if int(count) <= 0 and \
                       int(product_id) not in payload['id[]']:
                        # 無い商品を0個以下にしようとした場合、何もしない
                        continue
                    # payloadを再構築
                    new_payload = dict()
                    new_payload['id[]'] = list()
                    new_payload['num[]'] = list()

                    for key in data.keys():
                        # keyが編集する商品一覧にあるか
                        if key in edit_dict:
                            if key != product_id and edit_dict[key] <= 0:
                                # 削除済みの商品の場合、edit_dictからも削除
                                del edit_dict[key]
                            else:
                                # 変更する商品
                                new_payload['id[]'].append(int(key))
                                new_payload['num[]'].append(edit_dict[key])
                                data[key]['diff'] = edit_dict[key]
                        elif data[key]['diff'] >= data[key]['thres']:
                            # 通常通り追加する商品
                            new_payload['id[]'].append(int(key))
                            new_payload['num[]'].append(data[key]['diff'])

                    # カート用payload(新規追加の場合、カートから処理必要)
                    cart_payload = dict()
                    cart_payload['_token'] = token
                    cart_payload['id[]'] = list()
                    cart_payload['num[]'] = list()
                    # 以前のpayloadにデータがあるか確認
                    for key, value in edit_dict.items():
                        if key not in payload:
                            # 無かった場合、カートに追加
                            cart_payload['id[]'].append(int(key))
                            cart_payload['num[]'].append(value)
                    if len(cart_payload['id[]']) > 0:
                        # カート内に商品がある場合、送信
                        s.post(URL + 'shop/item/order/add', data=cart_payload)
                    payload['id[]'] = new_payload['id[]']
                    payload['num[]'] = new_payload['num[]']
                continue
            else:
                # 'Y'or'y'以外が入力された場合、終了
                print('中断しました。')
                quit()
        else:
            break

    # 以下注文処理の関係上、デバッグできてません
    # Y/yの場合、注文(清算ポチ2回目)
    r1 = s.post(URL + 'shop/item/order/settle', data={'_token': token})
    if r1.ok:
        print('注文しました!')
    else:
        print('注文に失敗した可能性があります。確認してください。')
