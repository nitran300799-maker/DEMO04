from flask import Flask, render_template_string
import csv
import io
import ssl
import urllib.request

app = Flask(__name__)

DATA_URL = "https://data.ntpc.gov.tw/api/datasets/781b822e-214a-4b9a-b4db-32c9f4626d98/csv/file"


def fetch_csv_data(url):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(url, context=context) as response:
        raw = response.read()
        content_type = response.getheader("Content-Type", "")
        text = raw.decode(response.headers.get_content_charset(failobj="utf-8"))

    stream = io.StringIO(text)
    reader = csv.DictReader(stream)
    rows = [row for row in reader]
    header = reader.fieldnames or []

    return {
        "url": url,
        "content_type": content_type,
        "data_length": len(raw),
        "total_rows": len(rows),
        "total_cols": len(header),
        "header": header,
        "rows": rows,
    }


@app.route("/")
def index():
    try:
        data = fetch_csv_data(DATA_URL)
    except Exception as e:
        error_html = """
            <!DOCTYPE html>
            <html lang="zh-Hant">
            <head>
              <meta charset="UTF-8" />
              <meta name="viewport" content="width=device-width, initial-scale=1.0" />
              <title>讀取資料錯誤</title>
              <style>
                body { font-family: Arial, sans-serif; background: #f2f4f7; color: #1f2937; padding: 40px; }
                .error-box { background: white; border: 1px solid #d1d5db; border-radius: 16px; padding: 28px; max-width: 800px; margin: 0 auto; }
                h1 { margin-top: 0; color: #dc2626; }
                pre { white-space: pre-wrap; word-break: break-word; color: #111827; }
              </style>
            </head>
            <body>
              <div class="error-box">
                <h1>讀取資料時發生錯誤</h1>
                <pre>{{ error }}</pre>
              </div>
            </body>
            </html>
        """
        return render_template_string(error_html, error=str(e))

    html = """
        <!DOCTYPE html>
        <html lang="zh-Hant">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>新北市文化活動資料卡片檢視</title>
          <style>
            body {
              margin: 0;
              padding: 30px 16px;
              font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
              background: #eef2f5;
              color: #111827;
            }
            .page-shell {
              max-width: 1200px;
              margin: 0 auto;
            }
            .page-title {
              font-size: 2.2rem;
              margin: 0 0 10px;
              color: #1a3ea8;
              font-weight: 800;
            }
            .page-description {
              margin: 0 0 24px;
              color: #475569;
              line-height: 1.7;
            }
            .summary-bar {
              display: flex;
              flex-wrap: wrap;
              gap: 14px;
              margin-bottom: 28px;
            }
            .summary-card {
              background: white;
              border: 1px solid #d1d5db;
              border-radius: 16px;
              padding: 18px 20px;
              flex: 1 1 220px;
              min-width: 220px;
              box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
            }
            .summary-card strong {
              display: block;
              font-size: 1.7rem;
              color: #1a73e8;
              margin-bottom: 4px;
            }
            .summary-label {
              color: #475569;
              font-size: 0.95rem;
            }
            .summary-url {
              margin-top: 12px;
              font-size: 0.9rem;
              color: #1a3ea8;
              word-break: break-all;
            }
            .record-card {
              background: white;
              border: 1px solid #d1d5db;
              border-radius: 18px;
              padding: 24px;
              margin-bottom: 20px;
              box-shadow: 0 16px 32px rgba(15, 23, 42, 0.06);
            }
            .record-title {
              margin: 0 0 18px;
              font-size: 1.35rem;
              color: #0f172a;
              font-weight: 700;
            }
            .field-row {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 16px;
              margin-bottom: 18px;
            }
            .field-item {
              display: flex;
              flex-direction: column;
              gap: 8px;
              word-break: break-word;
            }
            .field-label {
              font-size: 0.95rem;
              color: #1f2937;
              font-weight: 700;
            }
            .field-value {
              font-size: 1rem;
              color: #334155;
              line-height: 1.65;
              white-space: pre-wrap;
            }
            .field-value a {
              color: #1a73e8;
              text-decoration: none;
            }
            .field-value a:hover {
              text-decoration: underline;
            }
            .full-width {
              grid-column: 1 / -1;
            }
            @media (max-width: 860px) {
              .field-row {
                grid-template-columns: 1fr;
              }
            }
          </style>
        </head>
        <body>
          <div class="page-shell">
            <h1 class="page-title">新北市文化活動資料卡片檢視</h1>
            <p class="page-description">以下每筆資料皆以白色圓角卡片顯示，讓內容在淺灰背景中清楚突顯。</p>

            <div class="summary-bar">
              <div class="summary-card">
                <span class="summary-label">總列數</span>
                <strong>{{ data.total_rows }}</strong>
              </div>
              <div class="summary-card">
                <span class="summary-label">欄位數</span>
                <strong>{{ data.total_cols }}</strong>
              </div>
              <div class="summary-card">
                <span class="summary-label">資料大小</span>
                <strong>{{ "%.1f"|format(data.data_length / 1024) }} KB</strong>
              </div>
              <div class="summary-card">
                <span class="summary-label">資料格式</span>
                <strong>{{ data.content_type }}</strong>
              </div>
            </div>

            <div class="summary-card summary-url">
              <span>來源 URL：</span>
              {{ data.url }}
            </div>

            {% for row in data.rows %}
            <div class="record-card">
              <h2 class="record-title">第 {{ loop.index }} 筆資料</h2>

              <div class="field-row">
                <div class="field-item">
                  <div class="field-label">author</div>
                  <div class="field-value">{{ row.author or 'N/A' }}</div>
                </div>
                <div class="field-item">
                  <div class="field-label">【類型】</div>
                  <div class="field-value">{{ row.type or 'N/A' }}</div>
                </div>
                <div class="field-item">
                  <div class="field-label">【開始日期】</div>
                  <div class="field-value">{{ row.startdate or 'N/A' }}</div>
                </div>
                <div class="field-item">
                  <div class="field-label">【結束日期】</div>
                  <div class="field-value">{{ row.enddate or 'N/A' }}</div>
                </div>
                <div class="field-item full-width">
                  <div class="field-label">【標題】</div>
                  <div class="field-value">{{ row.title or 'N/A' }}</div>
                </div>
                <div class="field-item full-width">
                  <div class="field-label">【連結】</div>
                  <div class="field-value">
                    {% if row.link %}
                      <a href="{{ row.link }}" target="_blank" rel="noreferrer">{{ row.link }}</a>
                    {% else %}
                      N/A
                    {% endif %}
                  </div>
                </div>
                <div class="field-item full-width">
                  <div class="field-label">【簡介】</div>
                  <div class="field-value">{{ row.description or 'N/A' }}</div>
                </div>
                <div class="field-item full-width">
                  <div class="field-label">【發佈時間】</div>
                  <div class="field-value">{{ row.pubdate or 'N/A' }}</div>
                </div>
              </div>
            </div>
            {% endfor %}
          </div>
        </body>
        </html>
    """

    return render_template_string(html, data=data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
