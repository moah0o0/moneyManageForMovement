# PocketBase 연결 정보
PB_URL = "Pocketbase URL"
PB_USER = "users.permission이 'scrapper'인 계정의 이메일"
PB_PASS = "users.permission이 'scrapper'인 계정의 비밀번호"

# 스케줄러 기본 실행 설정
UPDATE_INTERVAL_SECONDS = 60 * 10 # 기본 10분마다 실행

# ===============================================
# 스크래핑 대상 계정 정보 목록 (여러 은행 정보 등록)
# ===============================================

BANK_ACCOUNTS = [
    {
        "JOB_ID": 'postbank_update_01',
        "BANK_TYPE": "Postbank",
        "BANK_SETTING_RECORD_ID": "Pocketbase BankSetting 컬렉션의 해당하는 계좌 정보 Record ID", 
        "ACCOUNT_NUMBER": "계좌번호", 
        "ACCOUNT_PASSWORD": "계좌 비밀번호", 
        "ACCOUNT_OWNER_BIRTH": "예금주 생년월일 또는 사업자번호", 
        "ACCOUNT_INIT_DATE": "2025.03.02.",  # 조회 시작일
        "UPDATE_PERIOD": "week", 
        "REMOVE_LIST": [1],
        "INTERVAL_SECONDS": 60 * 10
    },
]
