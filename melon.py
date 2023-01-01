import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
from datetime import datetime
import csv

load_dotenv(verbose=True)

M_ID = os.getenv('M_ID')
M_PW = os.getenv('M_PW')
MEMBERKEY = os.getenv('MEMBERKEY')


# 선택한 월의 TOP 10(num) 목록 가져오기
def get_monthly_top_songs(month:int, year:int, num:int) -> list:
    monthly_top_songs = []
    time.sleep(0.1)
    tbody = driver.find_element(By.TAG_NAME, "tbody")
    trs = tbody.find_elements(By.TAG_NAME, "tr")
    cnt = 0

    for i in range(num):
        try:
            msl = []
            rank = trs[i].find_element(By.CLASS_NAME, "no").text
            tleft = trs[i].find_element(By.CLASS_NAME, "t_left")
            title = tleft.find_elements(By.TAG_NAME, "a")[1].text
            artist = trs[i].find_element(By.ID, "artistName").text

            msl.append(year)
            msl.append(month)
            msl.append(title)
            if i==0:
                print(title)
                print()
            msl.append(artist)
            msl.append(rank)
            cnt += 1
        except:
            break

        monthly_top_songs.append(msl)
    
    if cnt==0:
        print("곡 없음 :: ", str(cnt))
        print()
        monthly_top_songs.append([year, month, "None"])

    return monthly_top_songs


# 특정 년도의 12달 크롤링
def get_one_year(year:int, num:int) -> list:
    lists = []
    for i in range(12):
        month_calendar = driver.find_element(By.CLASS_NAME, "month_calendar")
        month_btn = month_calendar.find_elements(By.CLASS_NAME, "btn")   # 12개
        month_btn[i].click()
        print(str(i+1),"월")
        month = i+1

        # 선택한 월의 곡 목록 가져오기
        lists.append(get_monthly_top_songs(month, year, num))
        driver.find_element(By.CLASS_NAME, "d_btn_calenadar").click()
    return lists


# 년도 확인
def check_year(target_year:int) -> list:
    my_list = []
    year = driver.find_element(By.CLASS_NAME, "date").text
    while(True):
        if year == "2015" or int(year) < target_year:
            print("종료")
            break
        else:
            print(year)

            # # 1~12월 곡 리스트 가져오는 함수
            my_list.append(get_one_year(year, 10))
            time.sleep(0.5)

            # # 이전 년도로 이동
            driver.find_element(By.CLASS_NAME, "btn_round.small.pre").click()
            year = driver.find_element(By.CLASS_NAME, "date").text
    
    print(my_list)

    return my_list


# 리스트를 csv로 저장
def save_to_file(lists: list):
    print("save to file")
    dt_today = datetime.today()
    today = dt_today.strftime('%Y-%m-%d__%H-%M-%S')

    with open(f"./Monthly_Top_10_{today}.csv", "w", encoding="utf-8-sig") as file:
        wr = csv.writer(file)
        wr.writerow(["year", "month", "title", "artist", "rank"])

        for list_y in lists:
            for list_m in list_y:
                for song in list_m:
                    wr.writerow(song)
        return True



if __name__ == "__main__":

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = 'https://member.melon.com/muid/web/login/login_informM.htm'
    driver.get(url)

    # 로그인
    driver.find_element(By.ID, "id").send_keys(M_ID)
    driver.find_element(By.ID, "pwd").send_keys(M_PW)
    driver.find_element(By.ID, "btnLogin").click()

    # 마이뮤직>많이들은
    url_mypage = f'https://www.melon.com/mymusic/top/mymusictopmanysong_list.htm?memberKey={MEMBERKEY}'
    driver.get(url_mypage)

    # 월별보기 클릭
    calendar = driver.find_element(By.CLASS_NAME, "d_btn_calenadar")
    calendar.click()
    time.sleep(2)

    mylist = check_year(target_year=2010)
    save_to_file(mylist)

    driver.quit()