# ポケモンGO 日本語カレンダー

ポケモンGOのイベントを日本時間・日本語でまとめた購読用カレンダーです。週1回、自動で更新されます。

## 購読URL

カレンダーは2つあります。必要なほうだけ、または両方を購読してください。

| カレンダー | 中身 | URL |
|---|---|---|
| ポケモンGO | イベント、コミュニティ・デイ、○○デイ、スポットライトアワー、レイドアワー、マックスマンデー、曜日ボーナス | `webcal://raw.githubusercontent.com/raitok0905/pogo-calendar-ja/main/pogo.ics` |
| ポケモンGO レイド | 伝説・メガ・シャドウレイドとマックスバトルのボスの入れ替わり | `webcal://raw.githubusercontent.com/raitok0905/pogo-calendar-ja/main/pogo-raids.ics` |

iPhone / Mac / iCloud.com のカレンダーで「照会カレンダー（購読カレンダー）」として追加してください。カレンダーごとに色や表示のオンオフを変えられます。

## しくみ

- `events.json`：イベントの一覧（ここを編集する）。`"calendar": "raids"` の予定はレイド用カレンダーに入る
- `build.py`：`events.json` から `pogo.ics` と `pogo-raids.ics` を作る（`python3 build.py`）

色違いの確率は攻略サイト・コミュニティの推定値で、公式発表ではありません。

情報源：ポケモンGO公式ニュース（pokemongo.com/ja/news）ほか。非公式のカレンダーです。
