#!/usr/bin/env python3
"""events.json から日本語のポケモンGOカレンダー (pogo.ics) を作る。

events.json の各要素:
  id          必須。予定を見分ける固定ID（変えると別の予定扱いになる）
  title       必須。予定のタイトル
  start/end   必須。日本時間。時刻ありは "YYYY-MM-DDTHH:MM"、終日は "YYYY-MM-DD"
  allDay      終日予定なら true（end は最終日の翌日）
  alarm       通知を何分前に出すか（省略で通知なし）
  description 説明（任意）
  url         情報源のURL（任意）
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "events.json"
OUT = HERE / "pogo.ics"
TZID = "Asia/Tokyo"


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


def build(events) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//pogo-calendar-ja//JA",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:ポケモンGO",
        f"X-WR-TIMEZONE:{TZID}",
        "X-WR-CALDESC:ポケモンGOのイベント（日本時間・自動更新）",
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
    seen = set()
    for e in events:
        if e["id"] in seen:
            sys.exit(f"IDが重複しています: {e['id']}")
        seen.add(e["id"])
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
    events.sort(key=lambda e: (e["start"], e["id"]))
    OUT.write_text(build(events), encoding="utf-8", newline="")
    print(f"{len(events)}件 → {OUT.name}")
