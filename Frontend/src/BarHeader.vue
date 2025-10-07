<template>
<div class="header">
    <div class="info none-select">
        
        <div class="service">
            <span class="logo-area">
                <img class="logo" src="./logo.png" alt="모두의결산 로고" />
            </span>
        </div>
        
        <div class="user">
            
            <div class="auth-info-display" v-if="loginStatus">
                <span class="auth-user-name"> {{ organizationName }}</span>
                <span class="auth-user-email"> {{ loginInfo.name }}님({{ permission }})</span>

            </div>
            
            <div class="status">
                <span :class="['button', loginStatus ? 'btn-logout' : 'btn-login']" 
                      @click="loginStatus ? Logout() : openModal()">
                    <i :class="['bi', loginStatus ? 'bi-box-arrow-right' : 'bi-person-fill-lock']"></i> 
                    {{ loginStatus ? '로그아웃' : '로그인' }}
                </span>
            </div>

        </div>
    </div>
    
    <div class="modal-backdrop" v-if="isModalOpen" @click.self="closeModal()">
        <div class="login-modal">
            <div class="modal-header">
                <h2>
                    <i class="bi bi-person-circle"></i> 
                    <span>로그인</span>
                </h2>
                <button class="close-button" @click="closeModal()"><i class="bi bi-x-lg"></i></button>
            </div>
            
            <div class="modal-body">
                <p class="description">
                    {{ organizationName }} DB에 접근하기 위해 로그인이 필요합니다
                </p>
                
                <!-- 에러 메시지 표시 영역 -->
                <div v-if="errorMessage" class="error-message">
                    <i class="bi bi-exclamation-triangle-fill"></i> {{ errorMessage }}
                </div>

                <!-- 1. 구글 로그인 영역 (유일한 로그인 수단) -->
                <div>
                    <span class="button btn-google-login modal-submit-button" @click="LoginWithGoogle">
                        <i class="bi bi-google"></i> 구글로 로그인 
                    </span>
                </div>
                
            </div>
        </div>
    </div>
    </div>
</template>

<script>
import PocketBase from 'pocketbase';
// PocketBase SDK 초기화 (전역 변수 __POCKETBASE_API_BASE_URL__ 사용)
const pb = new PocketBase(typeof __POCKETBASE_API_BASE_URL__ !== 'undefined' ? __POCKETBASE_API_BASE_URL__ : 'http://127.0.0.1:8090');

export default {
    props: ['loginStatus', 'loginInfo', 'organizationName'],
    
    data(){
        return {
            isModalOpen: false, 
            errorMessage: '', // 에러 메시지
        }
    },
    computed: {
        permission() {
            switch(this.loginInfo.permission){
                case "viewer":
                    return "일부권한 : 편집 불가"
                case "editor":
                    return "전체권한"
            }
            
        }
    },
    methods: {
        // 모달 열기/닫기
        openModal() {
            if (!this.loginStatus) {
                this.isModalOpen = true;
                this.errorMessage = '';
            }
        },
        
        closeModal() {
            this.isModalOpen = false;
            this.errorMessage = '';
        },

        // 1. Google OAuth2 로그인 처리 (주요 로그인 방법)
        async LoginWithGoogle() {
            this.errorMessage = '';
            try {
                // PocketBase OAuth2 인증 시작
                const authData = await pb.collection('users').authWithOAuth2({ provider: 'google' });
                
                // OAuth2 성공 후 토큰 확인
                if (pb.authStore.isValid) {
                    // 로그인 성공 처리
                    this.closeModal();
                    this.$emit('update');
                }

            } catch (error) {
                // 사용자가 팝업을 닫거나, 인증에 실패했을 때 에러 처리
                this.errorMessage = "Google 로그인에 실패했거나 취소되었습니다.";
                console.error("구글 로그인 오류:", error);
            }
        },

        // 로그아웃 처리
        async Logout(){
            if(this.loginStatus == false) return;
            this.errorMessage = '';

            try {
                pb.authStore.clear()
                this.$emit('update')
                console.log("로그아웃에 성공했습니다.") 
            } catch(error) {
                this.errorMessage = "로그아웃에 실패했습니다: " + error.message;
            }
        },
    },

    watch: {
        isModalOpen(isOpen) {
            document.body.style.overflow = isOpen ? 'hidden' : '';
            if (isOpen) {
                // 모달이 열릴 때 상태 초기화
                this.errorMessage = '';
            }
        }
    },
}
</script>

<style scoped>
/* -------------------- 기존 스타일 유지 -------------------- */
:root {
    --strong-color: #1a202c; /* Dark text/primary button */
    --medium-color: #4a5568; /* Subtext/borders */
    --light-color: #f7fafc; /* Light background/input background */
    --none-color: white;
    --danger-color: #e53e3e;
    --strong-color-rgb: 26, 32, 44;
}

.none-select {
  user-select: none;
  -moz-user-select: none;
  -webkit-user-drag: none;
}

.info {
    height: 100%;
    width: 100%;
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    align-items: center; 
    padding: 20px 0;
}

.service {
    display: flex;
    align-items: center;
    gap: 15px; 
    flex: 4;
}

.logo-area {
    display: flex;
    align-items: center;
    height: 35px; 
    flex-shrink: 0;
}

img.logo {
    max-height: 100%; 
    width: auto;
}

.user {
    display: flex;
    flex-direction: row; 
    justify-content: flex-end; 
    align-items: center;
    gap: 20px;
    flex: 1; 
    min-width: 200px;
}

.auth-info-display {
    display: flex;
    flex-direction: column;
    align-items: flex-end; 
    gap: 2px;
    flex-shrink: 1; 
}

.auth-user-name {
    font-weight: 700;
    font-size: 16px;
    color: var(--strong-color);
    white-space: nowrap;
}

.auth-user-email {
    font-weight: 500;
    font-size: 14px;
    color: var(--medium-color);
    white-space: nowrap;
}

.status {
    flex-shrink: 0;
}

.status > .button {
    font-weight: 700;
    cursor: pointer;
    font-size: 14px;
    padding: 6px 15px;
    gap: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 5px;
    transition: all 0.2s ease;
}

.status > .btn-login {
    color: var(--none-color, white);
    background-color: var(--strong-color); 
}
.status > .btn-login:hover {
    background-color: var(--medium-color);
}

.status > .btn-logout {
    color: var(--strong-color, #333);
    background-color: var(--light-color, #f0f0f0); 
    border: 1px solid var(--medium-color, #ccc);
}
.status > .btn-logout:hover {
    background-color: var(--medium-color, #ccc);
}


/* -------------------- 모달 디자인 개선 -------------------- */
.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw; 
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    background-color: rgba(0, 0, 0, 0.7); /* 배경을 조금 더 어둡게 */
}

.login-modal {
    background: var(--none-color, white); 
    padding: 30px 40px; /* 좌우 패딩을 늘려 여백 확보 */
    border-radius: 12px; /* 모서리 곡률 증가 */
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4); /* 그림자 강화 */
    width: 380px; 
    max-width: 90%;
    transform: translateY(0); 
    color: var(--strong-color); 
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 0;
    border-bottom: 1px solid var(--medium-color);
}

.modal-header h2 {
    font-size: 28px; /* 폰트 크기 증가 */
    font-weight: 900;
    color: var(--strong-color);
    display: flex;
    align-items: center;
    gap: 10px;
}

.close-button {
    background: none;
    border: none;
    font-size: 1.5em; /* 아이콘 크기 약간 줄임 */
    color: var(--medium-color);
    cursor: pointer;
    transition: color 0.2s;
}

.close-button:hover {
    color: var(--danger-color, #f44336);
}

.modal-body {
    display: flex;
    flex-direction: column;
    gap: 20px; /* 요소 간 간격 증가 */
}

.modal-body .description {
    font-size: 16px; /* 폰트 크기 약간 증가 */
    font-weight: 500;
    color: var(--strong-color);
    margin-bottom: 5px;
    line-height: 1.5;
    text-align: left; /* 중앙 정렬 */
}

.modal-submit-button {
    margin-top: 5px;
    width: 100%;
    height: 52px; /* 버튼 높이 증가 */
    font-size: 18px; /* 폰트 크기 증가 */
    font-weight: 700;
    border-radius: 8px; /* 버튼 모서리 곡률 증가 */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 버튼에 은은한 그림자 추가 */
    transition: transform 0.1s ease, box-shadow 0.2s;
}
.modal-submit-button:hover {
    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}
.modal-submit-button:active {
    transform: scale(0.99);
}

/* 구글 로그인 버튼 스타일 */
.btn-google-login {
    background-color: #4285f4; /* Google Blue */
    color: white;
    margin-top: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}
.btn-google-login:hover {
    background-color: #357ae8;
}

/* 에러 메시지 스타일 */
.error-message {
    padding: 12px; /* 패딩 증가 */
    background-color: #fff0f0; /* 더 연한 배경 */
    border: 1px solid #ff4d4f; /* 경고 레드 */
    color: #cc0000;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
}


</style>
