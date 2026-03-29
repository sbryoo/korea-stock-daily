import FinanceDataReader as fdr
import pandas as pd
import json
import os
from datetime import datetime

def collect_daily_stocks():
    # 1. 실행 시점의 오늘 날짜 가져오기
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"--- [{today_str}] 데일리 시장 분석 및 데이터 수집 시작 ---")
    
    try:
        # 2. KRX 종목 리스트 가져오기
        df = fdr.StockListing('KRX')
        
        if df is None or df.empty:
            print("❌ 데이터를 가져오지 못했습니다.")
            return

        # 3. 데이터 수치화 및 정제 (확인된 컬럼명 반영)
        df['Ratio'] = pd.to_numeric(df['ChagesRatio'], errors='coerce').fillna(0)
        df['Cap'] = pd.to_numeric(df['Marcap'], errors='coerce').fillna(0)
        
        # 추가 수치 데이터 (AI 기술적 분석용)
        for col in ['Close', 'Open', 'High', 'Low', 'Volume', 'Amount']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 4. 필터링 조건 (사용자 기준 유지)
        large_cap_threshold = 1_000_000_000_000
        large_condition = (df['Cap'] >= large_cap_threshold) & (df['Ratio'].abs() >= 3)
        small_condition = (df['Cap'] < large_cap_threshold) & (df['Ratio'].abs() >= 5)

        # 5. AI 전달용 상세 포맷팅 함수
        def format_for_ai(target_df):
            if target_df.empty: return []
            formatted = []
            for _, row in target_df.iterrows():
                # 가격 유지력 점수 계산 (고가-저가 대비 종가 위치)
                tail_ratio = 0
                if (row['High'] - row['Low']) > 0:
                    tail_ratio = round((row['Close'] - row['Low']) / (row['High'] - row['Low']), 2)

                formatted.append({
                    "code": row['Code'],
                    "name": row['Name'],
                    "market": row['Market'],
                    "close": int(row['Close']),
                    "changes_ratio": row['Ratio'],
                    "volume": int(row['Volume']),
                    "amount": int(row['Amount']),
                    "marcap": int(row['Cap']),
                    "ohlc": {
                        "open": int(row['Open']),
                        "high": int(row['High']),
                        "low": int(row['Low'])
                    },
                    "strength_score": tail_ratio,
                    "is_large_cap": row['Cap'] >= large_cap_threshold
                })
            return formatted

        # 6. 최종 데이터 구성
        result_data = {
            "metadata": {
                "base_date": today_str, # 매일 실행되는 시점의 날짜
                "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_movers": len(df[large_condition]) + len(df[small_condition])
            },
            "large_cap_movers": format_for_ai(df[large_condition].sort_values(by='Ratio', ascending=False)),
            "mid_small_cap_movers": format_for_ai(df[small_condition].sort_values(by='Ratio', ascending=False))
        }

        # 7. 폴더 생성 및 저장
        os.makedirs('data/history', exist_ok=True) # 히스토리 폴더 추가 생성
        
        # 최신본 저장 (latest.json)
        with open("data/latest.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)
            
        # 날짜별 백업 저장 (data/history/2026-03-29.json)
        history_path = f"data/history/{today_str}.json"
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ [{today_str}] 데이터 저장 완료! (총 {result_data['metadata']['total_movers']}종목)")
        print(f"📍 최신 파일: data/latest.json")
        print(f"📍 히스토리: {history_path}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    collect_daily_stocks()
