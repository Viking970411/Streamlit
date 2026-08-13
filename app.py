# 1. 데이터 만들기
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import koreanize_matplotlib


df = pd.DataFrame({
    "직원": ["김민수", "이영희", "박철수", "최지수", "정하늘", "한유진"],
    "부서": ["영업부", "개발부", "영업부", "개발부", "영업부", "개발부"],
    "매출": [500, 300, 700, 400, 600, 800]
})

# 2. 사이드바 필터
st.sidebar.title('조회조건')
dept = st.sidebar.selectbox('부서를 선택하세요',['전체','영업부','개발부'])
min_sales, max_sales = st.sidebar.slider('최소 매출을 선택하세요.',min_value=0,max_value=1000,value=(0,1000),step=50)

# 3. 데이터 필터링
if dept != '전체' :
    result = df[df['부서']==dept]
else :
    result = df    

result = result[result['매출']>= min_sales]

st.write(result)