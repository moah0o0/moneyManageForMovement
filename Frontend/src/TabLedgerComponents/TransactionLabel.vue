<template>
    <div class="transaction-number-list" v-if="transaction != null && bankSetting != null">
        <span class="label background transaction-number" @click="modalOpen = true">
            <i class="bi bi-cash"></i> <div class="number">{{ bankSetting.NickName }}({{ transaction.no }})</div>
        </span>
        <div :class="transaction == null ? 'modal disable' : 'modal'" v-if="modalOpen == true">
            <div class="modal-content transaction-info">

                <div class="meta">
                    <span class="title">거래내역 원본</span>
                    <span class="description">은행에서 불러온 세부사항을 확인하세요</span>
                </div>

                <div class="data">
                    <div class="data-line">
                        <span class="key">구분</span>
                        <span class="value">{{ transaction.type == "수입" ? "입금" : "출금" }}</span>
                    </div>
                    <div class="data-line">
                        <span class="key">일시</span>
                        <span class="value">{{ datetimeFormatter(transaction.datetime) }}</span>
                    </div>
                    <div class="data-line">
                        <span class="key">적요</span>
                        <span class="value">{{ transaction.description }}</span>
                    </div>
                    <div class="data-line">
                        <span class="key">금액</span>
                        <span class="value">{{ transaction.money.toLocaleString() }}</span>
                    </div>
                </div>
                <div class="data background">
                    <div class="data-line">
                        <span class="key">거래번호</span>
                        <span class="value">{{ transaction.no }}</span>
                    </div>
                    <div class="data-line">
                        <span class="key">계좌별칭</span>
                        <span class="value">{{ bankSetting.NickName }}</span>
                    </div>
                    <div class="data-line">
                        <span class="key">계좌은행</span>
                        <span class="value">{{ bankSetting.BankType }}</span>
                    </div>
                    <div class="data-line">
                        <span class="key">계좌번호</span>
                        <span class="value">{{ bankSetting.AccountNumber }}</span>
                    </div>
                </div>
                <button class="close-btn" @click="modalOpen = false">
                    <i class="bi bi-x-square-fill"></i>창 닫기
                </button>
            </div>
        </div>
    </div>


</template>

<style scoped>

.transaction-info {
    width: 450px;
    height: 500px;
    
    border-radius: 10px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.5);

    padding:50px;
    
    display: flex;
    flex-direction: column;
    justify-content: center;

    gap: 30px;
}

.transaction-info > .meta {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.transaction-info > .meta > span.title {
    font-size: 24px;
    font-weight: 800;
}

.transaction-info > .meta > span.description {
    font-size: 16px;
    font-weight: 500;
}


.transaction-info > .data {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.transaction-info > .data.background {
    border: 1px solid var(--medium-color);
    padding: 20px 20px;
    box-sizing: border-box;
}   

.transaction-info > .data > .data-line {
    display: flex;
    flex-direction: row;
    gap: 20px;
    box-sizing: border-box;
}

.transaction-info > .data > .data-line > span.key {
    font-size: 16px;
    font-weight: 800;
}

.transaction-info > .data > .data-line > span.value {
    font-size: 16px;
    font-weight: 500;
}

button.close-btn {
    height: 40px;
    border: unset;
    background-color: var(--light-color);
    padding: 5px 20px;
    
    display: flex;
    gap: 8px;

    align-items: center;
    font-weight: 600;
    font-size: 14px;

    justify-content: center;

    border-radius: 10px;

    transition: all 0.25s ease;
}

button.close-btn > i {
    font-size: 12px;
    transition: transform 0.25s ease;
}

button.close-btn:hover {
    cursor: pointer;
    background-color: var(--danger-color);
    color: white;
}

button.close-btn:hover > i {
    transform: rotate(90deg);
}



.transaction-number-list {
    display: flex;
    gap: 10pt;
    flex-wrap: wrap;
    margin-top:10px;
    margin-bottom:10px;

}

.transaction-number {
    cursor: pointer;
}

.transaction-number > .number{
    text-align: left;
    font-size: 0.8em;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis;
}



</style>

<script>
import PocketBase from 'pocketbase';
const pb = new PocketBase(__POCKETBASE_API_BASE_URL__);


export default {
    props: ['transaction'],

    data(){
        return {
            modalOpen: false,
            bankSetting: null
        }
    },
    async mounted(){
        window.addEventListener('keydown', this.closeModal)
        await this.getBankSetting()
    },

    beforeUnmount(){
        window.removeEventListener('keydown', this.closeModal)
    },

    methods: {
        async getBankSetting(){
            const bankSetting = await pb.collection("BankSetting").getOne(this.transaction.bank, {requestKey: null})
            this.bankSetting = bankSetting
        },

        datetimeFormatter(str){
            str = String(str)
            return str.substring(0, 12).replace(/(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})/,"$1-$2-$3 $4:$5")
        },

        closeModal(e) {
            if (e.key === 'Escape') {
                this.modalOpen = false
            }
        }
    }

}
</script>
