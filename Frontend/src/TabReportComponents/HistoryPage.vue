<template>
    <div class="PAGE_LANDSCAPE" 
         v-for="(page, pageIndex) in pagedAssetsResults" 
         :key="pageIndex">
        
        <div class="PAGE_HEADER">
            <div class="page-meta">
                <span class="subtitle">{{ organizationName }}</span>
                <span class="title">수입지출내역서</span>
                <span class="description">{{ formattedStartDate }} ~ {{ formattedEndDate }}</span>
            </div>
            <div class="page-info">
                <span class="currency-unit">(단위: 원)</span>
                <span class="page-number">총 {{ pagedAssetsResults.length }}쪽 중 {{ pageIndex + 1 }}번째</span>
            </div>
        </div>
        
        <div class="PAGE_CONTENT">
            <table>
                <thead>
                    <tr>
                        <th style="width:10%">거래일시</th> 
                        <th style="width:3%">관</th> 
                        <th style="width:4%">항</th>
                        <th style="width:23%">목</th>
                        <th style="width:10%">세목</th>
                        <th style="width:34%">장부내용</th> 
                        <th style="width:8%">장부금액</th>
                        <th style="width:8%">지출증빙</th> </tr>
                </thead>
                <tbody>
                    <tr v-for="(record, recordIndex) in page.items" :key="recordIndex" class="transaction-row">
                        <td>{{ record.datetime }}</td>
                        <td>{{ record.gwan }}</td> 
                        <td><AssetsLabel :asset-type="'Hang'" :asset="record.hang"/></td>
                        <td><AssetsLabel :asset-type="'Mok'" :asset="record.mok"/></td>
                        <td><AssetsLabel :asset-type="'Saemok'" :asset="record.saemok"/></td>
                        <td class="content-cell">{{ record.content }}</td>
                        <td class="amount-cell" :class="{'income-amount': record.type === '수입', 'expense-amount': record.type === '지출'}">
                            {{ formatCurrency(record.money) }}
                        </td>
                        <td class="status-cell">{{ record.receipt }}</td> 
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>



<script>
import './style.css'
import AssetsLabel from './AssetsLabel.vue';

export default {
    components: {
        AssetsLabel
    },

    props:[
        'startYearMonth', 
        'endYearMonth', 
        'organizationName', 
        'hangList', 
        'mokList', 
        'ledgerList',
        'gwanList', // 사용되지 않음
        'semokList' // 사용되지 않음
    ],

    data() {
        return {
            TRANSACTION_LIST: [], 
        }
    },
    
    watch: {
        // ledgerList에 expand된 데이터가 있다고 가정하고, 변경될 때마다 처리
        ledgerList: { 
            immediate: true, 
            handler(newVal) {
                if (newVal && newVal.length > 0) {
                    this.prepareTransactionList(); 
                } else if (newVal && newVal.length === 0) {
                    this.TRANSACTION_LIST = [];
                }
            }
        },
    },

    computed:{
        // ... (formattedStartDate, formattedEndDate 유지) ...
        formattedStartDate() {
            if (!this.startYearMonth) return '';
            const s = this.startYearMonth.toString();
            const year = s.substring(0, 4);
            const month = parseInt(s.substring(4, 6));
            return `${year}년 ${month}월`;
        },

        formattedEndDate() {
            if (!this.endYearMonth) return '';
            const s = this.endYearMonth.toString();
            const year = s.substring(0, 4);
            const month = parseInt(s.substring(4, 6));
            return `${year}년 ${month}월`;
        },

        // 거래 행 단위로 페이지네이션 (25행)
        pagedAssetsResults() {
            const MAX_ROWS_PER_PAGE = 10; 
            const pages = [];
            
            for (let i = 0; i < this.TRANSACTION_LIST.length; i += MAX_ROWS_PER_PAGE) {
                pages.push({
                    items: this.TRANSACTION_LIST.slice(i, i + MAX_ROWS_PER_PAGE)
                });
            }
            
            return pages;
        }
    },

    methods: {
        formatCurrency(number) {
            if (number === undefined || number === null) return '0';
            return number.toLocaleString('ko-KR');
        },
        
        // 거래일시를 YYYY-MM-DD HH:MM 형식으로 포매팅
        formatDateTime(dateTimeNum) {
            if (!dateTimeNum) return '';
            const s = String(dateTimeNum).padStart(12, '0');
            const Y = s.slice(0, 4);
            const M = s.slice(4, 6);
            const D = s.slice(6, 8);
            const H = s.slice(8, 10);
            const m = s.slice(10, 12);
            return `${Y}-${M}-${D} ${H}:${m}`;
        },
        
        // 📌 수정: Ledger Record의 expand 필드를 직접 사용하여 데이터 가공
        prepareTransactionList() {
            if (!this.ledgerList || this.ledgerList.length === 0) {
                this.TRANSACTION_LIST = [];
                return;
            }
            
            const finalTransactionList = this.ledgerList
                // 유효한 거래와 확장 데이터가 있는 경우만 필터링 (선택적)
                .filter(record => record.expand) 
                .map(record => {
                    // 📌 요청하신 데이터 구조를 그대로 사용
                    function receipt_count(){
                        if(record.not_need_receipt) return '불요'
                        if(record.receipt.length > 0) return `${record.receipt.length}건`
                        if(record.receipt.length == 0) return `미등록`
                    }
                    return {
                        datetime: this.formatDateTime(record.expand.transaction.datetime), 
                        content: record.reason || '', 
                        gwan: record.gwan,
                        hang: record.expand.hang,
                        mok: record.expand.mok,
                        saemok: record.expand.saemok,
                        money: record.money || 0,
                        type: record.add_type,
                        receipt: receipt_count()
                    };
                });
            
            // 거래일시(datetime 필드의 YYYY-MM-DD HH:MM 문자열) 기준으로 정렬
            finalTransactionList.sort((a, b) => a.datetime.localeCompare(b.datetime));
            
            this.TRANSACTION_LIST = finalTransactionList;
        },

    }
}
</script>