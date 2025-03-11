import requests
from bs4 import BeautifulSoup
import json
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service # 최신화된 chromedriver 초기화 방식 적용
from selenium.common.exceptions import NoSuchElementException # 페이지네이션 처리를 위해 필요
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from urllib.request import urlopen

from datetime import datetime

import ssl

dateMatcher = {
    "Jan" : "01",
    "Feb" : "02",
    "Mar" : "03",
    "Apr" : "04",
    "May" : "05",
    "Jun" : "06",
    "Jul" : "07",
    "Aug" : "08",
    "Sep" : "09",
    "Oct" : "10",
    "Nov" : "11",
    "Dec" : "12"
}

# 6 -> 06
# 12 -> 12
def dayFarmat(n):
    if(len(str(n)) == 1):
        return str("0" + str(n))
    return str(n)


# 딕셔너리 초기화
data = {}

# 카카오
# arr = []
# for i in range(1, 14):
#     context = ssl._create_unverified_context()
#     res = urlopen("https://tech.kakao.com/blog/"+str(i)+"/#posts", context=context)
#     soup = BeautifulSoup(res.read(), 'html.parser', from_encoding='utf-8')

#     urls = soup.select('ul.list_post strong.tit_post')
#     atag = soup.select('#posts > div > div.wrap_post > ul > li a.link_post')
#     date = soup.select('#posts > div > div.wrap_post > ul > li > a.link_post > span')


#     n = 1
#     for url in urls:
#         if(len(date[n-1].text)<3):# 몇개의 게시물의 날짜가 표시되지 않는다, 게시글까지 타고 들어가서 날짜를 가져온다
#             context = ssl._create_unverified_context()
#             res = urlopen(atag[n-1].get('href'), context=context)
#             soup = BeautifulSoup(res.read(), 'html.parser', from_encoding='utf-8')

#             date_branch = soup.select('span.txt_date')
#             arr.append({"title" : url.text, "url" : atag[n-1].get('href'), "date" : date_branch[0].text})
#             print(url.text +" "+ atag[n-1].get('href') +" "+ date_branch[0].text)
#         else:
#             arr.append({"title" : url.text, "url" : atag[n-1].get('href'), "date" : date[n-1].text})
#             print(url.text +" "+ atag[n-1].get('href') +" "+ date[n-1].text)
#         n += 1  
    
# data["카카오"] = arr

# 당근마켓 
# arr = []

# year = 2018
# size = 10

# base_url = "https://medium.com/daangn/archive/"

# NAVER D2
arr = []

# 네이버는 페이지 0부터 시작
# home = home/?page=0 이랑 똑같기 때문
page = 0
size = 20

base_url = "https://d2.naver.com/api/v1/contents"
params = {"size":20} # 한 페이지 당 20개의 포스트 - 이건 네이버에서 정해놓은거임임

page = 0 # 초기 페이지 번호

while True :
    params["page"] = page

    res = requests.get(base_url, params=params)

    if res.status_code != 200:
        print(f"API 호출 실패 : {res.status_code}")
        break

    # html 에서 content 부분만 파싱 (key-value 쌍이므로 content에 대한 key부분만 가져오기)
    html = res.json()
    posts = html.get("content", [])

    if not posts:
        print("더 이상 게시글이 없습니다")
        break

    for post in posts :
        title = post["postTitle"]
        url = f"https://d2.naver.com{post['url']}"  # 절대 URL로 변환
        atag = post["postHtml"]
        date = datetime.fromtimestamp(post["postPublishedAt"] / 1000).strftime('%Y.%m.%d')

        arr.append({"title": title, "url": url, "date": date})
        print(f"{title} {url} {date}")

    total_pages = html["page"]["totalPages"]

    if page >= total_pages - 1:
        print("마지막 페이지에 도달했습니다.")
        break

    page += 1

data["NAVER D2"] = arr



# 우아한 형제들
context = ssl._create_unverified_context()
res = urlopen("http://woowabros.github.io/?source=post_page-----e2d736d0e658----------------------", context=context)
soup = BeautifulSoup(res.read(), 'html.parser', from_encoding='utf-8')

urls = soup.select('body > div.page-content > div > section > div > div > a > h2')
atag = soup.select('body > div.page-content > div > section > div > div > a')
date = soup.select('body > div.page-content > div > section > div > div > span')

n = 1

arr = []
for url in urls:
    # 날짜 포멧 맞추기
    dateText = date[n-1].text
    dateEnd = dateText.find(",")+1
    subdate = dateText[0:dateEnd+5]
    resdate = str(subdate[subdate.find(",")+2:subdate.find(",")+6]) + "." + str(dayFarmat(dateMatcher[subdate[0:3]]))  + "." + str(dayFarmat(subdate[4:subdate.find(",")]))

    arr.append({"title" : url.text, "url" : "http://woowabros.github.io" + atag[n-1].get('href'), "date" : resdate})
    print(url.text +" "+ "http://woowabros.github.io" + atag[n-1].get('href') +" "+ resdate)
    n += 1  

data["우아한 형제들"] = arr


# 스포카
arr = []
for i in range(1, 12):
    if(i == 1):
        context = ssl._create_unverified_context()
        res = urlopen("https://spoqa.github.io", context=context)
        soup = BeautifulSoup(res.read(), 'html.parser', from_encoding='utf-8')
    else:
        context = ssl._create_unverified_context()
        res = urlopen("https://spoqa.github.io/page"+str(i), context=context)
        soup = BeautifulSoup(res.read(), 'html.parser', from_encoding='utf-8')

    urls = soup.select('body > div > div.content > div.posts > ul > li > div > h2 > a > span')
    atag = soup.select('body > div > div.content > div.posts > ul > li > div > h2 > a')
    date = soup.select('body > div > div.content > div.posts > ul > li > div > span.post-date')

    n = 1


    for url in urls:
        # 날짜 가져오기
        dateText = date[n-1].text
        year = dateText[0:4]
        month = dateText[6:8]
        day = dateText[10:12]
        resDate = year + "." + month + "." + day

        #a 다듬기 ..   . 이 앞에 붙어있다
        resHref = atag[n-1].get('href')[atag[n-1].get('href').find("/"):len(atag[n-1].get('href'))]
        arr.append({"title" : url.text, "url" : "https://spoqa.github.io" + resHref, "date" : resDate})
        print(url.text +" "+ "https://spoqa.github.io" + resHref + " " + resDate)
        n += 1  
    
data["스포카"] = arr 

# 라인
arr = []
for i in range(1, 19):
    res = requests.get('https://engineering.linecorp.com/ko/blog/page/'+str(i)+'/?source=post_page-----e2d736d0e658----------------------')
    html = res.content
    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')

    urls = soup.select('article > div > header > div > h2 > a')
    atag = soup.select('article > div > header > div > h2 > a')
    date = soup.select('article span.byline')
    n = 1

    for url in urls:
        dateText = date[n-1].text
        resDate = dateText[3:13]

        arr.append({"title" : url.text, "url" : atag[n-1].get('href'), "date" : resDate})
        print(url.text +" "+ atag[n-1].get('href') + " " + resDate)
        n += 1  
    
data["라인"] = arr


# 구글 (첫페이지만 가져온다)
res = requests.get('https://developers.googleblog.com/?source=post_page-----e2d736d0e658----------------------')
html = res.content
soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')

urls = soup.select('div.post > h2 > a')
atag = soup.select('div.post > h2 > a')
date = soup.select('span.publishdate')

n = 1

arr = []
for url in urls:
    dateText = date[n-1].text
    dateText_sub = dateText[dateText.find(",")+2:len(dateText)]
    year = dateText_sub[dateText_sub.find(",")+2 : dateText_sub.find(",")+6]
    month = dateMatcher[dateText_sub[0:3]]
    day = dayFarmat(dateText_sub[dateText_sub.find(" ")+1:dateText_sub.find(",")])
    
    resDate = year + "." + month + "." + day

    arr.append({"title" : url.text, "url" : atag[n-1].get('href'), "date" : resDate})
    print(url.text +" "+ atag[n-1].get('href') + " " + resDate)
    n += 1  

data["구글"] = arr 



# 페이스북 (최신 9개만 가져온다)
res = requests.get('https://developers.facebook.com/blog/')
html = res.content
soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')

urls = soup.select('h2._1jlv._7p3_._66wj')
atag = soup.select('a._8xd-._8xdi._8zgc._8zgd')
date = soup.select('div._6z8e > div._6z8b > div._6z8a')
n = 1

arr = []
for url in urls:
    # 날짜 만들기
    dateText = date[n-1].text
    year = dayFarmat(dateText[dateText.find("년")-4:dateText.find("년")].strip())
    month = dayFarmat(dateText[dateText.find("월")-2:dateText.find("월")].strip())
    day = dayFarmat(dateText[dateText.find("일")-2:dateText.find("일")].strip())

    resDate = year + "." + month + "." + day

    arr.append({"title" : url.text, "url" : atag[n-1].get('href'), "date" : resDate})
    print(url.text +" "+ atag[n-1].get('href') + " " + resDate)
    n += 1  

data["페이스북"] = arr



# 넷플릭스 (최신)
res = requests.get('https://medium.com/netflix-techblog')
html = res.content
soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')

urls = soup.select('h3.u-contentSansBold.u-lineHeightTightest.u-xs-fontSize24.u-paddingBottom2.u-paddingTop5.u-fontSize32 > div')
atag = soup.select('a:has(> h3.u-contentSansBold.u-lineHeightTightest.u-xs-fontSize24.u-paddingBottom2.u-paddingTop5.u-fontSize32)')
date = soup.select('div.postMetaInline.postMetaInline-authorLockup.ui-captionStrong.u-flex1.u-noWrapWithEllipsis > div > time')

n = 1

arr = []
for url in urls:
    dateText = date[n-1].text
    if(len(dateText) <= 8):
        year = "2019"
    else:
        year = dateText[dateText.find(",")+2 : dateText.find(",")+6]
    
    month = dateMatcher[dayFarmat(dateText[0:3])]
    day = dayFarmat(dateText[4:5])
    resDate = year + "." + month + "." + day
    print(resDate)

    arr.append({"title" : url.text, "url" : atag[n-1].get('href'), "date" : resDate})
    print(url.text +" "+ atag[n-1].get('href') + " " + resDate)
    n += 1  

data["넷플릭스"] = arr

#========================================== 아래부터는 ChromeDriver 사용 ===========================================

#====================================================== NHN =======================================================

# NHN (최신)
arr = []

# ChromeDriver 설정
service = Service('./chromedriver.exe')  # ChromeDriver 경로 지정
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(3)  # 기본 대기 시간 설정

# 초기 페이지 번호
page = 1

# 페이지네이션 처리 : 더 이상 넘어갈 페이지가 없을때까지 크롤링 진행
while True:
    url = f'https://meetup.nhncloud.com/?page={page}' # 페이지 URL 생성
    driver.get(url) # 페이지에 접근

    # 포스트 목록이 로드될 때까지 대기 (최대 5초)
    try:
        # Selenium에서 웹 페이지의 동적 콘텐츠를 기다리는 데 사용되는 부분
        # WebDriverWait 객체를 생성하여, 특정 조건이 만족될 때까지 Selenium이 기다리도록 설정
        wait = WebDriverWait(driver, 5)
        # wait.until = 지정된 조건이 충족될 때까지 기다립니다
        # 페이지에 <li class="lst_item"> 요소가 최소 하나 이상 나타날 때까지 대기
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "lst_item")))

        # 현재 페이지의 포스트 추출
        posts = driver.find_elements(By.CLASS_NAME, "lst_item")
        for post in posts:
            try:
                title = post.find_element(By.CLASS_NAME, "tit").text
                atag = post.find_element(By.CLASS_NAME, "lst_link").get_attribute('href')
                date = post.find_element(By.CLASS_NAME, "date").text.replace("등록일 ", "")
                arr.append({"title": title, "url": atag, "date": date})
                print(f"{title} {atag} {date}")
            except Exception as e:
                print(f"포스트 데이터 추출 중 오류: {e}")
                continue

        # 다음 페이지 버튼 확인
        next_button = driver.find_element(By.CSS_SELECTOR, ".tui-pagination .tui-next")
        if "tui-is-disabled" in next_button.get_attribute("class"):
            print("마지막 페이지에 도달했습니다.")
            break
        # 다음 페이지로 이동 (페이지 번호 증가)
        page += 1

    except NoSuchElementException:
        print("다음 버튼을 찾을 수 없음. 크롤링 종료.")
        break
    except Exception as e:
        print(f"페이지 처리 중 오류 발생: {e}")
        break

# 브라우저 종료
driver.quit()

# NHN 크롤링 결과 DICTIONARY에 저장
data["NHN"] = arr



# 모든 내용 json 파일화
# result.json 파일을 쓰기 모드로 열어 실행할때마다 덮어쓰기 진행
file = open('result.json','w', -1, "utf-8")
json.dump(data, file, ensure_ascii=False)
file.close