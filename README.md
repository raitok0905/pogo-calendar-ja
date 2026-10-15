# ポケモンGO 日本語カレンダー

ポケモンGOのイベントを日本時間・日本語でまとめた購読用カレンダーです。週1回、自動で更新されます。

## 購読URL

```
webcal://raw.githubusercontent.com/raitok0905/pogo-calendar-ja/main/pogo.ics
```

iPhone / Mac / iCloud.com のカレンダーで「照会カレンダー（購読カレンダー）」として追加してください。

## 中身

- 大型イベント、コミュニティ・デイ、レイドデイ、マックスバトルデイなど（通知あり）
- スポットライトアワー、レイドアワー、マックスマンデー（15分前に通知）
- 伝説・メガ・シャドウレイド、マックスバトルのボスの入れ替わり
- 仲良しフライデーなどの曜日ボーナス

## しくみ

- `events.json`：イベントの一覧（ここを編集する）
- `build.py`：`events.json` から `pogo.ics` を作る（`python3 build.py`）
- `pogo.ics`：購読されるカレンダー本体

情報源：ポケモンGO公式ニュース（pokemongo.com/ja/news）ほか。非公式のカレンダーです。
