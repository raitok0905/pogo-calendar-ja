#!/usr/bin/env python3
"""events.json から日本語のポケモンGOカレンダーを作る。

  pogo.ics        メイン（イベント・1時間イベント・曜日ボーナス）
  pogo-raids.ics  レイドボスの入れ替わり（calendar が "raids" の予定）

events.json の各要素:
  id          必須。予定を見分ける固定ID（変えると別の予定扱いになる）
  title       必須。予定のタイトル
  start/end   必須。日本時間。時刻ありは "YYYY-MM-DDTHH:MM"、終日は "YYYY-MM-DD"
  allDay      終日予定なら true（end は最終日の翌日）
  alarm       通知を何分前に出すか（省略で通知なし）
  description 説明（任意）
  url         情報源のURL（任意）
  calendar    "raids" ならレイド用カレンダーに入る（省略でメイン）
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "events.json"
TZID = "Asia/Tokyo"
CALENDARS = {
    "main": ("pogo.ics", "ポケモンGO", "ポケモンGOのイベント（日本時間・自動更新）"),
    "raids": ("pogo-raids.ics", "ポケモンGO レイド",
              "伝説・メガ・シャドウレイドとマックスバトルのボスの入れ替わり（日本時間・自動更新）"),
}


def esc(text: str) -> str:
    return (text.replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def fold(line: str) -> str:
    """RFC 5545: 1行75オクテット以内に折り返す（UTF-8の文字を途中で切らない）。"""
    out, cur, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        limit = 75 if not out else 74
        if size + n > limit:
            out.append(cur)
            cur, size = ch, n
        else:
            cur += ch
            size += n
    out.append(cur)
    return "\r\n ".join(out)


def dt(value: str, all_day: bool) -> str:
    if all_day:
        return ";VALUE=DATE:" + datetime.strptime(value, "%Y-%m-%d").strftime("%Y%m%d")
    return f";TZID={TZID}:" + datetime.strptime(value, "%Y-%m-%dT%H:%M").strftime("%Y%m%dT%H%M%S")


def build(events, name: str, desc_text: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//pogo-calendar-ja//JA",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{name}",
        f"X-WR-TIMEZONE:{TZID}",
        f"X-WR-CALDESC:{esc(desc_text)}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
        "X-PUBLISHED-TTL:PT6H",
        "BEGIN:VTIMEZONE",
        f"TZID:{TZID}",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0900",
        "TZOFFSETTO:+0900",
        "TZNAME:JST",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]
    for e in events:
        all_day = bool(e.get("allDay"))
        desc = e.get("description", "")
        if e.get("url"):
            desc = (desc + "\n" if desc else "") + e["url"]
        lines += [
            "BEGIN:VEVENT",
            f"UID:{e['id']}@pogo-calendar-ja",
            f"DTSTAMP:{stamp}",
            "DTSTART" + dt(e["start"], all_day),
            "DTEND" + dt(e["end"], all_day),
            f"SUMMARY:{esc(e['title'])}",
            "TRANSP:TRANSPARENT",
        ]
        if desc:
            lines.append(f"DESCRIPTION:{esc(desc)}")
        if e.get("url"):
            lines.append(f"URL:{e['url']}")
        if e.get("alarm"):
            lines += [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"DESCRIPTION:{esc(e['title'])}",
                f"TRIGGER:-PT{int(e['alarm'])}M",
                "END:VALARM",
            ]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


if __name__ == "__main__":
    events = json.loads(SRC.read_text(encoding="utf-8"))
    ids = [e["id"] for e in events]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        sys.exit(f"IDが重複しています: {', '.join(sorted(dup))}")
    events.sort(key=lambda e: (e["start"], e["id"]))
    unknown = {e.get("calendar", "main") for e in events} - set(CALENDARS)
    if unknown:
        sys.exit(f"不明な calendar: {', '.join(sorted(unknown))}")
    for key, (filename, name, desc_text) in CALENDARS.items():
        part = [e for e in events if e.get("calendar", "main") == key]
        (HERE / filename).write_text(build(part, name, desc_text), encoding="utf-8", newline="")
        print(f"{len(part)}件 → {filename}")
