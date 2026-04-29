import os
import json
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位专业的经济和风险投资分析师。请用中文总结以下邮件内容，控制在5句以内。
重点关注：融资金额、轮次、行业赛道、地区、政策影响等经济学相关视角。
如果内容不涉及这些，概括核心信息即可。"""


def summarize(client, body_text, max_retries=2):
    """Call DeepSeek Chat API to summarize the email body."""
    if not body_text or len(body_text.strip()) < 20:
        return "邮件内容过短，无法生成摘要。"

    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"请总结以下邮件内容：\n\n{body_text[:4000]}"},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            log.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None


def main():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        log.error("DEEPSEEK_API_KEY not set in environment or .env")
        return

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    if not os.path.exists("data/emails.json"):
        log.warning("data/emails.json not found, skipping.")
        return

    with open("data/emails.json", "r", encoding="utf-8") as f:
        emails = json.load(f)

    if not emails:
        log.info("No emails to analyze.")
        # Still write an empty analyzed file
        os.makedirs("data", exist_ok=True)
        with open("data/analyzed.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    results = []
    for i, email in enumerate(emails):
        subject = email.get("subject", "(No subject)")
        log.info(f"[{i+1}/{len(emails)}] Summarizing: {subject[:60]}")

        summary = summarize(client, email.get("body_text", ""))

        entry = {**email, "summary": summary}
        results.append(entry)

        if summary:
            log.info(f"  -> Summary: {summary[:100]}...")
        else:
            log.warning(f"  -> Failed to summarize: {subject[:60]}")

    os.makedirs("data", exist_ok=True)
    with open("data/analyzed.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    log.info(f"Done. {len(results)} email(s) written to data/analyzed.json")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
