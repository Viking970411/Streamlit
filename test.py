import streamlit as st

# 샘플
st.title('인사 앱 ')

name = st.text_input('이름을 입력하세요 :')

if name :
    st.write(f'안녕하세요, {name}님!')

#버튼 생성
if st.button('인사하기') :
    st.write(f'{name}님, 안녕')   

# 사이드 바
st.sidebar.title('조회 조건') 

dept =st.sidebar.selectbox('부서를 선택하세요',
                           ['전체', '인사팀','영업팀','개발팀'])
st.write(f'선택한 부서 :{dept}')

#재미있는 기능
if st.button('재미있는 기능') :
    st.balloons()
    st.snow()

#여러종류의 안내메세지
st.info('정보안내메세지')
st.success('성공안내메세지')
st.warning('경고안내메세지')
st.error('오류안내메세지')




# uv run streamlit run test.py
# cntrl + c 
# 화살표 위아래로 히스토리로 선택