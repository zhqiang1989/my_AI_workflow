"""用原始微信 TXT 更新 PPT 简报、下载包和手册里的画像与复制区。"""

import json
import re
from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
MATERIALS = ROOT / "materials"
MANUAL = ROOT / "私行客户经理_WorkBuddy实操手册.html"


def message_rows(plain_text):
    chat = plain_text.split("## 微信对话", 1)[1]
    time = ""
    for line in chat.splitlines():
        timestamp = re.fullmatch(r"\*\*【(.+)】\*\*", line)
        if timestamp:
            time = timestamp[1]
        message = re.fullmatch(r"\*\*([^*]+)\*\*[:：]\s*(.+)", line)
        if message:
            if not time:
                raise ValueError("微信消息缺少原记录时间")
            yield time, message[1], message[2]


def render_card(person, plain_text):
    slug = person["slug"]
    name = escape(person["name"])
    prompt_id = f"w_{slug}"
    rows = list(message_rows(plain_text))
    quote_time, quote_speaker, quote = rows[person["quote"] - 1]
    if quote_speaker != person["name"]:
        raise ValueError(f"画像引用必须是客户原话：{slug}")
    fields = "\n".join(f"          <div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>"
                       for label, value in person["fields"].items())
    chat = "\n".join(
        f'          <li class="{"manager" if speaker == "小陈" else "client"}">'
        f'<div class="message-meta"><b>{escape(speaker)}</b> <span>{escape(time[5:])}</span></div>'
        f'<p>{escape(text)}</p></li>'
        for time, speaker, text in rows
    )
    return f'''    <article class="persona-card" data-person="{slug}" aria-labelledby="title-{slug}">
      <img src="samples/portraits/{slug}.webp" alt="{escape(person['alt'])}" width="800" height="600" loading="lazy">
      <div class="persona-body">
        <h3 id="title-{slug}">{name}</h3>
        <p class="persona-hook">{escape(person['hook'])}</p>
        <p class="persona-description">{escape(person['description'])}</p>
        <dl class="persona-facts">
{fields}
        </dl>
        <blockquote>「{escape(quote)}」<cite>微信原话 · {escape(quote_time)}</cite></blockquote>
        <p class="persona-source"><a href="samples/客户微信_{name}.txt" download>下载课堂原始记录</a></p>
        <button class="copy" data-t="{prompt_id}">复制{name}的记录</button>
      </div>
      <details class="persona-chat">
        <summary>查看微信记录（{len(rows)} 条）</summary>
        <ol class="message-list" aria-label="{name}的课堂微信记录">
{chat}
        </ol>
        <pre id="{prompt_id}" class="sample-copy-text" hidden>{escape(plain_text)}</pre>
      </details>
    </article>'''


def replace_block(html, name, content):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    pattern = rf"({re.escape(start)})[\s\S]*?({re.escape(end)})"
    html, count = re.subn(pattern, lambda m: f"{m[1]}\n{content}\n{m[2]}", html)
    if count != 1:
        raise ValueError(f"应存在一组 HTML 标记：{name}")
    return html


def build():
    people = json.loads((SAMPLES / "人物样例.json").read_text(encoding="utf-8"))
    files = {f"客户微信_{person['name']}.txt": (SAMPLES / f"客户微信_{person['name']}.txt").read_text(encoding="utf-8")
             for person in people}
    if len(files) != 3:
        raise ValueError("课堂手册需要三位不同的样例客户")
    count = "、".join(f"{person['name']} {len(list(message_rows(plain)))} 条"
                     for person, plain in zip(people, files.values()))

    introduction = (
        "只在独立的「课堂示例知识库」整理本次材料。未确认目录时先问我，不要读取真实微信或写入业务库。\n"
        "用上一步可用的 LLM Wiki 技能或本地文件工具，按文件名分别保存虚构档案卡和长微信原文到 raw/客户微信/。\n"
        f"保留日期和说话人，核对消息条数：{count}。本步只归档原文，画像在第 4 步统一生成。\n"
        "回报文件位置和条数。档案测评是课堂字段，聊天中的语音、图片、转账和产品说法均为情境文字。"
    )
    records = "\n\n".join(f"【{name}】\n{plain.strip()}" for name, plain in files.items())
    bundle = introduction + "\n\n" + records
    (MATERIALS / "customer-chats.md").write_text(
        "# 三位课堂客户的长微信原文\n\n"
        f"虚构档案卡和微信对话。按下列文件名分开保存。消息条数：{count}。\n\n"
        + records + "\n", encoding="utf-8", newline="\n"
    )
    (MATERIALS / "brief.md").write_text(
        "# 课堂练习资料：从三份微信记录准备客户沟通\n\n"
        "客户经理收到王先生、李女士和张总各一份档案卡及长微信记录。这个练习用于找出不同客户的资金安排、沟通偏好和需要补问的事项，再准备经理审阅用的内容。\n\n"
        "## 本次课堂交付\n\n"
        "做一页 HTML，解释这份简报的用途、输入、四步流程和每步产出。为三位客户分别做卡片，每张写「关心什么」「怎么聊」「还要问什么」，配一条原话并注明记录日期。\n\n"
        "## 四步流程\n\n"
        "1. 查找能回到原文的公开资料。产品条件以该期官方说明书为依据。\n"
        "2. 整理三份记录，区分档案字段、客户原话、经理说法和待确认事项。\n"
        "3. 按每位客户的实际关切提供沟通要点和草稿方向。\n"
        "4. 由客户经理核对期限、取用条件、资金归属、措辞和适用范围，再决定是否使用。\n\n"
        "客户和档案都是课堂虚构。语音、图片、转账为记录占位，聊天里提到的产品条件或已经发过的资料不能代替官方原件。\n\n"
        f"## 三份长微信记录 · {count}\n\n"
        + records + "\n", encoding="utf-8", newline="\n"
    )
    html = MANUAL.read_text(encoding="utf-8")
    for marker, prompt_id in (("sample-import", "p0"), ("sample-copy-all", "w_all")):
        html = replace_block(html, marker, f'  <pre id="{prompt_id}">{escape(bundle)}</pre>')
    html = replace_block(html, "sample-cards", "\n".join(
        render_card(person, plain) for person, plain in zip(people, files.values())
    ))
    MANUAL.write_text(html, encoding="utf-8", newline="\n")

    with ZipFile(SAMPLES / "微信对话样例.zip", "w") as archive:
        for filename, plain in files.items():
            archive.writestr(ZipInfo(filename), plain.encode("utf-8"), compress_type=ZIP_DEFLATED)


if __name__ == "__main__":
    build()
