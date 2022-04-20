from datetime import datetime
from crawling_function import service_start, createFolder

now = datetime.now()
year, month, day = now.year, now.month, now.day

createFolder(f"./result/{year}{month}{day}")


words = input("제품명을 입력해주세요 : ")
df = service_start(words)
df.to_csv(f"./result/{year}{month}{day}/{words} 결과.csv",
          index=False, encoding="utf-8-sig")
