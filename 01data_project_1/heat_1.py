import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import koreanize_matplotlib

# =========================================================================================
#온열환자 데이터
# =========================================================================================
#heated_data_origin= pd.read_csv(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\질병관리청_온열질환 감시 데이터_20250925.CSV')

# BASE_DIR 정의 (heat_1.py 파일이 있는 폴더 기준)
BASE_DIR = Path(__file__).parent

# 수정 전: pd.read_csv(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\질병관리청...')
heated_data_origin = pd.read_csv(BASE_DIR / '질병관리청_온열질환 감시 데이터_20250925.CSV')

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
#covered_data= pd.read_excel(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\2025년(2024년_기준)_국가토지피복통계_토지피복지도현황.xlsx', sheet_name=1,header=2)

# 수정 전: pd.read_excel(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\2025년...')
covered_data = pd.read_excel(BASE_DIR / '2025년(2024년_기준)_국가토지피복통계_토지피복지도현황.xlsx', sheet_name=1, header=2)

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
#city_populate= pd.read_csv(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\주민등록인구_도시 포함.csv',header=1)

# 수정 전: pd.read_csv(r'C:\Users\SBA\Desktop\yjh\code_yjh\01data_project_1\주민등록인구_도시 포함.csv'...)
city_populate = pd.read_csv(BASE_DIR / '주민등록인구_도시 포함.csv', header=1)

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

# =========================================================================================
# 1. 전국 발생장소
# =========================================================================================
place_counts = meshup_clean['발생장소'].value_counts().reset_index()
place_counts.columns = ['발생장소', '건수']

# 2. 그래프 그리기
plt.figure(figsize=(10, 6))

sns.barplot(
    data=place_counts,
    x='발생장소',
    y='건수',
    hue='발생장소',       # 그라데이션 적용을 위한 hue 설정
    palette='Reds_r',   # 높은 값(왼쪽)일수록 짙은 파란색
    legend=False
)

plt.title('전국 발생 장소별 건수', fontsize=12)
plt.xlabel('발생장소')
plt.ylabel('건수')
plt.xticks(rotation=45, ha='right') # 라벨 오른쪽 정렬로 깔끔하게 배치
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# =========================================================================================
# 1. 전국 지면 구분별 발생건수
# =========================================================================================

ground_counts = df_all['사고지면구분'].value_counts().reset_index()
ground_counts.columns = ['사고지면구분', '건수']

ground_counts['사고지면구분'] = ground_counts['사고지면구분'].replace({'불투수 지면': '인공 지면'})
# 2. 그래프 그리기
plt.figure(figsize=(10, 6))

sns.barplot(
    data=ground_counts,
    x='사고지면구분',
    y='건수',
    hue='사고지면구분',       # 그라데이션 적용을 위한 hue 설정
    palette='Reds_r',   # 높은 값(왼쪽)일수록 짙은 파란색
    legend=False
)

plt.title('전국 지면 구분별 발생 건수', fontsize=12)
plt.xlabel('발생장소')
plt.ylabel('건수')
plt.xticks(ha='right') # 라벨 오른쪽 정렬로 깔끔하게 배치
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# =========================================================================================
# 1. 도시별 실외 인공 지면 비율 평균
# =========================================================================================

hood_asphalt = meshup_clean.groupby('발생시도')['실외 불투수 지면 비율'].mean().reset_index()
hood_asphalt = hood_asphalt.sort_values(by= '실외 불투수 지면 비율', ascending=False)
#hood_asphalt['사고지면구분'] = hood_asphalt['사고지면구분'].replace({'불투수 지면': '인공 지면'})

plt.figure(figsize=(10,6))
sns.barplot(data=hood_asphalt, x='발생시도', y='실외 불투수 지면 비율', palette='Reds_r')

plt.title('도시별 실외 인공 지면 비율 평균')
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()

# =========================================================================================
# 도시별 평균 발생률 (인구 10만 명당)
# =========================================================================================

sido_avg = df_all.groupby('발생시도')['발생률_10만명당'].mean().reset_index()

# 2. 평균값이 높은 순서대로 내림차순 정렬
sido_avg = sido_avg.sort_values(by='발생률_10만명당', ascending=False).reset_index(drop=True)

plt.figure(figsize=(10, 6))

# x축: 발생시도, y축: 평균 발생률
sns.barplot(data=sido_avg, x='발생시도', y='발생률_10만명당', palette='Blues_r')

plt.title('도시별 평균 발생률 (인구 10만 명당)')
plt.xlabel('발생시도')
plt.ylabel('평균 발생률 (10만 명당)')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.show()

# =========================================================================================
# 도시별 평균 발생률과 인공지면 비율  비교
# =========================================================================================

sido_summary = df_all.groupby('발생시도').agg(
    발생률_평균=('발생률_10만명당', 'mean'),
    불투수율_평균=('실외 불투수 지면 비율', 'mean')  # 실제 불투수율 컬럼명으로 확인
).reset_index()

# 2. 발생률 평균 기준 내림차순 정렬
sido_summary = sido_summary.sort_values(by='발생률_평균', ascending=False).reset_index(drop=True)

# 3. 이중 Y축 그래프 그리기
fig, ax1 = plt.subplots(figsize=(12, 6))

# 왼쪽 Y축 (막대): 발생률 평균
ax1.bar(sido_summary['발생시도'], sido_summary['발생률_평균'], color='steelblue', alpha=0.7, label='발생률')
ax1.set_xlabel('도시(발생시도)')
ax1.set_ylabel('평균 발생률 (10만 명당)', color='steelblue')
ax1.tick_params(axis='x', rotation=45)

# 오른쪽 Y축 (꺾은선): 불투수율 평균
ax2 = ax1.twinx()
ax2.plot(sido_summary['발생시도'], sido_summary['불투수율_평균'], color='#E65100', marker='o', linewidth=2, label='불투수율')
ax2.set_ylabel('평균 실외 불투수 지면 비율', color='#E65100')

plt.title('도시별 평균 발생률과 인공지면 비율  비교')
plt.grid(axis='y', linestyle='--', alpha=0.4)
fig.tight_layout()
plt.show()

# =========================================================================================
# 시군별 평균 발생률 및 지면 불투수율 비교
# =========================================================================================

sido_summary = df_all.groupby('발생시군구').agg(
    발생률_평균=('발생률_10만명당', 'mean'),
    불투수율_평균=('실외 불투수 지면 비율', 'mean')
).reset_index()

# 2. 발생률 평균 기준 내림차순 정렬
sido_summary = sido_summary.sort_values(by='발생률_평균', ascending=False).reset_index(drop=True)

# 3. 이중 Y축 그래프 그리기
fig, ax1 = plt.subplots(figsize=(12, 5))

# 왼쪽 Y축 (막대): 발생률 평균 (x축 위치는 시군구 이름 대신 순번 인덱스 사용)
ax1.bar(sido_summary.index, sido_summary['발생률_평균'], color='steelblue', alpha=0.7, label='발생률')
ax1.set_ylabel('평균 발생률 (10만 명당)', color='steelblue')

# [변경] X축 눈금선 및 시군구 이름 라벨 제거
ax1.tick_params(axis='x', bottom=False, labelbottom=False)

# 오른쪽 Y축 (꺾은선): 불투수율 평균
ax2 = ax1.twinx()
ax2.plot(sido_summary.index, sido_summary['불투수율_평균'], color='#E65100', marker='o', linewidth=2, label='불투수율')
ax2.set_ylabel('평균 실외 불투수 지면 비율', color='#E65100')

plt.title('시군별 평균 발생률 및 지면 불투수율 비교')
fig.tight_layout()
plt.show()

# =========================================================================================
# 실외 불투수 지면 비율과 도시별 환자 발생률의 상관관계
# =========================================================================================

city_summary = df_all.groupby('발생시도').agg(
    환자발생률=('발생률_10만명당', 'mean'),
    불투수율=('실외 불투수 지면 비율', 'mean')
).reset_index()

plt.figure(figsize=(10, 6)) # 그래프 크기를 조금 넓혀주면 여유가 생깁니다.

ax = sns.regplot(
    data=city_summary,
    x='불투수율',
    y='환자발생률',
    color='steelblue',
    line_kws={'color': 'red', 'linewidth': 2}
)

# 텍스트 객체들을 담을 리스트 생성
texts = []
for i in range(len(city_summary)):
    texts.append(
        plt.text(
            city_summary['불투수율'].iloc[i],
            city_summary['환자발생률'].iloc[i],
            city_summary['발생시도'].iloc[i],
            fontsize=9
        )
    )

# 텍스트가 서로 겹치지 않게 자동으로 밀어내고 화살표/선 연결
#adjust_text(texts, arrowprops=dict(arrowstyle='->', color='gray', lw=0.5))

plt.title('실외 불투수 지면 비율과 도시별 환자 발생률의 상관관계')
plt.xlabel('평균 실외 불투수 지면 비율')
plt.ylabel('환자 발생률(10만명 당)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# =========================================================================================
# 인공 지면 비율과 시군구별 환자 발생률의 상관관계
# =========================================================================================

# 1. 시군구별 데이터 집계
city_summary = df_all.groupby('발생시군구').agg(
    환자발생률=('발생률_10만명당', 'mean'),
    불투수율=('실외 불투수 지면 비율', 'mean')
).reset_index()

plt.figure(figsize=(10, 6))

# 2. 회귀 산점도 그리기
ax = sns.barplot_or_reg = sns.regplot(
    data=city_summary,
    x='불투수율',
    y='환자발생률',
    color='steelblue',
    line_kws={'color': 'red', 'linewidth': 2} # 회귀선은 빨간색으로 강조
)

# [제거됨] 기존의 for문(plt.text) 삭제 -> 점 옆의 도시명 텍스트가 사라집니다.

# 3. 축 및 제목 설정
plt.title('인공 지면 비율과 시군구별 환자 발생률의 상관관계', fontsize=13)
plt.xlabel('평균 실외 불투수 지면 비율')
plt.ylabel('환자 발생률(10만명 당)')
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# =========================================================================================
# 서울특별시내 발생 장소별 건수
# =========================================================================================

# 1. 서울특별시 데이터 필터링
seoul_df = meshup_clean[meshup_clean['발생시도']=='서울특별시']

# 2. 서울특별시 내 발생장소별 건수 집계 및 내림차순 정렬
place_counts = seoul_df['발생장소'].value_counts().reset_index()
place_counts.columns = ['발생장소', '건수']

# 3. 그래프 그리기
plt.figure(figsize=(10, 6)) # 사진과 유사한 비율로 크기 조정

sns.barplot(
    data=place_counts,
    x='발생장소',
    y='건수',
    hue='발생장소',       # 그라데이션 적용을 위한 hue 설정
    palette='Blues_r',    # 짙은 빨강 -> 옅은 빨강 (내림차순 정렬과 어울림)
    legend=False         # 범례 숨기기
)

# 4. 사진과 동일한 스타일링
plt.title('서울특별시내 발생 장소별 건수', fontsize=12) # 제목 수정
plt.xlabel('발생장소')
plt.ylabel('건수')

# X축 라벨 회전 및 오른쪽 정렬 (사진 스타일)
plt.xticks(rotation=45, ha='right')

# 점선 스타일의 가로 그리드 추가 (사진 스타일)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# =========================================================================================
# 서울특별시내 발생 장소별 건수
# =========================================================================================

# 1. 서울특별시 데이터 필터링
seoul_df = df_all[meshup_clean['발생시도']=='서울특별시']

seoul_df['사고지면구분'] = seoul_df['사고지면구분'].replace({'불투수 지면': '인공 지면'})
# 2. 서울특별시 내 발생장소별 건수 집계 및 내림차순 정렬
place_counts = seoul_df['사고지면구분'].value_counts().reset_index()
place_counts.columns = ['사고지면구분', '건수']

# 3. 그래프 그리기
plt.figure(figsize=(10, 6)) # 사진과 유사한 비율로 크기 조정

sns.barplot(
    data=place_counts,
    x='사고지면구분',
    y='건수',
    hue='사고지면구분',       # 그라데이션 적용을 위한 hue 설정
    palette='Blues_r',    # 짙은 빨강 -> 옅은 빨강 (내림차순 정렬과 어울림)
    legend=False         # 범례 숨기기
)

# 4. 사진과 동일한 스타일링
plt.title('서울특별시내 발생 장소별 건수', fontsize=12) # 제목 수정
plt.xlabel('사고지면구분')
plt.ylabel('건수')

# X축 라벨 회전 및 오른쪽 정렬 (사진 스타일)
plt.xticks( ha='right')

# 점선 스타일의 가로 그리드 추가 (사진 스타일)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# =========================================================================================
# 서울특별시 구별·지면구분별 발생 건수
# =========================================================================================

# 1. 서울특별시 데이터 필터링
seoul_ground = meshup_clean[meshup_clean['발생시도'] == '서울특별시']

# 2. 총 발생 건수가 많은 구(시군구) 순서 리스트 추출 (가로축 정렬용)
sigungu_order = seoul_ground['발생시군구'].value_counts().index

# 3. 그래프 그리기
plt.figure(figsize=(12, 6))

ax = sns.countplot(
    data=seoul_ground,
    x='발생시군구',
    hue='사고지면구분',
    order=sigungu_order,   # 발생 건수가 많은 구부터 내림차순 배치
    palette='Set2'         # 구분이 명확하고 차분한 파스텔 팔레트
)

# 4. 비주얼 디테일 강화
plt.title('서울특별시 구별·지면구분별 발생 건수', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('발생시군구', fontsize=11)
plt.ylabel('발생 건수', fontsize=11)

# X축 텍스트 45도 회전 및 오른쪽 끝 맞춤 (글자 겹침 방지)
plt.xticks(rotation=45, ha='right', fontsize=10)

# Y축 점선 그리드 추가 (수치 비교 용이)
plt.grid(axis='y', linestyle='--', alpha=0.5)

# 범례 상단 배치 및 디자인 설정
plt.legend(title='사고지면구분', title_fontsize='10', fontsize='9', loc='upper right')

plt.tight_layout()
plt.show()

# =========================================================================================
# 대전광역시내 발생 장소별 건수
# =========================================================================================

# 1. 대전광역시 데이터 필터링 및 발생장소별 건수 집계 (내림차순)
daejeon_df = meshup_clean[meshup_clean['발생시도'] == '대전광역시']
place_counts = daejeon_df['발생장소'].value_counts().reset_index()
place_counts.columns = ['발생장소', '건수']

# 2. 그래프 그리기
plt.figure(figsize=(10, 5))

sns.barplot(
    data=place_counts,
    x='발생장소',
    y='건수',
    hue='발생장소',       # 그라데이션 적용을 위한 hue 설정
    palette='Blues_r',   # 짙은 파랑 -> 옅은 파랑 (내림차순 정렬용)
    legend=False
)

# 3. 사진 스타일 적용
plt.title('대전광역시내 발생 장소별 건수', fontsize=12)
plt.xlabel('발생장소')
plt.ylabel('건수')

plt.xticks(rotation=45, ha='right')           # 라벨 45도 회전 및 오른쪽 정렬
plt.grid(axis='y', linestyle='--', alpha=0.7) # 가로 점선 그리드

plt.tight_layout()
plt.show()

# =========================================================================================
# 대전광역시내 사고지면구분별 건수
# =========================================================================================

# 1. 대전광역시 데이터 필터링 및 사고지면구분별 건수 집계 (내림차순)
daejeon_df = meshup_clean[meshup_clean['발생시도'] == '대전광역시']
ground_counts = daejeon_df['사고지면구분'].value_counts().reset_index()
ground_counts.columns = ['사고지면구분', '건수']

ground_counts['사고지면구분'] = ground_counts['사고지면구분'].replace({'불투수 지면': '인공 지면'})
# 2. 그래프 그리기
plt.figure(figsize=(6, 4))

sns.barplot(
    data=ground_counts,
    x='사고지면구분',
    y='건수',
    hue='사고지면구분',       # 그라데이션 적용을 위한 hue 설정
    palette='Blues_r',   # 짙은 파랑 -> 옅은 파랑 (내림차순 정렬용)
    legend=False
)

# 3. 동일 양식 스타일 적용
plt.title('대전광역시내 사고지면구분별 건수', fontsize=12)
plt.xlabel('사고지면구분')
plt.ylabel('건수')

plt.xticks( ha='right')           # 라벨 45도 회전 및 오른쪽 정렬
plt.grid(axis='y', linestyle='--', alpha=0.7) # 가로 점선 그리드

plt.tight_layout()
plt.show()

# =========================================================================================
# 대전광역시 구별·지면구분별 발생 건수
# =========================================================================================

# 1. 대전광역시 데이터 필터링
daejeon_ground = meshup_clean[meshup_clean['발생시도'] == '대전광역시']

# 2. 총 발생 건수가 많은 구(시군구) 순서 리스트 추출 (내림차순 정렬용)
sigungu_order = daejeon_ground['발생시군구'].value_counts().index

# 3. 그래프 그리기
plt.figure(figsize=(10, 5))

ax = sns.countplot(
    data=daejeon_ground,
    x='발생시군구',
    hue='사고지면구분',
    order=sigungu_order,   # 발생 건수가 많은 구부터 내림차순 배치
    palette='Set2'         # 가독성이 높은 파스텔 팔레트
)

# 4. 비주얼 디테일 설정
plt.title('대전광역시 구별·지면구분별 발생 건수', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('발생시군구', fontsize=11)
plt.ylabel('발생 건수', fontsize=11)

# X축 텍스트 정렬 및 Y축 가로 그리드 설정
plt.xticks( ha='right', fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend(title='사고지면구분', title_fontsize='10', fontsize='9', loc='upper right')

plt.tight_layout()
plt.show()

# =========================================================================================
# 울산광역시내 발생 장소별 건수
# =========================================================================================

# 1. 울산광역시 데이터 필터링 및 발생장소별 건수 집계 (내림차순)
ulsan_df = meshup_clean[meshup_clean['발생시도'] == '울산광역시']
place_counts = ulsan_df['발생장소'].value_counts().reset_index()
place_counts.columns = ['발생장소', '건수']

# 2. 그래프 그리기
plt.figure(figsize=(10, 5))

sns.barplot(
    data=place_counts,
    x='발생장소',
    y='건수',
    hue='발생장소',       # 그라데이션 적용을 위한 hue 설정
    palette='Blues_r',   # 짙은 파랑 -> 옅은 파랑 (내림차순 정렬용)
    legend=False
)

# 3. 동일 양식 스타일 적용
plt.title('울산광역시내 발생 장소별 건수', fontsize=12)
plt.xlabel('발생장소')
plt.ylabel('건수')

plt.xticks(rotation=45, ha='right')           # 라벨 45도 회전 및 오른쪽 정렬
plt.grid(axis='y', linestyle='--', alpha=0.7) # 가로 점선 그리드

plt.tight_layout()
plt.show()

# =========================================================================================
# 울산광역시내 사고지면구분별 건수
# =========================================================================================

# 1. 울산광역시 데이터 필터링 및 사고지면구분별 건수 집계 (내림차순)
ulsan_df = meshup_clean[meshup_clean['발생시도'] == '울산광역시']
ground_counts = ulsan_df['사고지면구분'].value_counts().reset_index()
ground_counts.columns = ['사고지면구분', '건수']

# 2. 그래프 그리기
plt.figure(figsize=(6,4))

sns.barplot(
    data=ground_counts,
    x='사고지면구분',
    y='건수',
    hue='사고지면구분',       # 그라데이션 적용을 위한 hue 설정
    palette='Blues_r',   # 짙은 파랑 -> 옅은 파랑 (내림차순 정렬용)
    legend=False
)

# 3. 동일 양식 스타일 적용
plt.title('울산광역시내 사고지면구분별 건수', fontsize=12)
plt.xlabel('사고지면구분')
plt.ylabel('건수')

plt.xticks( ha='right')           # 라벨 45도 회전 및 오른쪽 정렬
plt.grid(axis='y', linestyle='--', alpha=0.7) # 가로 점선 그리드

plt.tight_layout()
plt.show()

# =========================================================================================
# 울산광역시 구별·지면구분별 발생 건수
# =========================================================================================

# 1. 울산광역시 데이터 필터링
ulsan_ground = meshup_clean[meshup_clean['발생시도'] == '울산광역시']

# 2. 총 발생 건수가 많은 구(시군구) 순서 리스트 추출 (내림차순 정렬용)
sigungu_order = ulsan_ground['발생시군구'].value_counts().index

# 3. 그래프 그리기
plt.figure(figsize=(10, 5))

ax = sns.countplot(
    data=ulsan_ground,
    x='발생시군구',
    hue='사고지면구분',
    order=sigungu_order,   # 발생 건수가 많은 구부터 내림차순 배치
    palette='Set2'         # 가독성이 높은 파스텔 팔레트
)

# 4. 비주얼 디테일 설정
plt.title('울산광역시 구별·지면구분별 발생 건수', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('발생시군구', fontsize=11)
plt.ylabel('발생 건수', fontsize=11)

# X축 텍스트 정렬 및 Y축 가로 그리드 설정
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend(title='사고지면구분', title_fontsize='10', fontsize='9', loc='upper right')

plt.tight_layout()
plt.show()

# =========================================================================================
# 나이별 인공지면 온열환자 발생율
# =========================================================================================
city_summary = meshup_clean.groupby('발생시도').agg(
    환자발생수=('발생시도', 'count'),
    불투수율=('실외 불투수 지면 비율', 'mean')
).reset_index()

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
    color='#FED976'
)

plt.title('나이별 인공지면 온열환자 발생율')
plt.xlabel('연령대')
plt.ylabel('환자 발생율')
plt.grid(axis='y', linestyle='--', alpha=0.7)

#for container in ax.containers:
   # ax.bar_label(container, fmt='%.1f')

plt.show()

# =========================================================================================
# 도시별·연령대별 실외 온열환자 발생률 히트맵
# =========================================================================================

# 1. 연령대 컬럼 생성
workplace_df['연령대'] = (workplace_df['나이'] // 10 * 10).fillna(0).astype(int).astype(str) + '대'

# 2. (시도 x 연령대) 평균 발생률 피벗 테이블 생성
pivot_df = workplace_df.pivot_table(
    index='시도',
    columns='연령대',
    values='발생률_10만명당',
    aggfunc='mean'
).fillna(0)

age_order = [f'{i}대' for i in range(0, 110, 10)] # ['0대', '10대', ..., '90대', '100대']
existing_cols = [col for col in age_order if col in pivot_df.columns]
pivot_df = pivot_df[existing_cols]

# 3. 히트맵 시각화
plt.figure(figsize=(12, 8))
sns.heatmap(
    pivot_df,
    annot=True,          # 각 칸에 숫자 표시
    fmt='.1f',           # 소수점 첫째자리까지
    cmap='YlOrRd',       # 옅은 노랑 -> 붉은색 범주
    linewidths=0.5
)

plt.title('도시별·연령대별 실외 온열환자 발생률 히트맵', fontsize=14)
plt.xlabel('연령대')
plt.ylabel('시도(도시)')
plt.show()


# -------------------------------------------------------------
# 인공지면 온열환자 성비
# -------------------------------------------------------------

plt.figure(figsize=(8, 5))

# 세련된 파랑과 적색 컬러 팔레트 적용
ax = sns.barplot(
    data=workplace_df,
    x='성별',
    y='발생률_10만명당',
    hue='성별',                     # palette 사용을 위한 hue 지정
    palette=['#2B5C8F', '#C0392B'],   # [첫 번째 막대(파랑), 두 번째 막대(적색)]
    legend=False,                  # 중복 범례 숨기기
    errorbar=None
)

plt.title('인공지면 온열환자 성비', fontsize=13, pad=12)
plt.xlabel('성별')
plt.ylabel('환자 발생율')

# 가독성을 높이기 위한 가로 점선 그리드 추가
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# -------------------------------------------------------------
# 도시별 실외 온열환자 남녀비
# -------------------------------------------------------------

plt.figure(figsize=(8,5))

ax = sns.barplot(
    data=workplace_df,
    x='시도',
    y='발생률_10만명당',
    palette=['#2B5C8F', '#C0392B'],
    errorbar=None,
    hue='성별'
)

ax.tick_params(axis='x', rotation=45)

plt.title('도시별 실외 온열환자 남녀비율')
plt.xlabel('성별')
plt.ylabel('환자 발생율')

plt.show()

# -------------------------------------------------------------
# streamlit
# -------------------------------------------------------------

import streamlit as st

# -------------------------------------------------------------
# streamlit 오류 보완
# -------------------------------------------------------------

# 1. 필터용 옵션 리스트 생성
sido_options = ['전국'] + list(df_all['발생시도'].dropna().unique())

if '연령대' in df_all.columns:
    age_options = ['전체'] + sorted([str(x) for x in df_all['연령대'].dropna().unique()])
else:
    age_options = ['전체']

gender_options = ['전체'] + list(df_all['성별'].dropna().unique()) if '성별' in df_all.columns else ['전체']

# 2. 가장 기본형 드롭다운 선택창(selectbox) 생성
st.subheader("데이터 필터 선택")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    selected_sido = st.selectbox('지역 선택', options=sido_options)
with col_f2:
    selected_age = st.selectbox('연령대 선택', options=age_options)
with col_f3:
    selected_gender = st.selectbox('성별 선택', options=gender_options)

# 3. 데이터 필터링
filtered_df = df_all.copy()

if selected_sido != '전국':
    filtered_df = filtered_df[filtered_df['발생시도'] == selected_sido]

if selected_age != '전체' and '연령대' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['연령대'].astype(str) == selected_age]

if selected_gender != '전체' and '성별' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['성별'] == selected_gender]

# 4. KPI 표시 (기본 st.metric 사용)
st.markdown("---")
st.subheader("핵심 지표 (KPI)")

total_patients = len(filtered_df)
avg_incidence_rate = filtered_df['발생률_10만명당'].mean() if not filtered_df.empty else 0
avg_impervious_rate = filtered_df['실외 불투수 지면 비율'].mean() if not filtered_df.empty else 0

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    st.metric(label="총 환자 발생 수", value=f"{total_patients:,} 명")
with kpi_col2:
    st.metric(label="평균 발생률 (10만명당)", value=f"{avg_incidence_rate:.1f} 명")
with kpi_col3:
    st.metric(label="평균 실외 불투수 지면 비율", value=f"{avg_impervious_rate:.1f} %")

st.markdown("---")

# 5. 사고지면구분별 건수 집계 및 인사이트 도출
ground_counts = filtered_df['사고지면구분'].value_counts().reset_index()
ground_counts.columns = ['사고지면구분', '건수']
ground_counts['사고지면구분'] = ground_counts['사고지면구분'].replace({'불투수 지면': '인공 지면'})

# 인사이트 텍스트 작성
st.subheader("분석 인사이트")

if not ground_counts.empty:
    top_ground = ground_counts.iloc[0]['사고지면구분']
    top_count = ground_counts.iloc[0]['건수']
    top_ratio = (top_count / total_patients) * 100 if total_patients > 0 else 0
    
    insight_text = f"""
    - **{selected_sido}** ({selected_age}, {selected_gender}) 조건의 총 발생 건수는 **{total_patients:,}건**입니다.
    - 가장 환자 발생이 많은 지면은 **[{top_ground}]**으로 전체의 **{top_ratio:.1f}%**({top_count:,}건)를 차지합니다.
    - 선택된 조건의 평균 실외 불투수 지면 비율은 **{avg_impervious_rate:.1f}%**입니다.
    """
    st.info(insight_text)
else:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

# 6. 시각화 그래프 출력
st.subheader("지면 구분별 발생 건수")
graph_title = f"{selected_sido} | {selected_age} | {selected_gender} 지면 구분별 발생 건수"

fig, ax = plt.subplots(figsize=(10, 5))

if not ground_counts.empty:
    sns.barplot(
        data=ground_counts,
        x='사고지면구분',
        y='건수',
        hue='사고지면구분',
        palette='Reds_r',
        legend=False,
        ax=ax
    )
    ax.set_title(graph_title, fontsize=12)
    ax.set_xlabel('사고지면구분')
    ax.set_ylabel('건수')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
else:
    ax.text(0.5, 0.5, '데이터가 없습니다.', horizontalalignment='center', verticalalignment='center', fontsize=12)

plt.tight_layout()
st.pyplot(fig)