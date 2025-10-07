from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import inspect
import traceback
import requests
from zoneinfo import ZoneInfo
import json
import os 

import bank_scrapper.PostBankScrapper as PostBankScrapper

class Scrapper:

    def __init__(self, bankType, bankSettingRecord, accountNumber, accountPassword, accountOwnerBirth, accountInitDate, updatePreiod, pocketbaseConn, session = requests.session()):
        
        # 로그 파일 경로 설정
        self.ScheduleStartDate = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
        
        current_file_path = os.path.abspath(__file__)


        one_up = os.path.dirname(current_file_path)


        base_dir = os.path.dirname(one_up)
        log_dir = os.path.join(base_dir, "logs") 

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

            
        timestamp_for_file = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(log_dir, f"{bankType}_{timestamp_for_file}.log")
        
        self.bankSettingRecord = bankSettingRecord
        self.accountNumber = accountNumber
        self.accountPassword = accountPassword
        self.accountOwnerBirth = accountOwnerBirth
        self.accountInitDate = accountInitDate
        self.updatePreiod = updatePreiod
        self.pocketbaseConn = pocketbaseConn
        self.bankType = bankType
        self.session = session

        scrapping_function_list = {
            "Postbank":PostBankScrapper,
        }

        self.scrappingFunction = scrapping_function_list[self.bankType]


    def Logger(self, message, error=None, error_code=None):
        
        error_info = None
        if isinstance(error, Exception):
            error_info = traceback.format_exc()
        elif error is not None:
            error_info = str(error)

        log_raw = {
            "datetime": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
            "level": "ERROR" if error_info else "INFO",
            "bankSettingRecord": self.bankSettingRecord,
            "function": inspect.stack()[1].function, 
            "ScheduleStartDate": self.ScheduleStartDate,
            "message": message,
            "error_code": error_code,
            "error_traceback": error_info # <--- 여기에 전체 트레이스백이 저장됩니다.
        }
        
        # 파일에 JSON 형태로 저장하여 가독성 확보 (들여쓰기 4칸)
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_raw, ensure_ascii=False, indent=4) + ',\n')

        except Exception as e:
            # 파일 저장 실패 시 콘솔에 출력 (최후의 수단)
            print(f"로그 파일 저장 실패: {e}")
            print(json.dumps(log_raw, ensure_ascii=False, indent=4))


    def Init(self, remove_filter=[]):
        try:
            self.Logger(message="함수 시작")

            RESULT_TRANSACTION = []

            start = datetime.strptime(self.accountInitDate, "%Y.%m.%d.").date()
            today = datetime.now(ZoneInfo("Asia/Seoul")).date()

            interval_months = 6

            while start <= today:
                try: 
                    end = start + relativedelta(months=interval_months)
                    end = min(end, today)
                    next_start = (end + timedelta(days=1))

                    start_str = start.strftime("%Y.%m.%d.")
                    end_str = end.strftime("%Y.%m.%d.")
                    
                    resultTransactions = self.scrappingFunction.GET(
                        session=self.session,
                        bankSettingRecord=self.bankSettingRecord,
                        accountNumber=self.accountNumber,
                        accountPassword=self.accountPassword,
                        accountOwnerBirth=self.accountOwnerBirth,
                        startDate=start_str,
                        endDate=end_str
                    )

                    RESULT_TRANSACTION += resultTransactions 

                    start = next_start

                    self.Logger(message="{}~{}에 대한 Scrapping 완료".format(start_str, end_str))
                
                except requests.exceptions.HTTPError as http_err:
                    self.Logger(
                        message=f"HTTP 에러 발생 ({start_str}~{end_str})", 
                        error=http_err, 
                        error_code=http_err.response.status_code if http_err.response else "N/A"
                    )
                    start = next_start
                
                except Exception as period_e:
                    self.Logger(
                        message=f"스크래핑 중 예상치 못한 오류 발생 ({start_str}~{end_str})", 
                        error=period_e, 
                        error_code="SCRAP_UNKNOWN"
                    )
                    start = next_start
            
            # remove_filter 처리
            original_len = len(RESULT_TRANSACTION)
            RESULT_TRANSACTION = [t for t in RESULT_TRANSACTION if t["no"] not in remove_filter]
            removed_count = original_len - len(RESULT_TRANSACTION)
            
            self.Logger(message=f"필터 제거 완료. 총 {removed_count}건 제거됨. 남은 건수: {len(RESULT_TRANSACTION)}")
        
            for transaction in RESULT_TRANSACTION:
                self.pocketbaseConn.collection("Transaction").create(transaction)
            
            self.Logger(message="완료 - {}건 업로드 성공".format(len(RESULT_TRANSACTION)))

        except Exception as e:
            self.Logger(message="Init 함수 실행 중 치명적인 오류 발생", error=e, error_code="FATAL_INIT")
            raise e


    def Update(self, remove_filter):
        try:
            self.Logger(message="함수 시작")

            today = datetime.now(ZoneInfo("Asia/Seoul")).date()
            initDate = datetime.strptime(self.accountInitDate, "%Y.%m.%d.").date()
            
            updatePreiodList = {
                "month":relativedelta(months=1) - relativedelta(days=1), 
                "week":relativedelta(weeks=1) - relativedelta(days=1),
                "day":relativedelta(days=1) - relativedelta(days=1)
            }
            
            updatePreiod = updatePreiodList[self.updatePreiod]
            
            start = today - updatePreiod
            
            if start < initDate:
                self.Logger(message=f"조회 기간 오류. start({start})가 initDate({initDate})보다 작음.", error=ValueError("start Value Error"), error_code="PERIOD_INVALID")
                raise ValueError("start Value Error 조회기간 설정이 잘못되었습니다. today - updatePreiod는 initDate보다 커야 합니다.")

            start_str = start.strftime("%Y.%m.%d.")
            end_str = today.strftime("%Y.%m.%d.")

            try:
                RESULT_TRANSACTION = self.scrappingFunction.GET(
                    session=self.session,
                    bankSettingRecord=self.bankSettingRecord,
                    accountNumber=self.accountNumber,
                    accountPassword=self.accountPassword,
                    accountOwnerBirth=self.accountOwnerBirth,
                    startDate=start_str,
                    endDate=end_str
                )
            except requests.exceptions.HTTPError as http_err:
                 self.Logger(
                    message=f"HTTP 에러 발생 ({start_str}~{end_str})", 
                    error=http_err, 
                    error_code=http_err.response.status_code if http_err.response else "N/A"
                )
                 RESULT_TRANSACTION = [] 
            except Exception as period_e:
                self.Logger(
                    message=f"스크래핑 중 예상치 못한 오류 발생 ({start_str}~{end_str})", 
                    error=period_e, 
                    error_code="SCRAP_UNKNOWN"
                )
                RESULT_TRANSACTION = []

            
            RESULT_TRANSACTION = list(filter(lambda t: t["no"] not in remove_filter, RESULT_TRANSACTION))

            self.Logger(message="{}~{}에 대한 Scrapping 완료".format(start_str, end_str))
            self.Logger(message="완료 - {}건 불러오기 성공".format(len(RESULT_TRANSACTION)))

            NEW_DATA_COUNT = 0

            for transaction in RESULT_TRANSACTION:
                find_records = self.pocketbaseConn.collection('Transaction').get_full_list(query_params={
                    "filter": 'bank.id="{}" && no="{}" && datetime="{}" && money={}'.format(
                        self.bankSettingRecord, transaction["no"], transaction["datetime"], transaction["money"]
                    ), 
                    "expand":"bank"
                })

                if find_records != []:
                    continue
                
                self.pocketbaseConn.collection('Transaction').create(transaction)
                NEW_DATA_COUNT += 1
            
            self.Logger(message="완료 - {}건 업로드 성공".format(NEW_DATA_COUNT))
            
        except Exception as e:
            self.Logger(message="Update 함수 실행 중 오류 발생", error=e, error_code="FATAL_UPDATE")
            raise e


    def Remove(self, remove_filter=[]):
        try:
            removed_count = 0
            for target in remove_filter:
                
                target_record = self.pocketbaseConn.collection("Transaction").get_full_list(
                    query_params={
                        "filter": f'no = "{target}"'
                    }
                )
                
                for record in target_record:
                    self.pocketbaseConn.collection('Transaction').delete(record.id)
                    removed_count += 1
            
            self.Logger(message=f"Remove 완료 - 총 {removed_count}건 삭제 성공")

        except Exception as e:
            self.Logger(message="Remove 함수 실행 중 오류 발생", error=e, error_code="FATAL_REMOVE")
            raise e
