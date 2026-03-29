import FinanceDataReader as fdr
import pandas as pd
import json
import os

def save_stock_data():
    try:
        # 1. 상장 종목 리스트 무조건 가져오기
        df_krx = fdr.StockListing('KRX')
        
        # 2. 데이터가 있는지 확인 (비어있으면 강제로 샘플 데이터 생성)
        if df_krx.empty:
            print("No data from FDR, using sample data for testing")
            target_large = [{"Code": "005930", "Name": "삼성전자", "ChangesRatio": 1.5, "MarCap": 400000000000000}]
            target_mid_small = []
        else:
            # 시총 순 정렬 후 상위 10개만 무조건 추출
            df_sorted = df_krx.sort_values(by='MarCap', ascending=False).head(10)
            target_large = df_sorted.to_dict(orient='records')
            target_mid_small = []

        # 3. JSON 구조 생성
        result_data = {
            "date": "2026-03-27", # 테스트용 날짜 고정
            "status": "Force generated for testing",
            "large_cap_movers": target_large,
            "mid_small_cap_movers": target_mid_small
        }

        # 4. 폴더 강제 생성 및 저장
        os.makedirs('data', exist_ok=True)
        
        # 파일 두 개 생성
        for filename in ["stock_test.json", "latest.json"]:
            with open(f"data/{filename}", 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=4)
            
        print("!!! Success: Data saved to data/ folder !!!")

    except Exception as e:
        print(f"Error detail: {e}")

if __name__ == "__main__":
    save_stock_data()
