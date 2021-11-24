import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle
import requests
import requests_html
from selenium.webdriver.chrome.options import Options
URL = 'https://www.youtube.com/watch?v=QPYY1DiV7cs'
from bs4 import BeautifulSoup
from threading import Thread, Barrier
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import PySimpleGUI as sg
#URL = 'https://youtu.be/Uustku44-xk'


#Get proxy
def scrap_proxy():
    global px_list
    px_list = set()
    res = []
    res_2 = []
    px_list = []
    session = requests_html.HTMLSession()
    r = session.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(r.html.html, 'html.parser')
    for i in soup.find_all('textarea'):
        for k in i:
            res.append(k)
    a = list(map(lambda x: x.replace('Free proxies from free-proxy-list.net', ''), res))
    for p in a:
        res_2.append(p.split('\n'))
    res_2[0].remove(res_2[0][1])
    res_2[0].remove(res_2[0][2])
    res_2[0].remove(res_2[0][3])
    for i in res_2:
        for k in i:
            if k != '':
                px_list.append(k)
    print(len(px_list))

    print('--New proxy scrapped, left:' + str(len(px_list)))
    with open('proxis.pickle', 'wb') as f:
        pickle.dump(px_list, f)
    return px_list





#Check get proxy
def check_proxy(px):
    try:
        requests.get('https://www.google.com/', proxies = {'https':
                                                          'https://'+ px}, timeout = 3)
    except Exception as x:
        print(f'--{px} is dead {x.__class__.__name__}')
        return False
    return True


def get_proxy(scrap = False):
    global px_list
    if scrap or len(px_list) < 6:
        px_list = scrap_proxy()
    while True:
        if len(px_list) < 6:
            px_list = scrap_proxy()
        while True:
            if len(px_list) < 6:
                px_list = scrap_proxy()
            px = px_list.pop()
            if check_proxy(px):
                break
        print('-' + px + 'is alive. ({} left)'.format(str(len(px_list))))
        with open('proxis.pickle', 'wb') as f:
            pickle.dump(px_list, f)
        return px


#lock = threading.RLock()

def drive(URL,barrier, options):
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(URL)

    try:
        if EC.alert_is_present():
            print('EC.alert_is_present()')
            WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.ID, 'CloseLink'))).click()
        else:
            print('hmm... alert not present')
    except Exception as e:
        print('-->', e)



    element = driver.find_element_by_class_name('ytp-play-button.ytp-button')
    element.send_keys(Keys.ENTER)
    #driver.switch_to(driver.find_element_by_xpath('//iframe[starts-with@src, "https://youtu.be/Uustku44-xk")]'))
    #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Play"]'))).click()
    #print('wait for others')
    time.sleep(5)
    print('close')
    barrier.wait()
    time.sleep(36)
    driver.close()


def users(URL, barrier):
    PROXY = get_proxy(scrap = True)
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % PROXY)
    try:
        drive(URL,barrier, options)
    except:
        time.sleep(33)
        drive(URL, barrier, options)

  #  element.send_keys(Keys.ENTER)
   # time.sleep(31)
    #element.send_keys(Keys.ENTER)





def activate(URL, number_of_threads):
        barrier = Barrier(number_of_threads)
        threads = []
        for  _ in range(number_of_threads):
            my_thread = Thread(target = users,args = (URL,barrier,) )
            my_thread.start()
            threads.append(my_thread)
            print(f'Запущено потоков: {threading.active_count()}')
        for t in threads:
            t.join()


layout = [
    [sg.Text('URL'), sg.InputText()],
    [sg.Text('Количесвто пользователей'),sg.InputText()],
    [sg.Output(size = (30,5))],
    [sg.Submit(), sg.Cancel()]

]
window = sg.Window('YouTube', layout)
while True:
    event, values = window.read()
    print('Запущено добавление пользователей')
    activate(values[0], int(values[1]))
    if event in (None, 'Exit', 'Cancel'):
        break




