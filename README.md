> 기획 : 2025. 8. 28.


# 1. 전제
○ 결산 방식 : 단식부기
○ 계정 수준 : 관-항-목
○ 거래내역과 장부 분리
○ TestTarget : 부산퀴어행동 계좌

# 2. 기능

## 1) Scraper

✓ 15분마다 은행 빠른조회를 이용하여 법인/개인 계좌 거래내역 스크래핑 → 거래내역 DB 등록 및 텔레그램 알림 발송

## 2) WebApp

✓ 거래내역 조회

✓ 스크래핑 로그

✓ 계정과목 관리

✓ 장부 관리
· 거래내역에서 불러오기
· (edit disable) 일련번호, 구분, 일시, 적요, 금액
· (editable) 계정, 세부내역, 증빙자료(코드) 

✓ 증빙자료 관리
· 코드 : multiple Files (PDF Only)

✓ 실시간 보고서 공개
· depth1 결산표 → depth2 계정별 거래내역, 증빙자료 확인

✓ 실시간 보고서 다운로드
· dpeth1 결산표, 장부, 증빙자료 묶음 → PDF 처리

# 3. 기술

## 1) Scrapper
✓ python Selenium + Requests
✓ APScheduler → Scrapping Manage Page 
✓ TelegramAPI
✓ Database : to Pocketbase


**디렉터리**
```
|- bank_scrapper (은행별 스크래퍼 함수 묶음)
|-- Job.py (스크래핑 → Pocketbase Collections 세팅 → Pocketbase Record 생성)
|-- PostBankScrapper (우체국예금 스크래퍼)
|- main.py (스케쥴러)
|- setting.py (후술)
```

**setting.py**

```py

# 우체국 함수 호출
from bank_scrapper import PostBankScrapper

ThreadPool = 8 # 스케쥴러 ThreadPool


SERVICES = {
    "등록계좌명" : {
      "function": PostBankScrapper, # 거래내역 수집 계좌가 해당하는 은행 함수를 입력
      "accountNumber": "-------", # 거래내역 수집 계좌 
      "accountPassword": "----", # 거래내역 수집 계좌 비밀번호
      "accountOwnerBirth": "------", # 거래내역 수집 계좌 사업자번호 또는 예금주 생년월일(앞 6자리)
      "initDate": "2025.03.02.", # 거래내역 수집 시작 기간 (초기 세팅시 필요 / YYYY.MM.DD. 형태)
      "session":requests.session(), 
      # "session": PostBankScrapper.cookie_creator(), # 우체국의 경우, 정상 접속 유저 cookie가 반영된 세션이 불필요함. 다만 필요시 selenium을 통해 세션을 불러온 우, requests로 스크래핑할 수 있음
      "pb": PocketBase("http://127.0.0.1:8090"), # PocketBase 백엔드 서버 주소
      "pb_admin_email":"-----@----.---", # PocketBase 백엔드 서버 슈퍼관리자 email
      "pb_admin_password":"------", # PocketBase 백엔드 서버 슈퍼관리자 password
      "pb_collection_name_settings":{ # PocketBase 백엔드 서버 컬렉션명 설정
          "TransactionHistoryScrappingLog": "TransactionHistoryScrappingLog", # - 거래내역 스크래핑 로그
          "TransactionHistory": "TransactionHistory" # - 거래내역
      },
      "updatePreiod":"month", # month(30일), week(7일), day(1일)
      "updateSchedule":15, # (초) 스케쥴러 반복 주기(인터벌)
    },
    
    (...)
}
```

## 2) WebApp

✓ Backend : Pocketbase
✓ Frontend : VueJS Router (deploy with Python Flask) 
  ※ CSR(SPA) 베이스로 하되, SSO 등 향후 접근성 고려하여 일부단 SSR 처리.
