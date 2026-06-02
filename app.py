from flask import Flask, render_template, abort
import csv
import io
import ssl
import urllib.request

app = Flask(__name__)

DATA_URL = "https://data.ntpc.gov.tw/api/datasets/781b822e-214a-4b9a-b4db-32c9f4626d98/csv/file"


def fetch_csv_data(url):
    """獲取 CSV 資料並轉換為結構化格式"""
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
    """主頁面 - 顯示資料表格"""
    try:
        data = fetch_csv_data(DATA_URL)
    except Exception as e:
        return render_template(
            "details.html",
            error=True,
            error_message=str(e),
            item={},
            header=[],
            source_url=DATA_URL,
        )

    return render_template("table.html", data=data)


@app.route("/details/<int:item_id>")
def details(item_id):
    """詳細資料頁面 - 顯示單筆資料的完整內容"""
    try:
        data = fetch_csv_data(DATA_URL)
    except Exception as e:
        return render_template(
            "details.html",
            error=True,
            error_message=str(e),
            item={},
            header=[],
            source_url=DATA_URL,
        )

    if item_id < 0 or item_id >= len(data["rows"]):
        abort(404)

    item = data["rows"][item_id]
    return render_template(
        "details.html",
        item=item,
        header=data["header"],
        item_id=item_id,
        total_rows=data["total_rows"],
        source_url=data["url"],
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
