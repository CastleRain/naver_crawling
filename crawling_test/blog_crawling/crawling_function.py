# 시스템
import os
import sys
import re
import json

# 크롤링
import urllib.request
import requests
from bs4 import BeautifulSoup

import pandas as pd

from tqdm import tqdm
# 태그 데이터를 삭제하는 코드


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        pass


def tag_remove(word):
    word = re.sub('(<([^>]+)>)', '', word)
    return word

# blog가 네이버 블로그인지 아닌지 판별하는 코드


def naver_blog_check(code):

    if code[0].isdigit():
        return False
    else:
        return True

# 제목에서 크롤링해올 데이터 찾아오기


def naver_title_check(search_word, title):

    for words in search_word.split():
        for word in words:
            if word.lower() not in title.lower():
                return True


def naver_api(search_word, start, display):
    client_id = "GvNa2sBgFDA6v7ujnaz0"
    client_secret = "Yo0jOskXlZ"
    encText = urllib.parse.quote(search_word)

    url = "https://openapi.naver.com/v1/search/blog?query=" + encText  # json 결과
    url += f"&start={start}"
    url += f"&display={display}"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode == 200):
        response_body = response.read()
    else:
        print("Error Code:" + rescode)
    return json.loads(response_body.decode('utf-8'))


# 이름이 들어오면 해당 내용을 이용하여 블로그를 파싱한다.

# search_word : 어떤 제품을 검색하는지
# repeat_num : 해당 제품이 제목에서 몇번 안나올때까지 검색을 진행할 지
# 최대 1000개까지만 진행하자
def item_parsing(search_word, start, display, repeat_num):

    cnt = 0
    blog_search = naver_api(search_word, start, display)

    # result : url
    # writer : 작성자 이름
    # code : 블로그 코드
    # title : 블로그 제목
    # description : 블로그 요약 설명
    blog_result = []
    blog_writer = []
    blog_code = []
    blog_title = []
    blog_description = []
    repeat = True
    cnt = 0
    # 제목에서 해당 제품의 이름이 5번 연속 안나온다면 패스
    while repeat:
        print(cnt)
        for blog in blog_search["items"]:
            # 블로그 코드
            code = blog["link"][blog["link"].find("logNo=") + 6:]
            if naver_blog_check(code):  # 네이버 블로그가 아닌경우 다음으로 넘기기
                continue

            # 이름
            writer = blog["bloggerlink"][23:]

            # 제목
            title = tag_remove(blog["title"])

            if naver_title_check(search_word, title):
                continue

            # 블로그 요약
            description = tag_remove(blog["description"])
            # 데이터 추가하는 곳
            # 블로그 코드 추가
            blog_code.append(code)
            # 이름 추가
            blog_writer.append(writer)
            # 제목 추가
            blog_title.append(title)
            # 블로그 요약 추가
            blog_description.append(description)
            # 본문 크롤링을 위한 URL주소 추가
            blog_result.append(
                f"https://blog.naver.com/PostView.naver?blogId={writer}&logNo={code}")
        try:
            if start + display <= blog_search["total"]:
                cnt += 1
                start += display
                blog_search = naver_api(search_word, start, display)
            else:
                repeat = False

            if cnt == 10:
                break
        except:
            break
    return blog_result, blog_writer, blog_code, blog_title, blog_description

# 네이버 블로그 크롤링


def blog_content_parsing(url):

    blog_req = requests.get(url)
    blog_bs = BeautifulSoup(blog_req.text, "html.parser")

    result = []
    quote = []

    quote_cnt = 0
    img_cnt = 0
    blog_text, content, first_img, last_img = "", "", "", ""
    try:
        # 현재 여기서 안되는것은 스마트에디터 3로 작성된 경우이다.
        # 이미지 내용 크롤링
        img_craw = blog_bs.select(".se-module-image")
        img_cnt = len(img_craw)

        if img_cnt != 0:  # 사진이 있는 경우만 크롤링
            try:
                first_img = img_craw[0].select_one(
                    ".se-module-image-link > img")["data-lazy-src"]
                last_img = img_craw[img_cnt-1].select_one(
                    ".se-module-image-link > img")["data-lazy-src"]

            except:
                first_img = img_craw[0].select_one(
                    ".se-module-image-link > img")["src"]
                last_img = img_craw[img_cnt -
                                    1].select_one(".se-module-image-link > img")["src"]
        # 글 내용 크롤링
        blog_text = blog_bs.select(".se-text")
        for i in blog_text:
            for j in i.select(".se-module-text > p"):
                txt = j.text
                if txt != "\u200b":
                    result.append(txt)
        content = " ".join(result)

        for i in blog_bs.select(".se-quote"):
            quote.append(i.text)
            quote_cnt += 1
    except:
        return False, content, len(content), len(blog_text), quote, quote_cnt,  first_img, last_img,  img_cnt

    return True, content, len(content), len(blog_text), quote, quote_cnt, first_img, last_img,  img_cnt

# 검색되는 데이터 확인


def search_word(word):
    result = []
    append_data = ["후기", "리뷰"]
    for data in append_data:
        result.append(word + " " + data)

    return result


def df_keyword_contains(df):

    keyword_contains = ["허락", "내돈내산", "리얼후기", "협찬",
                        "체험단", "coupa.ng", "<", ">", "♡", "♥", "구매후기"]
    keyword_cnt = ["솔직", "비교", "ㅋ", "ㅋㅋ", "ㅋㅋㅋ", "ㅋㅋㅋㅋ", "...",
                   "....", "ㅜ", "ㅜㅜ", "ㅜㅜㅜ", "ㅜㅜㅜㅜ", "ㅠ", "ㅠㅠ", "ㅠㅠㅠ", "ㅠㅠㅠㅠ"]
    keyword_badword = ["개좋다", "개좋음", "개멋짐", "개빠름", "개큼", "존나", "걍", "씹창"]

    for key in keyword_cnt:
        df[key + " 빈도 수"] = 0
    df["비속어 빈도 수"] = 0

    for i in range(len(df)):
        content = df.loc[i, "content"]
        for key in keyword_contains:
            if key in content:
                df.loc[i, key+" 키워드"] = "1"

            else:
                df.loc[i, key+" 키워드"] = "0"

        for cont in content.split():
            for key in keyword_cnt:
                if key in cont:
                    df.loc[i, key + " 빈도 수"] += 1

            for bad in keyword_badword:
                if bad in cont:
                    df.loc[i, "비속어 빈도 수"] += 1
    return df


def df_check_ad(df):
    df["광고 분류1"] = 9
    df["광고 분류2"] = 9

    pure_review = ["허락 키워드", "내돈내산 키워드", "리얼후기 키워드", "솔직 빈도 수", "비교 빈도 수"]
    reward_review = ["coupa.ng 키워드"]
    advertise_review = ["협찬 키워드", "체험단 키워드"]
    items = [pure_review, reward_review, advertise_review]

    for i in range(len(df)):

        for idx,  item in enumerate(items):

            if idx == 0:
                for it in item:
                    if str(df.loc[i, it]) != "0":
                        df.loc[i, "광고 분류1"] = 0
                        df.loc[i, "광고 분류2"] = 0
                        break

            elif idx == 1:
                for it in item:
                    if df.loc[i, it] != "0":
                        df.loc[i, "광고 분류1"] = 1
                        df.loc[i, "광고 분류2"] = 1
                        break

            elif idx == 2:
                for it in item:
                    if df.loc[i, it] != "0":
                        df.loc[i, "광고 분류1"] = 1
                        df.loc[i, "광고 분류2"] = 2
                        break

# 서비스 시작


def service_start(word):
    df = pd.DataFrame()
    url, title = [], []
    words = search_word(word)

    for word in words:
        blog_result, blog_writer, blog_code, blog_title, blog_description = item_parsing(
            word, 1, 100, 3)
        url += blog_result
        title += blog_title

    df["url"] = url
    df["title"] = title

    # # 중복 url삭제
    df = df.drop_duplicates(["url"]).reset_index(drop=True)

    content_list, content_cnt_list, content_line_list, quote_list, quote_cnt_list, first_img_list, last_img_list, img_cnt_list = [
    ], [], [], [], [], [], [], []
    for i in tqdm(range(len(df))):
        _, content, content_cnt, content_line, quote, quote_cnt, first_img, last_img, img_cnt = blog_content_parsing(
            df.loc[i, "url"])

        content_list.append(content)
        content_cnt_list.append(content_cnt)
        content_line_list.append(content_line)
        quote_list.append(quote)
        quote_cnt_list.append(quote_cnt)
        first_img_list.append(first_img)
        last_img_list.append(last_img)
        img_cnt_list.append(img_cnt)

    df["content"] = content_list
    df["content_cnt"] = content_cnt_list
    df["content_line"] = content_line_list
    df["quote"] = quote_list
    df["quote_cnt"] = quote_cnt_list
    df["first_img"] = first_img_list
    df["last_img"] = last_img_list
    df["img_cnt"] = img_cnt_list
    df_keyword_contains(df)
    df_check_ad(df)
    return df
