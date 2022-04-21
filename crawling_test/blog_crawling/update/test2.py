# 시스템
from multiprocessing import Pool
import os
import sys
import re
import time
# 크롤링
import urllib.request
import requests
import json
from scrapy.http import TextResponse
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm

import pandas as pd

import warnings
warnings.filterwarnings('ignore')
# 태그 데이터를 삭제하는 코드


def tag_remove(word):

    word = re.sub('(<([^>]+)>)', '', word)

    return word


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

# blog가 네이버 블로그인지 아닌지 판별하는 코드


def naver_blog_check(code):

    if code[0].isdigit():
        return False
    else:
        return True


# 모든 단어를 하나씩 나누어서 확인하자.
#

def naver_title_check(search_word, title):

    # search_word = preprocess_sentence_kr(search_word)

    for words in search_word.split():
        for word in words:
            if word.lower() not in title.lower():
                return True

# 이름이 들어오면 해당 내용을 이용하여 블로그를 파싱한다.

# search_word : 어떤 제품을 검색하는지
# repeat_num : 해당 제품이 제목에서 몇번 안나올때까지 검색을 진행할 지


def item_parsing(search_word, start, display, repeat_num):
    print("value %s is in PID : %s" % (start, os.getpid()))
    cnt = 0
    blog_search = naver_api(search_word, start, display)
    # test = search_word
    # print(f"naver api {test}")
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
    # while repeat:

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
        # try:
        #     if start + display <= blog_search["total"]:
        #         cnt += 1
        #         start += display
        #         blog_search = naver_api(
        #             search_word, start, display)
        #     else:
        #         repeat = False

        #     if cnt == 10:
        #         break
        # except:
        #     break
    return blog_result, blog_writer, blog_code, blog_title, blog_description


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


def search_word(word):
    result = []
    append_data = ["후기", "리뷰"]
    for data in append_data:
        result.append(word + " " + data)

    return result


# print(num_cores)

# def test(x,y):

#     return x*y


def test(x, y):
    print("value %s is in PID : %s" % (x, os.getpid()))
    return x*y


def multi(args):
    print(args)
    return test(*args)


def multi_jjin(args):

    return item_parsing(*args)


if __name__ == '__main__':
    start = int(time.time())
    df = pd.DataFrame()
    words = search_word("LG 스타일러")
    url, title = [], []
    # data = [(1, 2), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (
    #     3, 4), (2, 3), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4), (2, 3), (3, 4)]

    # pool = Pool(processes=4)
    # output = pool.map(multi, data)
    # print(output)
    # output = []
    # for i in range(len(data)):
    #     x, y = data[i]
    #     output.append(test(x, y))

    # print(output)
    pool = Pool(processes=4)
    for word in words:

        # blog_result, blog_writer, blog_code, blog_title, blog_description = pool.map(
        #     item_parsing, (word, range(1, 1000, 100), 100, 3))
        word, 1, 100, 3
        word, 101, 100, 3
        word, 201, 100, 3
        blog_result, blog_writer, blog_code, blog_title, blog_description = pool.map(
            multi_jjin, data)
        url += blog_result
        title += blog_title
    # description += blog_description

    print("***run time(sec) :", time.time() - start)


# pool.close()  # 더이상 추가 작업이 들어가지 않는다.
# pool.join()  # 모든 프로세스가 종료되기를 기다리는것

# df["url"] = url
# df["title"] = title
# # df["description"] = description

# print(df)
# df = df.drop_duplicates(["url"]).reset_index(drop=True)
