import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import koreanize_matplotlib

# =========================================================================================
#온열환자 데이터
# =========================================================================================
heated_data_origin= pd.read_csv(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\질병관리청_온열질환 감시 데이터_20250925.CSV')
#print(heated_data.head())
#print(heated_data['성별'].isnull().sum())

#공백리스트 제거 원본에 작업
heated_data_origin = heated_data_origin.dropna(subset=['성별'])
#print(heated_data['성별'].isnull().sum())  

print('''

***데이터 상태***

''')
print(heated_data_origin.shape)
print('***결측치***')
print('-'*30)
print(heated_data_origin.isnull().sum())

#시군구단위의 데이터가 필요함으로 시군구 집계가된 시점의 데이터만 활용(2019년 이후)
print('''
***결측치 확인***''')
print('-'*30)
heated_data = heated_data_origin.dropna()
print(heated_data.isnull().sum())
print(heated_data.shape)

#print(heated_data.head())
print('''
***사고 발생 장소 컬럼***''')
print('-'*30)
print(heated_data['발생장소'].value_counts())

#이상치확인
print('''
***이상치 확인***''')
print('-'*30)
category_colunms = heated_data.select_dtypes(include='object').columns

for colunm in category_colunms:
  print(heated_data[colunm].value_counts())
  print('-'*30)

print('''
***나이 이상치 확인***''')
print(heated_data.describe().T)

print((heated_data['나이']==0).sum())
#나이가 0인 데이터(5명)는 결측이 아니라 영유아로 판단, 최대치는 104살
#이상치 없음

# =========================================================================================
#불투수면율 데이터
# =========================================================================================
print('''
***불투수면율 데이터***''')
print('-'*30)
covered_data= pd.read_excel(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\2025년(2024년_기준)_국가토지피복통계_토지피복지도현황.xlsx', sheet_name=1,header=2)
covered_data.to_csv('피폭도.csv', index=False, encoding='utf-8-sig')
print(covered_data.shape)
print(covered_data.head(7))

#비율을 데이터로 활용할 것이기 때문에 면적 리스트는 제거
print('''
***절대 면적 리스트 제거, 단위 수정, 컬럼이름 통합***''')
print('-'*30)
covered_data_new = covered_data[covered_data['구분'].astype(str).str.strip() == '비율(%)'].reset_index(drop=True) 
#print(covered_data['구분'].unique())
#print(covered_data_new.head())

#단위 표시 수정
import pandas as pd
pd.set_option('display.float_format', lambda x : '%0f' % x)
#print(covered_data_new.head())

#결측치, 이상값 확인 
#print(covered_data.isnull().sum())
#print('-'*30)
#category_colunms2 = covered_data.select_dtypes(include='object').columns
#for colunm in category_colunms2:
  #print(covered_data[colunm].value_counts())
  #print('-'*30)
#print(covered_data.describe().T)

# =========================================================================================
#데이터 결합
# =========================================================================================
# 컬럼이름 통합
print('-'*30)
covered_data_new.columns = covered_data_new.columns.str.strip()
covered_data_new = covered_data_new.rename(columns = {'시군구' :'발생시군구' })
print(covered_data_new.head())

#데이터 결합
print('''
***데이터 결합***''')
print('-'*30)
meshup_data = pd.merge(
  heated_data,
  covered_data_new,
  on = '발생시군구' ,
  indicator=True
)
print(meshup_data.head())

# 토지피폭도 발생장소에 매핑
print('''
***컬럼 전처리***''')
print('-'*30)
place_mapping = {
    '실외작업장 비율': ['공업시설', '채광지역', '기타공공시설'],
    '논밭 비율': ['경지정리가 된 논', '경지정리가 안 된 논', '경지정리가 된 밭', '경지정리가 안 된 밭', '과수원', '기타재배지'],
    '길가 비율': ['도로', '기타교통통신시설'],
    '실외 기타 비율': ['기타나지', '혼합지역', '기타공공시설'],
    '실내 작업장 비율': ['공업시설', '상업업무시설'],
    '집 비율': ['단독주거시설', '공동주거시설'],
    '주거지 주변 비율': ['단독주거시설', '공동주거시설'],
    '운동장(공원) 비율': ['운동장', '문화체육휴양시설', '골프장', '자연초지'],
    '산 비율': ['활엽수림', '침엽수림', '혼효림'],
    '건물 비율': ['상업업무시설', '교육행정시설', '기타공공시설'],
    '실내 기타 비율': ['상업업무시설', '기타공공시설'],
    '비닐하우스 비율': ['시설재배지'],
    '강가,해변 비율': ['강기슭', '해변', '하천'],
    '찜질방(사우나) 비율': ['상업업무시설']
}

for new_col, source_cols in place_mapping.items():
    meshup_data[new_col] = meshup_data[source_cols].sum(axis=1)


print('-'*30)
place_mapping_2 = {
    '실외 불투수 지면 비율': ['길가 비율', '실외작업장 비율', '운동장(공원) 비율', '주거지 주변 비율'],
    '실외 자연 지면 비율': ['논밭 비율', '산 비율', '비닐하우스 비율', '강가,해변 비율', '실외 기타 비율'],
    '실내 밀폐 공간 비율': ['집 비율', '건물 비율', '실내 작업장 비율', '찜질방(사우나) 비율', '실내 기타 비율']
}

for new_col, source_cols in place_mapping_2.items():
    meshup_data[new_col] = meshup_data[source_cols].sum(axis=1)

#매핑한 외 데이터 삭제
print('''
***불필요 컬럼 삭제***''')
print('-'*30)
meshup_data_2 = meshup_data.copy()
#***통합 전체 컬럼2 추출***
#meshup_data_2.to_csv('통합 전체 컬럼2.csv', index=False, encoding='utf-8-sig')
print(meshup_data_2.columns[8:66])
meshup_clean = meshup_data_2.drop(meshup_data_2.columns[8:66], axis=1)
print(meshup_clean.columns)

#발생장소 지면 종류 구분 칼럼 추가
meshup_clean = meshup_clean.copy()
place_mapping_3 = {
    '불투수 지면': ['실외 작업장', '길가', '운동장(공원)', '주거지 주변'],
    '자연 지면': ['논밭', '실외 기타', '산', '비닐하우스', '강가,해변'],
    '밀폐 공간': ['실내 작업장', '집', '건물', '실내 기타', '찜질방(사우나)']
}
reverse_map = {place: category for category, places in place_mapping_3.items() for place in places}
meshup_clean['사고지면구분'] = meshup_clean['발생장소'].map(reverse_map)

#***통합 컬럼2 추출***
#meshup_clean.to_csv('통합 컬럼2.csv', index=False, encoding='utf-8-sig')

# =========================================================================================
#인구비율을 위한 전체 인구 데이터(도시기준)
# =========================================================================================
city_populate= pd.read_csv(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\주민등록인구_도시 포함.csv',header=1)
city_populate = city_populate.drop(0).reset_index(drop=True)

# 1. 대한민국 광역시도 명칭 리스트
sido_list = [
    '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', 
    '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도', 
    '강원특별자치도', '충청북도', '충청남도', '전라북도', '전북특별자치도', 
    '전라남도', '경상북도', '경상남도', '제주특별자치도'
]

# 2. '발생시도' 컬럼 생성 및 위에서 아래로 채우기(ffill)
city_populate['발생시도'] = city_populate['행정구역별'].apply(
    lambda x: str(x).strip() if str(x).strip() in sido_list else None
)
city_populate['발생시도'] = city_populate['발생시도'].ffill()

# 3. '서울특별시' 같은 시도 자체 행(합계 행) 삭제
city_populate = city_populate[~city_populate['행정구역별'].astype(str).str.strip().isin(sido_list)].copy()

# 4. 기존 '행정구역별' 컬럼명을 '발생시군구'로 변경
city_populate = city_populate.rename(columns={'행정구역별': '발생시군구'})

# 5. '발생시도'를 가장 맨 앞(첫 번째 컬럼)으로 순서 재배치
cols = ['발생시도', '발생시군구', '계 (명)', '남 (명)', '여 (명)']
city_populate = city_populate[cols].reset_index(drop=True)

#인구 데이터 병합
# [1단계] 발생시군구 변환 함수 정의
def map_to_parent_sigungu(name):
    if pd.isna(name):
        return name
    
    name = str(name).strip()
    
    # 1. 통합시 예외 처리 (창원시 진해구 -> 통합창원시, 청주시 흥덕구 -> 통합청주시)
    if name.startswith('창원시'):
        return '통합창원시'
    if name.startswith('청주시'):
        return '통합청주시'
    
    # 2. '수원시 장안구', '고양시 덕양구' 등에서 대표 '시' 명칭만 추출 ('수원시', '고양시')
    return name.split()[0]


# [2단계] df1 및 df2 데이터 전처리 (컬럼 값 재지정)

# 1) 발생시도 명칭 통일 (전북특별자치도 -> 전라북도 등)
sido_fix = {
    '전북특별자치도': '전라북도',
    '강원특별자치도': '강원도'
}

meshup_clean['발생시도'] = meshup_clean['발생시도'].astype(str).str.strip().replace(sido_fix)
city_populate['발생시도'] = city_populate['발생시도'].astype(str).str.strip().replace(sido_fix)

# 2) df1의 '발생시군구'를 두 번째 리스트 양식으로 변환하여 재지정
meshup_clean['발생시군구'] = meshup_clean['발생시군구'].apply(map_to_parent_sigungu)
city_populate['발생시군구'] = city_populate['발생시군구'].astype(str).str.strip()


# [3단계] 변환된 df1과 df2 병합 (Merge)
merged_df = pd.merge(
    meshup_clean, 
    city_populate, 
    on=['발생시도', '발생시군구'], 
    how='left'
)
#merged_df = merged_df.drop(columns=['발생시군구_정제_x', '발생시군구_정제_y', errors='ignore'])

# =========================================================================================
#인구대비 발생율 칼럼 생성
# =========================================================================================
# 1. 시도/시군구별 환자 수(행 개수) 및 총 인구수 집계
sigungu_summary = merged_df.groupby(['발생시도', '발생시군구']).agg(
    환자수=('발생일자', 'count'),    # 해당 시군구의 발생 건수
    인구수=('계 (명)', 'first')     # 해당 시군구의 총 인구수
).reset_index()

# 2. 인구 10만 명당 발생률 계산
sigungu_summary['발생률_10만명당'] = (sigungu_summary['환자수'] / sigungu_summary['인구수']) * 100000

# (선택) 단순 비율(%)로 계산하고 싶을 경우
# sigungu_summary['발생률_%'] = (sigungu_summary['환자수'] / sigungu_summary['인구수']) * 100

# 3. 발생률이 높은 순서대로 내림차순 정렬
sigungu_summary = sigungu_summary.sort_values(by='발생률_10만명당', ascending=False).reset_index(drop=True)

df_all = pd.merge(
    merged_df, 
    sigungu_summary, 
    on=['발생시도', '발생시군구'], 
    how='left'
)


# 2. 전체 결측치 개수 확인
print("=== 결측치 개수 ===")
print(df_all.isnull().sum())

# 3. [위치 변경] dropna()를 하기 '전'에 결측치 발생 시군구 확인
missing_match = df_all[df_all['발생률_10만명당'].isnull()]['발생시군구'].unique()
print("=== 발생률이 NaN인 시군구 목록 ===")
print(missing_match)

# 4. 결측치 확인이 끝난 후 최종 행 삭제
# 결측치 숫자가 5개로 미미한 양은 삭제
df_all = df_all.dropna().reset_index(drop=True)

# =========================================================================================
# 데이터 분석
# =========================================================================================
#city = sns.load_dataset('발생시도')
#place = sns.load_dataset('발생장소')
print('''
***기본 온열환자 발생 집계***''')
print('-'*30)

plt.figure(figsize=(6,3))
#그래프 순위별 정열 코드 / #histplot 에 적용안됨
city_heat_list = meshup_clean['발생시도'].value_counts().index
sns.countplot(data=meshup_clean, x='발생시도', order=city_heat_list)
plt.title('도시별 발생수')
plt.xticks(rotation=45)
plt.show()

print('''
***도시별 온열환자 발생 비율***''')
print('-'*30)


# 1. 도시별 발생률 
# 1. 발생시도별 발생률 평균 계산
sido_avg = df_all.groupby('발생시도')['발생률_10만명당'].mean().reset_index()

# 2. 평균값이 높은 순서대로 내림차순 정렬
sido_avg = sido_avg.sort_values(by='발생률_10만명당', ascending=False).reset_index(drop=True)

plt.figure(figsize=(10, 6))

# x축: 발생시도, y축: 평균 발생률
sns.barplot(data=sido_avg, x='발생시도', y='발생률_10만명당', palette='Reds_r')

plt.title('발생시도별 평균 발생률 (인구 10만 명당)')
plt.xlabel('발생시도')
plt.ylabel('평균 발생률 (10만 명당)')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()



plt.figure(figsize=(6,3))
sns.histplot(data=meshup_clean, x='발생장소')
plt.title('전국 발생장소')
plt.xticks(rotation=45)
plt.show()

plt.figure(figsize=(6,3))
sns.histplot(data=meshup_clean[meshup_clean['발생시도']=='울산광역시'], x='발생장소')
plt.title('울산광역시내 발생장소')
plt.xticks(rotation=45)
plt.show()

plt.figure(figsize=(6,3))
sns.histplot(data=meshup_clean, x='사고지면구분')
plt.title('전국 사고장소 지면 종류별 현황')
plt.show()


print('''
***도시별 실외 불투면 비율***''')
print('-'*30)
print(meshup_clean.groupby('발생시도')['실외 불투수 지면 비율'].mean())

print('''
***군구별 실외 불투면 비율***''')
print('-'*30)
print(meshup_clean.groupby('발생시군구')['실외 불투수 지면 비율'].mean())

print('''
***군구별 온열환자 그래프화***''')
print('-'*30)

hood_heat_count = data=meshup_clean['발생시군구'].value_counts().head(20).index
sns.countplot(data=meshup_clean, x='발생시군구', order = hood_heat_count)
plt.title('군구별 환자 발생수')
plt.xticks(rotation=45)
plt.show()

print('''
***도시별 실외 불투면 비율 그래프화***''')
print('-'*30)

hood_asphalt = meshup_clean.groupby('발생시도')['실외 불투수 지면 비율'].mean().reset_index()
hood_asphalt = hood_asphalt.sort_values(by= '실외 불투수 지면 비율', ascending=False)

plt.figure(figsize=(6,3))
sns.barplot(data=hood_asphalt, x='발생시도', y='실외 불투수 지면 비율', palette='Blues_r')

plt.title('도시별 실외 불투수 지면 비율 평균')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print('''
***군구별 실외 불투면 비율 그래프화***''')
print('-'*30)

hood_asphalt = meshup_clean.groupby('발생시군구')['실외 불투수 지면 비율'].mean().reset_index()
hood_asphalt = hood_asphalt.sort_values(by= '실외 불투수 지면 비율', ascending=False).head(20)

plt.figure(figsize=(6,3))
sns.barplot(data=hood_asphalt, x='발생시군구', y='실외 불투수 지면 비율', palette='Blues_r')

plt.title('군구별 실외 불투수 지면 비율 평균')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print('''
***도시별 환자수와 불투수율***''')
print('-'*30)
city_summary = meshup_clean.groupby('발생시도').agg(
    환자발생수=('발생시도', 'count'),
    불투수율=('실외 불투수 지면 비율', 'mean')
).reset_index()
#print(city_summary.head())

ax = sns.regplot(
    data=city_summary, 
    x='불투수율', 
    y='환자발생수',
    color='steelblue',
    line_kws={'color': 'red', 'linewidth': 2} # 회귀선은 빨간색으로 강조
)

for i in range(len(city_summary)):
    plt.text(
        city_summary['불투수율'].iloc[i] + 0.005, 
        city_summary['환자발생수'].iloc[i], 
        city_summary['발생시도'].iloc[i], 
        fontsize=9
    )

plt.title('실외 불투수 지면 비율과 도시별 환자 발생수의 상관관계')
plt.xlabel('평균 실외 불투수 지면 비율')
plt.ylabel('환자 발생수(건)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

print('''
***군구별 환자수와 불투수율***''')
print('-'*30)
city_summary = meshup_clean.groupby('발생시군구').agg(
    환자발생수=('발생시군구', 'count'),
    불투수율=('실외 불투수 지면 비율', 'mean')
).reset_index()
#print(city_summary.head())

ax = sns.regplot(
    data=city_summary, 
    x='불투수율', 
    y='환자발생수',
    color='steelblue',
    line_kws={'color': 'red', 'linewidth': 2} # 회귀선은 빨간색으로 강조
)

for i in range(len(city_summary)):
    plt.text(
        city_summary['불투수율'].iloc[i] + 0.005, 
        city_summary['환자발생수'].iloc[i], 
        city_summary['발생시군구'].iloc[i], 
        fontsize=9
    )

plt.title('실외 불투수 지면 비율과 도시별 환자 발생수의 상관관계')
plt.xlabel('평균 실외 불투수 지면 비율')
plt.ylabel('환자 발생수(건)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# 1. 도시별 발생률 
# 1. 발생시도별 '발생률'과 '불투수 비율' 평균을 함께 집계
sido_summary = df_all.groupby('발생시도').agg(
    발생률_평균=('발생률_10만명당', 'mean'),
    불투수율_평균=('실외 불투수 지면 비율', 'mean')  # 실제 불투수율 컬럼명으로 확인
).reset_index()

# 2. 발생률 평균 기준 내림차순 정렬
sido_summary = sido_summary.sort_values(by='발생률_평균', ascending=False).reset_index(drop=True)

# 3. 이중 Y축 그래프 그리기
fig, ax1 = plt.subplots(figsize=(12, 5))

# 왼쪽 Y축 (막대): 발생률 평균
ax1.bar(sido_summary['발생시도'], sido_summary['발생률_평균'], color='skyblue', alpha=0.7, label='발생률')
ax1.set_xlabel('도시(발생시도)')
ax1.set_ylabel('평균 발생률 (10만 명당)', color='blue')
ax1.tick_params(axis='x', rotation=45)

# 오른쪽 Y축 (꺾은선): 불투수율 평균
ax2 = ax1.twinx()
ax2.plot(sido_summary['발생시도'], sido_summary['불투수율_평균'], color='crimson', marker='o', linewidth=2, label='불투수율')
ax2.set_ylabel('평균 실외 불투수 지면 비율', color='crimson')

plt.title('도시별 평균 발생률 및 지면 불투수율 비교')
fig.tight_layout()
plt.show()

# 1. 시군별 발생률 

sido_summary = df_all.groupby('발생시군구').agg(
    발생률_평균=('발생률_10만명당', 'mean'),
    불투수율_평균=('실외 불투수 지면 비율', 'mean') 
).reset_index()

# 2. 발생률 평균 기준 내림차순 정렬
sido_summary = sido_summary.sort_values(by='발생률_평균', ascending=False).reset_index(drop=True)

# 3. 이중 Y축 그래프 그리기
fig, ax1 = plt.subplots(figsize=(12, 5))

# 왼쪽 Y축 (막대): 발생률 평균
ax1.bar(sido_summary['발생시군구'], sido_summary['발생률_평균'], color='skyblue', alpha=0.7, label='발생률')
ax1.set_xlabel('도시(발생시군구)')
ax1.set_ylabel('평균 발생률 (10만 명당)', color='blue')
ax1.tick_params(axis='x', rotation=45)

# 오른쪽 Y축 (꺾은선): 불투수율 평균
ax2 = ax1.twinx()
ax2.plot(sido_summary['발생시군구'], sido_summary['불투수율_평균'], color='crimson', marker='o', linewidth=2, label='불투수율')
ax2.set_ylabel('평균 실외 불투수 지면 비율', color='crimson')

plt.title('시군별 평균 발생률 및 지면 불투수율 비교')
fig.tight_layout()
plt.show()

# =========================================================================================
# 나이별 데이터 분석으로 전환 
# =========================================================================================
df_all['연령대'] = pd.cut (
    df_all['나이'],
    bins=[0,9,19, 29, 39, 49,59,69,79,89,99,109],
    labels=['10세이하','10대','20대','30대','40대','50대','60대','70대','80대','90대','100세이상']
)


plt.figure(figsize=(8, 5))

workplace_df = df_all[df_all['사고지면구분'] == '불투수 지면']

ax = sns.barplot(
    data=workplace_df,
    x='연령대',
    y='발생률_10만명당',
    errorbar=None,
    color='steelblue'
)

plt.title('나이별 인공지면 온열환자 발생율')
plt.xlabel('연령대')
plt.ylabel('환자 발생율')

for container in ax.containers:
    ax.bar_label(container, fmt='%.1f')

plt.show()

# =========================================================================================
# 성별 데이터 분석으로 전환 
# =========================================================================================

plt.figure(figsize=(8, 5))

ax = sns.barplot(
    data=workplace_df,
    x='성별',
    y='발생률_10만명당',
    errorbar=None
)

plt.title('실외 온열환자 성비')
plt.xlabel('성별')
plt.ylabel('환자 발생율')

plt.show()

# =========================================================================================
# 도시별 성별 데이터 분석으로 전환 
# =========================================================================================

plt.figure(figsize=(8,5))

ax = sns.barplot(
    data=workplace_df,
    x='시도',
    y='발생률_10만명당',
    errorbar=None,
    hue='성별'
)

ax.tick_params(axis='x', rotation=45)

plt.title('도시별 실외 온열환자 남녀비율')
plt.xlabel('성별')
plt.ylabel('환자 발생율')

plt.show()

# =========================================================================================
# 발생시군구별 성별 데이터 분석으로 전환 
# =========================================================================================

#fig,ax1 = plt.subplots(figsize=(12,5))

#ax1.plot(df_all['발생시군구'],df_all[df_all['성별']=='남자'],color='blue',marker='o',linewidth=2, label='남성')

#ax2 = ax1.twinx()
#ax1.plot(df_all['발생시군구'],df_all[df_all['성별']=='여자'],color='red',marker='o',linewidth=2, label='여성')


#ax.tick_params(axis='x', rotation=45)

#plt.title('발생시군구별 실외 온열환자 남녀비율')
#plt.xlabel('성별')
#plt.ylabel('환자 발생율')

#plt.show()

gender_sigun = df_all.pivot_table(
    index='발생시군구',
    columns='성별',
    values='발생률_10만명당',
    aggfunc='mean'
).dropna()

#상위 20개 구 

gender_sigun['합계'] = gender_sigun.sum(axis=1)
top20_gender_sigun = gender_sigun.sort_values(by='합계', ascending=False).head(20)

fig,ax1 = plt.subplots(figsize=(14,6))

ax1.plot(gender_sigun.index, gender_sigun['남자'], color='blue', marker='o', linewidth=2, label='남성')
ax1.plot(gender_sigun.index, gender_sigun['여자'], color='red', marker='o', linewidth=2, label='여성')

plt.title('발생시군구별 실외 온열환자 남녀비율')
ax.tick_params(axis='x', rotation=45)

plt.show()