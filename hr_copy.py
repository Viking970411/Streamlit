#과제
# KPI3개, 그래프 2개
#챌린지 : 사이드바 필터, 그래프 증가

# KPI 출력
#print(f'전체 직원 수: {total_employees:,}명')
#print(f'퇴직자 수: {total_attritions:,}명')
#print(f'전체 퇴직률: {overall_rate:.1f}%')


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

st.title("HR 퇴사율")

# 1. 데이터 만들기
df= pd.read_csv('HR Data.csv')  

using_columns = [
    '퇴직여부', '나이', '성별', '출장빈도', '부서', '집과의거리', '전공',
    '업무환경만족도', '업무참여도', '업무만족도', '결혼여부', '월급여',
    '일한회사수', '야근정도', '급여증가분백분율', '스톡옵션정도',
    '근속연수', '현재역할년수', '마지막승진년수'
]

df.isnull().sum()


hr = df[using_columns].copy()

hr['퇴직'] = hr['퇴직여부'].map({'No': 0, 'Yes': 1}).astype('int8')

hr['연령대'] = pd.cut(
    hr['나이'],
    bins=[0, 29, 39, 49, 59, 100],
    labels=['20대 이하', '30대', '40대', '50대', '60대 이상']
)


def attrition_summary (data, group_column) :
    result = data.groupby(group_column,observed=True).agg(직원수=('퇴직','size'),
                                    퇴직자수 = ('퇴직','sum'),
                                    퇴직율 = ('퇴직','mean')).reset_index()
    result['퇴직율'] = (result['퇴직율']*100).round(1)
    return result.sort_values('퇴직율',ascending=False)

age_result = attrition_summary(hr,'연령대')

#사이드바

st.sidebar.header("조회 조건")

department = st.sidebar.selectbox("연령대를 선택하세요.", ["전체", "20대 이하", "30대",'40대','50대','60대 이상'])
off_record = st.sidebar.slider("퇴직율을 선택하세요.", min_value=0, max_value=20000, value=0, step=100)


result = hr[hr["월급여"] >= off_record]

if department != "전체":
    result = result[result["연령대"] == department]


#kpi 3개

total_employees = len(hr)
total_attritions = result['퇴직'].sum()
overall_rate =round(result['퇴직'].mean() *100,1)

col1, col2, col3 = st.columns(3)
col1.metric(label='총 직원수', value=f'{total_employees}명')
col2.metric(label='퇴직자 수', value=f'{total_attritions}명')
col3.metric(label='전체 퇴직율', value=f'{overall_rate}%')


#그래프


team_result = attrition_summary(result,'부서')



st.subheader("부서별 퇴직율")

fig1, ax1 = plt.subplots(figsize=(8, 4))
sns.barplot(data=team_result, x="부서", y="퇴직율", ax=ax1, color='red')
ax1.set_xlabel("부서")
ax1.set_ylabel("퇴직율(%)")
st.pyplot(fig1)



st.subheader("연령대별 퇴직율")

fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.barplot(data=age_result, x="연령대", y="퇴직율", ax=ax2, color='green')
ax2.set_xlabel("연령대")
ax2.set_ylabel("퇴직율(%)")
st.pyplot(fig2)


#사이드바
