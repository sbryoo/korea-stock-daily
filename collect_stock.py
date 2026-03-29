import FinanceDataReader as fdr
import pandas as pd
import json
import os
from datetime import datetime

def collect_filtered_stocks_rich_data():
    print(f"--- [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AI 분석용 확장 데이터 수집 시작 ---")
    
    try:
        # 1. 실제 KRX 종목 리스트 가져오기
        df = fdr.StockListing('KRX')
        
        if df is None or df.empty:
            print("❌ 데이터를 가져오지 못했습니다.")
            return

        # 2. 데이터 수치화 및 정제 (확인된 컬럼명 반영)
        df['Ratio'] = pd.to_numeric(df['ChagesRatio'], errors='coerce').fillna(0)
        df['Cap'] = pd.to_numeric(df['Marcap'], errors='coerce').fillna(0)
        
        # 추가 수치 데이터 (AI가 기술적 분석을 하기 위함)
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce').fillna(0)     # 종가
        df['Open'] = pd.to_numeric(df['Open'], errors='coerce').fillna(0)       # 시가
        df['High'] = pd.to_numeric(df['High'], errors='coerce').fillna(0)       # 고가
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce').fillna(0)         # 저가
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)   # 거래량
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)   # 거래대금

        # 3. 필터링 조건 (사용자 요청 조건 유지)
        large_cap_threshold = 1_000_000_000_000
        large_condition = (df['Cap'] >= large_cap_threshold) & (df['Ratio'].abs() >= 3)
        small_condition = (df['Cap'] < large_cap_threshold) & (df['Ratio'].abs() >= 5)

        # 4. AI 전달용 상세 포맷팅 함수
        def format_for_ai(target_df):
            if target_df.empty: return []
            
            # AI가 분석하기 좋게 필드를 매핑
            formatted = []
            for _, row in target_df.iterrows():
                # 고가 대비 종가 위치 (윗꼬리 확인용: 1에 가까울수록 장마감까지 강세)
                tail_ratio = 0
                if (row['High'] - row['Low']) > 0:
                    tail_ratio = round((row['Close'] - row['Low']) / (row['High'] - row['Low']), 2)

                formatted.append({
                    "code": row['Code'],
                    "name": row['Name'],
                    "market": row['Market'],             # KOSPI / KOSDAQ / KONEX
                    "close": int(row['Close']),          # 현재가(종가)
                    "changes_ratio": row['Ratio'],       # 등락률
                    "volume": int(row['Volume']),        # 거래량
                    "amount": int(row['Amount']),        # 거래대금 (수급 확인용)
                    "marcap": int(row['Cap']),           # 시가총액
                    "ohlc": {                            # 캔들 모양 분석용
                        "open": int(row['Open']),
                        "high": int(row['High']),
                        "low": int(row['Low'])
                    },
                    "strength_score": tail_ratio,        # 가격 유지력(AI 참고지표)
                    "is_large_cap": row['Cap'] >= large_cap_threshold
                })
            return formatted

        # 5. 최종 데이터 구성
        result_data = {
            "metadata": {
                "base_date": "2026-03-27",
                "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_movers": len(df[large_condition]) + len(df[small_condition])
            },
            "large_cap_movers": format_for_ai(df[large_condition].sort_values(by='Ratio', ascending=False)),
            "mid_small_cap_movers": format_for_ai(df[small_condition].sort_values(by='Ratio', ascending=False))
        }

        # 6. 저장
        os.makedirs('data', exist_ok=True)
        with open("data/latest.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ AI용 확장 데이터 저장 완료! (총 {result_data['metadata']['total_movers']}종목)")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    collect_filtered_stocks_rich_data()
