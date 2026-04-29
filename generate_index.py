#!/usr/bin/env python3
"""Generate index.html listing all weekly reports and downloadable files."""

import os
import glob


def generate(site_dir="."):
    output_dir = os.path.join(site_dir, "docs")
    reports_dir = os.path.join(site_dir, "reports")

    # ---- collect reports ----
    reports = []
    if os.path.isdir(output_dir):
        for f in sorted(glob.glob(os.path.join(output_dir, "*.md")), reverse=True):
            reports.append(os.path.basename(f))

    # ---- collect downloads ----
    downloads = []
    if os.path.isdir(reports_dir):
        for f in sorted(os.listdir(reports_dir)):
            fp = os.path.join(reports_dir, f)
            if os.path.isfile(fp):
                size = os.path.getsize(fp)
                downloads.append((f, size))

    # ---- build HTML ----
    def fmt_size(n):
        for unit in ("B", "KB", "MB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} GB"

    report_rows = ""
    if reports:
        for name in reports:
            report_rows += f"""
            <li>
              <a href="docs/{name}" class="report-link">{name.replace('-weekly.md', '').replace('output/', '')}</a>
              <a href="docs/{name}" class="btn" target="_blank">查看</a>
            </li>"""
    else:
        report_rows = "<li class='empty'>暂无周报</li>"

    download_rows = ""
    if downloads:
        for name, size in downloads:
            download_rows += f"""
            <li>
              <span class="file-name">{name}</span>
              <span class="file-size">({fmt_size(size)})</span>
              <a href="reports/{name}" class="btn" download>下载</a>
            </li>"""
    else:
        download_rows = "<li class='empty'>暂无下载文件</li>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VC/PE 每周市场观察</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f5f7fa; color: #1a1a2e; line-height: 1.6; }}
  .container {{ max-width: 880px; margin: 0 auto; padding: 32px 20px; }}
  header {{ text-align: center; padding: 32px 0 24px; }}
  header h1 {{ font-size: 1.6rem; font-weight: 700; color: #16213e; }}
  header p {{ color: #6b7280; font-size: 0.9rem; margin-top: 4px; }}
  section {{ background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  section h2 {{ font-size: 1.1rem; font-weight: 600; color: #16213e; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #eef1f5; }}
  ul {{ list-style: none; }}
  li {{ display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f5; gap: 12px; }}
  li:last-child {{ border-bottom: none; }}
  li.empty {{ color: #9ca3af; font-style: italic; }}
  .report-link {{ flex: 1; color: #2563eb; text-decoration: none; font-weight: 500; }}
  .report-link:hover {{ text-decoration: underline; }}
  .file-name {{ flex: 1; font-weight: 500; }}
  .file-size {{ color: #9ca3af; font-size: 0.85rem; white-space: nowrap; }}
  .btn {{ display: inline-block; padding: 4px 14px; border-radius: 6px; font-size: 0.8rem; text-decoration: none; font-weight: 500; background: #2563eb; color: #fff; white-space: nowrap; }}
  .btn:hover {{ background: #1d4ed8; }}
  footer {{ text-align: center; color: #9ca3af; font-size: 0.8rem; padding: 24px 0; }}
  @media (max-width: 600px) {{ .container {{ padding: 16px 12px; }} section {{ padding: 16px; }} li {{ flex-wrap: wrap; }} }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>VC/PE 每周市场观察</h1>
    <p>自动化周报系统 · 每周一更新</p>
  </header>

  <section>
    <h2>&#128196; 历史周报</h2>
    <ul>{report_rows}
    </ul>
  </section>

  <section>
    <h2>&#128206; 可下载报告</h2>
    <ul>{download_rows}
    </ul>
  </section>

  <footer>
    <p>GitHub Actions &#43; DeepSeek 自动生成</p>
  </footer>
</div>
</body>
</html>"""

    out_path = os.path.join(site_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html generated ({len(reports)} reports, {len(downloads)} downloads)")


if __name__ == "__main__":
    generate()
