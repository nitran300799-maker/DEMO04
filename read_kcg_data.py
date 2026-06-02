

import csv
import io
import ssl
import urllib.request

url = "https://data.ntpc.gov.tw/api/datasets/781b822e-214a-4b9a-b4db-32c9f4626d98/csv/file"

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(url, context=context) as response:
        raw = response.read()
        content_type = response.getheader("Content-Type", "")
        text = raw.decode(response.headers.get_content_charset(failobj="utf-8"))

    stream = io.StringIO(text)
    reader = csv.reader(stream)
    rows = [row for row in reader]

    if not rows:
        print("沒有讀到任何資料。")
    else:
        header, *data = rows
        total_rows = len(data)
        total_cols = len(header)
        data_length = len(raw)

        print("===== 讀取結果 =====")
        print(f"URL: {url}")
        print(f"Content-Type: {content_type}")
        print(f"資料長度: {data_length} bytes")

        print("===== 資料摘要 =====")
        print(f"總列數: {total_rows}")
        print(f"欄位數: {total_cols}")

        preview_count = min(5, total_rows)
        for index in range(preview_count):
            row = data[index]
            print(f"===== 第{index + 1}筆資料 =====")
            for col_index, field_name in enumerate(header):
                value = row[col_index] if col_index < len(row) else ""
                print(f"{field_name}: {value}")

        if total_rows > preview_count:
            print(f"...共 {total_rows} 筆資料，僅顯示前 {preview_count} 筆。")
except Exception as e:
    print(f"讀取資料時發生錯誤: {e}")
