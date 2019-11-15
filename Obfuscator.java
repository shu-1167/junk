
import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// ファイル内にかっこ"()"があれば、setlocal enabledelayedexpansionをするようにする
// かっこ内は!を使うようにする。広めスコープの変数に!か%入れるようにして、付与時にそこから拾えばいい？
public class Obfuscator {

    // 変数名用文字群
    static StringBuilder var_chars = new StringBuilder();
    // bat用変数Map
    static Map<String, String> var = new HashMap<>();
    // 変数を囲む文字(%か!)
    static String enclose = "%";

    public static void main(String[] args) {
        // StringBuilderで組み立てる
        StringBuilder cmd = new StringBuilder();
        // cmd.append("@echo off\r\n");
        // bat変数構成用文字列
        var_chars.append("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789[]{}");
        // あ?んの文字を追加
        // "ぁ"の文字コードが入る(デフォはUTF-8)
        byte[] b = "ぁ".getBytes();
        // "み"までループ("む"は飛んでる)
        for (int i = 0; i <= 62; i++) {
            var_chars.append(new String(b));
            b[2]++;
        }
        // "む"の文字コード
        b = "む".getBytes();
        // "ん"までループ
        for (int i = 0; i < 20; i++) {
            var_chars.append(new String(b));
            b[2]++;
        }

        // set のパターンを8パターン作る。=はオマケ
        String[] pattern = {"s", "e", "t", " ", "et ", "se", "t ", "et", "set", "set ", "="};
        List<String> set_pattern = new ArrayList<>(Arrays.asList(pattern));
        // 順番をランダム化
        Collections.shuffle(set_pattern, new SecureRandom());
        // 変数化したsetコマンドが入る。初期値は変数化していないsetコマンド
        String value = "set ";
        for (String s : set_pattern) {
            set_var(s);
            cmd.append(value)
                    .append(var.get(s));
            // "="が変数化されているか
            if (var.containsKey("=") && !s.equals("=")) {
                cmd.append(castle_letter("="));
            } else {
                cmd.append("=");
            }
            cmd.append(s)
                    .append("\r\n");
            value = create_set();
        }

        // batファイルを開く
        try (BufferedReader br = Files.newBufferedReader(Paths.get("Elevate.bat"), Charset.forName("Shift_JIS"))) {
            String text;
            // 1行ずつ抽出
            while ((text = br.readLine()) != null) {
                // @echo offではなく、空行でもなく、rem(コメント)でもない、
                // 要するに実行するコマンドの場合
                if (!text.equals("@echo off") && !text.equals("") && !text.substring(0, 3).toLowerCase().equals("rem")) {
                    // 実行する変数化したコマンド
                    String cmd_var = new String();
                    // 1文字ずつ抽出
                    for (String s : text.split("")) {
                        System.out.print(s);
                        // %の場合、エスケープさせる
                        if (s.equals("%")) {
                            s = s.concat("%");
                        }
                        // varに文字があるか
                        if (!var.containsKey(s)) {
                            // 無ければ追加
                            set_var(s);
                            cmd.append(set_cmd())
                                    .append(var.get(s))
                                    .append(castle_letter("="))
                                    .append(s)
                                    .append("\r\n");
                        }
                        // コマンドを生成
                        cmd_var = cmd_var.concat(castle_letter(s));
                    }
                    cmd.append(cmd_var)
                            .append("\r\n");
                    System.out.println();
                }
            }
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        System.out.println(cmd.toString());
        // ファイルへ出力
        try (FileOutputStream fos = new FileOutputStream("test.bat"); OutputStreamWriter osw = new OutputStreamWriter(fos, "Shift_JIS")) {
            osw.write(cmd.toString());
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    // ランダムな文字列を返す。bat変数用
    static String var_name() {
        SecureRandom r = new SecureRandom();
        // 文字数(ループする回数)
        int length = r.nextInt(2) + 2;
        String str = new String();
        for (int i = 0; i <= length; i++) {
            // var_charsからランダムな1文字を抽出
            char c = var_chars.charAt(r.nextInt(var_chars.length()));
            // strに連結
            str = str.concat(String.valueOf(c));
            if (i == 0 && Character.isDigit(str.charAt(0))) {
                // １文字目が数値の場合、やり直し
                i--;
                str = new String();
            }
        }

        // 生成したランダムな文字列を返す
        return str;
    }

    // 引数の文字をbat用変数に割り当てる
    static void set_var(String key) {
        // 既に割り当て済みの場合、return
        if (var.containsKey(key)) {
            System.out.println("\"" + key + "\"は既に割り当て済みです");
            return;
        }

        String str = new String();
        // 重複しない文字列が得られるまでループ
        do {
            str = var_name();
        } while (var.containsValue(str));

        // 割り当て
        var.put(key, str);
    }

    // set のパターンを返す
    static String set_cmd() {
        // 文字が入ってるか確認。なければreturn
        if (!var.containsKey("set ")) {
            System.out.println("setコマンド群が初期化されていません");
            return null;
        }
        SecureRandom r = new SecureRandom();
        // ↓の8パターン
        // 1:1:1:1,1:3,1:2:1,1:1:2,2:2,2:1:1,3:1,4
        int pattern = r.nextInt(8);
        String s = new String();

        switch (pattern) {
            case 0:
                // 1:1:1:1
                s = castle_letter("s") + castle_letter("e") + castle_letter("t") + castle_letter(" ");
                break;
            case 1:
                // 1:3
                s = castle_letter("s") + castle_letter("et ");
                break;
            case 2:
                // 1:2:1
                s = castle_letter("s") + castle_letter("et") + castle_letter(" ");
                break;
            case 3:
                // 1:1:2
                s = castle_letter("s") + castle_letter("e") + castle_letter("t ");
                break;
            case 4:
                // 2:2
                s = castle_letter("se") + castle_letter("t ");
                break;
            case 5:
                // 2:1:1
                s = castle_letter("se") + castle_letter("t") + castle_letter(" ");
                break;
            case 6:
                // 3:1
                s = castle_letter("set") + castle_letter(" ");
                break;
            case 7:
                s = castle_letter("set ");
                break;
        }
        // 生成したset を返す
        return s;
    }

    // set を生成する
    static String create_set() {
        // 識別用
        String key = new String();
        // 実際にbatに出力する用(returnする)
        String value = new String();
        do {
            String tmp;
            switch (key.length()) {
                case 0:
                    tmp = find_char("s");
                    if (tmp == null) {
                        // 見つからなかった場合
                        key = key.concat("s");
                        value = value.concat("s");
                    } else {
                        // 見つかった場合
                        key = key.concat(tmp);
                        value = value.concat(castle_letter(tmp));
                    }
                    break;

                case 1:
                    tmp = find_char("e");
                    if (tmp == null) {
                        // 見つからなかった場合
                        key = key.concat("e");
                        value = value.concat("e");
                    } else {
                        // 見つかった場合
                        key = key.concat(tmp);
                        value = value.concat(castle_letter(tmp));
                    }
                    break;

                case 2:
                    tmp = find_char("t");
                    if (tmp == null) {
                        // 見つからなかった場合
                        key = key.concat("t");
                        value = value.concat("t");
                    } else {
                        // 見つかった場合
                        key = key.concat(tmp);
                        value = value.concat(castle_letter(tmp));
                    }
                    break;

                case 3:
                    tmp = find_char(" ");
                    if (tmp == null) {
                        // 見つからなかった場合
                        key = key.concat(" ");
                        value = value.concat(" ");
                    } else {
                        // 見つかった場合
                        key = key.concat(tmp);
                        value = value.concat(castle_letter(tmp));
                    }
                    break;
            }
        } while (key.length() < 4);

        // 生成した文字列を返す
        return value;
    }

    // varから特定文字を探し出し、varのkeyを返す
    static String find_char(String s) {
        String find = null;
        // varをシャッフルしたlist生成
        List<Map.Entry<String, String>> var_list = new ArrayList<>(var.entrySet());
        Collections.shuffle(var_list, new SecureRandom());
        // ループで1つずつ確認
        for (Map.Entry<String, String> entry : var_list) {
            if (entry.getKey().substring(0, 1).equals(s)) {
                // あった
                find = entry.getKey();
                break;
            }
        }

        return find;
    }

    // %or!の囲い字を付与する
    static String castle_letter(String key) {
        return enclose + var.get(key) + enclose;
    }
}
