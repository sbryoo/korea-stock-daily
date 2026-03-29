import FinanceDataReader as fdr
import pandas as pd
import json
from datetime import datetime
import os

def save_stock_data():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        # 1. 데이터 수집
        df_krx = fdr.StockListing('KRX')
        df_krx['ChangesRatio'] = pd.to_numeric(df_krx['ChangesRatio'], errors='coerce')
        df_sorted = df_krx.sort_values(by='MarCap', ascending=False).reset_index(drop=True)

        # 2. 필터링 (대형주 1~100위 3%, 중소형주 101위~ 5%)
        large_cap = df_sorted.iloc[:100]
        mid_small_cap = df_sorted.iloc[100:]
        
        target_large = large_cap[large_cap['ChangesRatio'].abs() >= 3.0]
        target_mid_small = mid_small_cap[mid_small_cap['ChangesRatio'].abs() >= 5.0]

        # 3. JSON 구조 생성
        result_data = {
            "date": today,
            "large_cap_movers": target_large[['Code', 'Name', 'ChangesRatio', 'MarCap']].to_dict(orient='records'),
            "mid_small_cap_movers": target_mid_small[['Code', 'Name', 'ChangesRatio', 'MarCap']].to_dict(orient='records')
        }

        # 4. 파일 저장 (날짜별 & 최신본)
        os.makedirs('data', exist_ok=True)
        
        # 날짜별 파일
        with open(f"data/stock_{today}.json", 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)
            
        # AI 접근용 최신 파일 (latest.json)
        with open(f"data/latest.json", 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)
            
        print(f"Update complete for {today}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    save_stock_data()
