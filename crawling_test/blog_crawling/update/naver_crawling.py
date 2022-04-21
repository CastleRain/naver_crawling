from datetime import datetime
from crawling_function import service_start, createFolder

now = datetime.now()
year, month, day = now.year, now.month, now.day

createFolder(f"./result/{year}{month}{day}")


if __name__ == "__main__":
    company = input("제조 회사 이름을 작성해주세요 : ")
    words = input("제품명을 입력해주세요 : ")
    df = service_start(company, words)
    df.to_csv(f"./result/{year}{month}{day}/{company}_{words} 결과.csv",
              index=False, encoding="utf-8-sig")
