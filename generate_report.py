import os
import json
import logging
from datetime import datetime

from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SYSTEM_PROMPT_OVERVIEW = """你是一位专业的经济分析师。根据以下多条VC/PE资讯摘要，用3-5句中文提炼本周市场总体趋势。
重点关注：融资活跃度、热门赛道、地区分布、政策动向等。"""


def generate_overview(client, summaries):
    """Use DeepSeek to generate a weekly overview from all summaries."""
    if not summaries:
        return "本周无有效资讯。"

    text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(summaries) if s)

    try:
        resp = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_OVERVIEW},
                {"role": "user", "content": f"请根据以下资讯摘要生成本周市场概览：\n\n{text[:4000]}"},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log.warning(f"Overview generation failed: {e}")
        return "本周概览生成失败。"


def build_markdown(data, overview):
    """Build the markdown weekly report string."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []
    lines.append(f"# VC/PE 每周市场观察（{today}）")
    lines.append("")

    # Section 1: Overview
    lines.append("## 一、本周概览")
    lines.append("")
    lines.append(overview)
    lines.append("")

    # Section 2: Details
    lines.append("## 二、重点资讯详情")
    lines.append("")
    for i, item in enumerate(data, 1):
        subject = item.get("subject", "(No subject)")
        sender = item.get("sender", "")
        date = item.get("date", "")
        summary = item.get("summary", "无摘要")
        all_links = item.get("all_links", [])

        lines.append(f"### {i}. {subject}")
        lines.append("")
        lines.append(f"- **发件人**: {sender}")
        lines.append(f"- **日期**: {date}")
        lines.append(f"- **摘要**: {summary}")
        if all_links:
            lines.append("- **相关链接**:")
            for link in all_links[:5]:  # top 5 links to keep report clean
                url = link["url"]
                text = link.get("text", url)
                lines.append(f"  - [{text}]({url})")
            if len(all_links) > 5:
                lines.append(f"  - *...及另外 {len(all_links) - 5} 个链接*")
        lines.append("")

    # Section 3: Downloadable reports
    lines.append("## 三、本周可下载报告")
    lines.append("")
    all_report_links = []
    for item in data:
        all_report_links.extend(item.get("report_links", []))

    if all_report_links:
        for link in all_report_links:
            url = link["url"]
            text = link.get("text", url)
            lines.append(f"- [{text}]({url})")
    else:
        lines.append("本周无可下载报告。")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def main():
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not os.path.exists("data/analyzed.json"):
        log.warning("data/analyzed.json not found, skipping.")
        return

    with open("data/analyzed.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        log.warning("No analyzed data to report.")
        return

    # Generate overview using DeepSeek
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com") if api_key else None
    summaries = [item.get("summary", "") for item in data]

    if client:
        log.info("Generating weekly overview...")
        overview = generate_overview(client, summaries)
    else:
        overview = "（未配置 DEEPSEEK_API_KEY，概览暂缺）"

    markdown = build_markdown(data, overview)

    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("docs", exist_ok=True)
    filepath = os.path.join("docs", f"{today}-weekly.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    log.info(f"Weekly report saved to {filepath}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
