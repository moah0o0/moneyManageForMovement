import requests
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# (인증서 없는 환경 기준) 우체국 Index → 보안프로그램 설치 팝업 닫기 → 간편조회 클릭 → 거래내역 조회 클릭 → 쿠키 Get 후 세션 Return
def cookie_creator(): 
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) 
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://epostbank.go.kr/")

    TARGETS = [
        (True,  By.CSS_SELECTOR, "button.btn_close_popup", "닫기 버튼"),
        (False, By.CSS_SELECTOR, "div.dimed", "오버레이층"),
        (True,  By.CSS_SELECTOR, "body > div.wrapper > header > div > div.quick_menu_wrap > div > div.quick_menu > div:nth-child(3) > ul.quick_link > li:nth-child(2) > a", "빠른조회 버튼"),
        (True,  By.ID, "btnIHSICH00AT", "거래내역조회 버튼"),
    ]

    for is_click, by, selector, desc in TARGETS:
        try:
            if is_click:
                elem = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((by, selector))
                )
                try:
                    elem.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", elem)
            else:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((by, selector))
                )
        except TimeoutException:
            pass

    # requests.Session()에 쿠키 이관
    result_session = requests.Session()
    for c in driver.get_cookies():
        result_session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path'))

    driver.quit()
    return result_session


def post_api(session, accountNumber, accountPassword, accountOwnerBirth, startDate, endDate, value_bfLastDlngNoS8):

    url = "https://epostbank.go.kr/IHSICH00R02.do"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "epostbank.go.kr",
        "Origin": "https://epostbank.go.kr",
        "Referer": "https://epostbank.go.kr/errorCustom.do",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }


    data = {
        "IHSICHloginYn": "",
        "IHSICHbfLastDlngNoS8": value_bfLastDlngNoS8,
        "IHSICHnextDatExistYnS1": "Y",
        "IHSICHdepsActno": accountNumber,
        "IHSICHinptEpwd": accountPassword,
        "IHSICHbrdt": accountOwnerBirth,
        "IHSICHinqBgngYmd": startDate,
        "IHSICHinqEndYmd": endDate,
        "IHSICHinqDvsnS1": "1",
        "IHSICHinqSeqCdS1": "1",
    }

    resp = session.post(url, headers=headers, data=data, verify=True)

    return resp


def formatter_transaction_data(data, bankSettingRecord, bankAccountNumber):
    description = data.get("txmnEnm")
    
    if data.get("txmnEnm") is None:
        description = "공란"    
    
    result = {
        "no": data.get("dlngNo"),
        "bank": bankSettingRecord,
        "bankAccountNumber":bankAccountNumber,
        "type": {"입금":"수입", "지급":"지출"}[data.get("pbmpRnpyDvsnCdNm")],
        "datetime": (data.get("dlngYmd") + data.get("dlngTm"))[:12],
        "description": description,
        "money": int(data.get("dlngAmt")),
    }
    return result


def GET(session, bankSettingRecord, accountNumber, accountPassword, accountOwnerBirth, startDate, endDate):    
    RESULT_TRANSACTIONS = []
    
    bfLastDlngNoS8 = ""

    while True:
        resp = post_api(session, accountNumber, accountPassword, accountOwnerBirth, startDate, endDate, bfLastDlngNoS8)
        data = resp.json()
        
        if data.get("failed") != True:
            RESULT_TRANSACTIONS.extend(data.get("inqDatagrid", []))

        if data.get("nextDatExistYnS1") == "N":
            break
        
        bfLastDlngNoS8 = data.get("bfLastDlngNoS8")
        time.sleep(2)

    RESULT_TRANSACTIONS = map(lambda x: formatter_transaction_data(data=x, bankSettingRecord=bankSettingRecord, bankAccountNumber=accountNumber), RESULT_TRANSACTIONS)
    RESULT_TRANSACTIONS = list(RESULT_TRANSACTIONS)
    RESULT_TRANSACTIONS = sorted(RESULT_TRANSACTIONS, key=lambda x: x["datetime"])

    return RESULT_TRANSACTIONS