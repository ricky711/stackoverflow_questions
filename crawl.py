import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import time
import pymysql
from multiprocessing import Process, Manager, cpu_count

url_root = 'https://stackoverflow.com/questions?sort=votes&pagesize=50&page='


# 爬取器
def crawl(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
        'accept-language': 'zh-CN,zh;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))

    try:
        response = s.get(url, headers=headers, timeout=10).text
    except requests.exceptions.RequestException as e:
        print(time.strftime('%Y-%m-%d %H:%M:%S'), 'failed crawled:', url)
        print(e)
        response = None

    return response


# 网页解析器
def parser(response, id_):
    bs = BeautifulSoup(response, 'lxml')
    questions = bs.find_all('div', class_='question-summary')
    question_list = []
    counter = 0

    for question in questions:
        counter += 1
        votes = question.find('div', class_='votes').span.strong.get_text()

        if question.find('div', class_='answered-accepted') is not None:
            answers = question.find('div', class_='answered-accepted').strong.get_text()
        elif question.find('div', class_='answered') is not None:
            answers = question.find('div', class_='answered').strong.get_text()
        elif question.find('div', class_='unanswered') is not None:
            answers = question.find('div', class_='unanswered').strong.get_text()
        else:
            answers = 'Not found'

        views = question.find('div', class_='views').get_text().strip().replace(' views', '')
        title = question.find('div', class_='summary').h3.a.get_text()
        title_link = 'https://stackoverflow.com' + question.find('div', class_='summary').h3.a['href']
        description = question.find('div', class_='summary').find('div', class_='excerpt').get_text().strip().replace('\n', '').replace('\r', '')
        tags = ','.join([each.get_text() for each in question.find('div', class_='summary').find('div', class_='tags').find_all('a')])
        create_time = time.strftime('%Y-%m-%d %H:%M:%S')
        question_list.append((votes, answers, views, title, title_link, description, tags, create_time, str(id_), str(counter)))

    return question_list


# 存储器
def storag(fields):
    connect = pymysql.connect(host='',
                              user='',
                              password='',
                              db='crawl',
                              port=3306,
                              charset='utf8mb4')

    with connect.cursor() as cursor:
        for field in fields:
            sql = 'INSERT INTO crawl.t_stackoverflow_questions\
             (votes, answers, views, title, title_link, description, tags, create_time, page, page_rank)\
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, field)
            connect.commit()
        cursor.close()

    connect.close()


def main(targetUrls,failUrls):
    while True:
        page_index = targetUrls.get()
        response = crawl(url_root + str(page_index))
        if response is not None:
            question_list = parser(response, page_index)
            storag(question_list)
            time.sleep(1)
        else:
            failUrls.put(page_index)


if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'start')

    with Manager() as manager:
        targetUrls = manager.Queue()
        failUrls = manager.Queue()

        for i in range(21):
            targetUrls.put(i)
        
        pList = []

        for i in range(cpu_count):
            p = Process(target=main, args=(targetUrls,failUrls))
            p.start()
            pList.append(p)
        
        for p in pList:
            p.join()
        
        print("failUrls' size is", failUrls.qsize())
    
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'end')
