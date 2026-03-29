import FinanceDataReader as fdr
import pandas as pd
import json
from datetime import datetime
import os

def save_stock_data():
    target_date = "2026-03-27" 
    
    try:
        # 1. 상장 종목 리스트 가져오기
        df_krx = fdr.StockListing('KRX')
        
        # 등락률 수치화 및 정렬
        df_krx['ChangesRatio'] = pd.to_numeric(df_krx['ChangesRatio'], errors='coerce').fillna(0)
        df_sorted = df_krx.sort_values(by='MarCap', ascending=False).reset_index(drop=True)

        # 2. 강제 추출 (조건 상관없이 상위 10개씩)
        # 데이터가 있는지 확인하기 위해 필터링을 풀고 가져옵니다.
        target_large = df_sorted.iloc[:10].copy() # 대형주 1~10위
        target_mid_small = df_sorted.iloc[100:110].copy() # 중소형주 일부

        # 3. JSON 구조 생성
        result_data = {
            "date": target_date,
            "status": "Force generated for testing",
            "large_cap_movers": target_large[['Code', 'Name', 'ChangesRatio', 'MarCap']].to_dict(orient='records'),
            "mid_small_cap_movers": target_mid_small[['Code', 'Name', 'ChangesRatio', 'MarCap']].to_dict(orient='records')
        }

        # 4. 폴더 생성 및 저장
        os.makedirs('data', exist_ok=True)
        
        file_list = [f"stock_{target_date}.json", "latest.json"]
        for filename in file_list:
            with open(f"data/{filename}", 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=4)
            
        print(f"!!! Success: Data saved for {target_date} !!!")

    except Exception as e:
        print(f"Error detail: {e}")

if __name__ == "__main__":
    save_stock_data()
