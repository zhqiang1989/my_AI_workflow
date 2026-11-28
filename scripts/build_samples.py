"""生成课堂的微信式 TXT、下载包，以及手册中的人物卡和复制区。"""

import json
import re
from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
MATERIALS = ROOT / "materials"
MANUAL = ROOT / "私行客户经理_WorkBuddy实操手册.html"


def message_rows(person):
    for index, (time, speaker, text) in enumerate(person["messages"], 1):
        yield f"{person['code']}-W{index:02}", time, speaker, text


def transcript(person):
    # 延续课程 seed_lab.py 的编号、时间、说话人、原文布局。
    lines = [f"# {person['name']}的微信式课堂对话", "",
             "文学人物的现代课堂模拟。资金用途、日期和对白均为虚构。", "",
             f"客户代号：{person['code']}。", "正式风险测评：未提供。", "", "## 微信记录", ""]
    lines.extend(f"{key}　{time}　{speaker}\n> {text}\n"
                 for key, time, speaker, text in message_rows(person))
    return "\n".join(lines)


def render_card(person, plain_text):
    slug = person["slug"]
    name = escape(person["name"])
    prompt_id = f"w_{slug}"
    rows = list(message_rows(person))
    quote_id, _, quote_speaker, quote = rows[person["quote"] - 1]
    if quote_speaker != person["name"]:
        raise ValueError(f"画像引用必须是客户原话：{slug}")
    fields = "\n".join(f"          <div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>"
                       for label, value in person["fields"].items())
    chat = "\n".join(
        f'          <li class="{"manager" if speaker == "小陈" else "client"}">'
        f'<div class="message-meta"><b>{escape(speaker)}</b> <span>{escape(time[5:])} · {key}</span></div>'
        f'<p>{escape(text)}</p></li>'
        for key, time, speaker, text in rows
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
        <blockquote>「{escape(quote)}」<cite>微信原话 · {quote_id}</cite></blockquote>
        <p class="persona-source"><a href="{escape(person['source_url'])}" target="_blank" rel="noopener">性格取材 · {escape(person['source_label'])}</a></p>
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
    texts = [(person, transcript(person)) for person in people]
    files = {f"客户微信_{person['name']}.txt": plain for person, plain in texts}
    if len(files) != 3:
        raise ValueError("课堂手册需要三位不同的样例客户")

    introduction = (
        "只在独立的「课堂示例知识库」整理本次材料。未确认目录时先问我，不要读取真实微信或写入业务库。\n"
        "以下是全部虚构的课堂对话。请用上一步实际可用的 LLM Wiki 技能或本地文件工具，按文件名分别保存到 raw/客户微信/。\n"
        "保留原文、编号、日期和说话人，每份核对 10 条。本步只归档原文，画像在第 4 步统一生成。\n"
        "在现有索引和日志中登记，回报文件位置和条数。正式风险测评未提供。"
    )
    records = "\n\n".join(f"【{name}】\n{plain.strip()}" for name, plain in files.items())
    bundle = introduction + "\n\n" + records
    (MATERIALS / "customer-chats.md").write_text(
        "# 三位课堂客户的模拟微信原文\n\n"
        "按下列文件名分开保存。全部为课堂虚构，每位各 10 条，正式风险测评未提供。\n\n"
        + records + "\n", encoding="utf-8", newline="\n"
    )
    html = MANUAL.read_text(encoding="utf-8")
    for marker, prompt_id in (("sample-import", "p0"), ("sample-copy-all", "w_all")):
        html = replace_block(html, marker, f'  <pre id="{prompt_id}">{escape(bundle)}</pre>')
    html = replace_block(html, "sample-cards", "\n".join(render_card(person, plain) for person, plain in texts))
    MANUAL.write_text(html, encoding="utf-8", newline="\n")

    with ZipFile(SAMPLES / "微信对话样例.zip", "w") as archive:
        for filename, plain in files.items():
            content = plain.encode("utf-8")
            (SAMPLES / filename).write_bytes(content)
            archive.writestr(ZipInfo(filename), content, compress_type=ZIP_DEFLATED)


if __name__ == "__main__":
    build()
