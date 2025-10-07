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

# 임시메모. 설치

## Frontend 배포

### 1) frontend 빌드

```bash
cd Frontend
npm run dev
```

### 2) nginx 배포 준비

```bash
mv ./Frontend/dist /var/www/money-dist 
# Frontend 프로젝터 폴더 내 dist를 /var/www/money-dist로 이동
```

### 3) nginx sites 설정 변경

```bash
nano /etc/nginx/sites-enabled/default
# 실제 환경에서는 sites-available/default 수정 후 스위칭하기를...
```

```bash
server {
    listen 80;
    server_name money.busanqueeract.kr;
    return 301 https://$host$request_uri;
}


server {
    listen 443 ssl;
    server_name money.busanqueeract.kr;

    ssl_certificate /root/ssl/origin.crt;
    ssl_certificate_key /root/ssl/origin.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    root /var/www/money-dist;
    index index.html;

    # index.html 직접 요청은 그대로 파일 반환 (루프 방지)
    location = /index.html {
        try_files $uri =404;
    }

    # vue-router history 모드: 존재하지 않는 경로는 index.html로
    location / {
        try_files $uri /index.html;
    }

    # 정적 파일 캐시 비활성 (요청 시마다 받기)
    location ~* \.(?:ico|css|js|gif|jpe?g|png|woff2?|eot|ttf|svg|mp4)$ {
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
    }

    # favicon 없으면 로그 억제
    location = /favicon.ico {
       log_not_found off;
       access_log off;
    }
```

### 4) nginx 재시작
```bash
service nginx restart
```

## Backend 배포

### 1) Pocketbase 서비스 등록

미작성 - 단순 개발시에 필요한 것만 기재하도록 하였음.

```bash
nano /etc/systemd/system/money-api.service
```

```bash
[Unit]
Description = pocketbase for money

[Service]
Type           = simple
User           = root
Group          = root
LimitNOFILE    = 4096
Restart        = always
RestartSec     = 5s
StandardOutput = append:/root/money-api/errors.log
StandardError  = append:/root/money-api/errors.log
ExecStart      = /root/money-api/pocketbase serve --http=127.0.0.1:5090

[Install]
WantedBy = multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start money-api 
sudo systemctl status money-api # 상태 확인
sudo systemctl enable money-api
```


### 2) Nginx 등록

```bash
server {
    listen 80;
    server_name money-api.busanqueeract.kr;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name money-api.busanqueeract.kr;

    ssl_certificate /root/ssl/origin.crt;
    ssl_certificate_key /root/ssl/origin.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    location / {
        proxy_hide_header Access-Control-Allow-Origin;
        proxy_hide_header Access-Control-Allow-Credentials;
        proxy_hide_header Access-Control-Allow-Methods;
        proxy_hide_header Access-Control-Allow-Headers;

        set $cors_origin "";

        if ($http_origin = "https://money.busanqueeract.kr") {
            set $cors_origin "https://money.busanqueeract.kr";
        }

        if ($http_origin = "https://busanqueeract.kr") {
            set $cors_origin "https://busanqueeract.kr";
        }

        if ($http_origin = "https://www.busanqueeract.kr") {
            set $cors_origin "https://www.busanqueeract.kr";
        }
        if ($http_origin = "http://localhost:5173") {
            set $cors_origin "http://localhost:5173";
        }

        if ($cors_origin != "") {
            add_header 'Access-Control-Allow-Origin' "$cors_origin" always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE, PATCH' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        }

        if ($request_method = OPTIONS) {
            add_header 'Access-Control-Allow-Origin' "$cors_origin" always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE, PATCH' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            add_header 'Access-Control-Max-Age' 1728000 always;
            add_header 'Content-Type' 'text/plain; charset=UTF-8' always;
            add_header 'Content-Length' 0 always;
            return 204;
        }

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        proxy_read_timeout 360s;

        proxy_pass http://127.0.0.1:5090;
    }
}
```

```bash
service nginx restart
```


## Scrapper 배포

미작성 - 단순 개발시에 필요한 것만 기재하도록 하였음.
setting.py 설정 필수

### 패키지 설치

```bash
cd Scrapper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 테스트
```
source venv/bin/activate
python main.py
```


### 서비스 등록

```bash
nano /etc/systemd/system/money-scrapper.service
```

```bash
[Unit]
Description = scrapper for money

[Service]
Type           = simple
User           = root
Group          = root
LimitNOFILE    = 4096
Restart        = always
RestartSec     = 5s
StandardOutput = append:/root/money-scrapper/errors.log
StandardError  = append:/root/money-scrapper/errors.log
ExecStart      = /root/money-scrapper/venv/bin/python /root/money-scrapper/main.py

[Install]
WantedBy = multi-user.target
```


```bash
sudo systemctl daemon-reload
sudo systemctl start money-scrapper 
sudo systemctl status money-scrapper # 상태 확인
sudo systemctl enable money-scrapper
```
