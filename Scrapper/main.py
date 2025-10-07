import signal, sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from pocketbase import PocketBase
import setting 

import bank_scrapper.Job as Job 
from datetime import datetime
from zoneinfo import ZoneInfo

# ===============================================
# 1. 스케줄러 및 실행자 설정
# ===============================================

sched = BlockingScheduler(
    executors={
        "default": ThreadPoolExecutor(8)
    },
    job_defaults={
        "max_instances": 1, 
        "coalesce": True 
    }
)

def get_pocketbase_client():
    """PocketBase 클라이언트를 생성하고 인증을 수행합니다."""
    try:
        pocketbase = PocketBase(setting.PB_URL)
        pocketbase.collection("users").auth_with_password(setting.PB_USER, setting.PB_PASS)
        return pocketbase
    except Exception as e:
        print(f"FATAL: PocketBase 연결 또는 인증 실패 - {e}")
        raise e

def make_scrapper_job(bank_config):

    def run_scrapper():
        
        job_id = bank_config['JOB_ID']
        current_time = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[{current_time}][{job_id}] - Scrapper Functions: start")
        scrapper = None
        
        try:    
            pocketbase = get_pocketbase_client()
            
            scrapper = Job.Scrapper(
                bankType=bank_config['BANK_TYPE'],
                bankSettingRecord=bank_config['BANK_SETTING_RECORD_ID'], 
                accountNumber=bank_config['ACCOUNT_NUMBER'], 
                accountPassword=bank_config['ACCOUNT_PASSWORD'], 
                accountOwnerBirth=bank_config['ACCOUNT_OWNER_BIRTH'], 
                accountInitDate=bank_config['ACCOUNT_INIT_DATE'], 
                updatePreiod=bank_config['UPDATE_PERIOD'], 
                pocketbaseConn=pocketbase
            )
            
            scrapper.Update(remove_filter=bank_config.get('REMOVE_LIST', []))
            print(f"[{current_time}][{job_id}] - Scrapper Functions: ok end")

        except Exception as e: 
            if scrapper:
                scrapper.Logger(
                    message=f"스케줄러 작업 실행 중 오류 발생 (Update 실패)",
                    error=e,
                    error_code="SCHED_FAIL"
                )
            
            print(f"[{current_time}][{job_id}] - Scrapper Functions: failed - {e}")

    return run_scrapper

def _shutdown(signum, frame):
    """SIGTERM/SIGINT 신호를 받아 스케줄러를 안전하게 종료합니다."""
    print(f"\n[SIGNAL {signum}] -> Received shutdown signal.")
    print("Shutting down scheduler...")
    sched.shutdown(wait=False)
    sys.exit(0)

# ===============================================
# 2. 메인 실행 루틴
# ===============================================

if __name__ == "__main__":
    
    print("--------------------------------------------------")
    print(f"Total {len(setting.BANK_ACCOUNTS)} bank accounts found to monitor.")
    
    for config in setting.BANK_ACCOUNTS:
        job_id = config['JOB_ID']
        interval = config.get('INTERVAL_SECONDS', setting.UPDATE_INTERVAL_SECONDS)
        
        print(f"\n[Initial Run - {job_id}]: {config['BANK_TYPE']} 계정 업데이트를 즉시 시작합니다.")
        make_scrapper_job(config)()
        print(f"[Initial Run - {job_id}]: 완료.")
        
        sched.add_job(
            make_scrapper_job(config), 
            "interval", 
            seconds=interval, 
            id=job_id, 
            replace_existing=True
        )
        print(f"Scheduler ADD - Job: {job_id}")
        print(f"+ registered Job ID={job_id}, every {interval} seconds")

    print("--------------------------------------------------")
    
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)
    
    try:
        print("--------------------------------------------------")
        print("BlockingScheduler START. Press Ctrl+C to stop.")
        print("--------------------------------------------------")
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass