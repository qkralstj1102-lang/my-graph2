import streamlit as st
import pandas as pd
import plotly.express as px


# ==========================================
# 페이지 설정
# ==========================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 216편의 데이터를 이용해 "
    "영화의 분포와 관계를 살펴봅니다."
)


# ==========================================
# 데이터 불러오기
# ==========================================

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL)


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.write(e)
    st.stop()


# ==========================================
# 데이터 전처리
# ==========================================

# 여러 장르가 있는 경우 첫 번째 장르만 사용
df["genre_first"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

df.loc[df["genre_first"] == "", "genre_first"] = "미상"


# 제작 국가 결측값 처리
df["nation"] = (
    df["nation"]
    .fillna("미상")
    .astype(str)
    .str.strip()
)

df.loc[df["nation"] == "", "nation"] = "미상"


# 숫자 데이터 변환
df["total_audi"] = pd.to_numeric(
    df["total_audi"],
    errors="coerce"
)

df["first_scrn"] = pd.to_numeric(
    df["first_scrn"],
    errors="coerce"
)

df["first_week_audi"] = pd.to_numeric(
    df["first_week_audi"],
    errors="coerce"
)


# ==========================================
# 그래프 1
# 장르별 영화 편수 도넛 그래프
# ==========================================

st.divider()

st.header("그래프 1. 장르별 영화 편수")

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]


fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)


fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)


fig1.update_layout(
    height=550,
    legend_title="장르"
)


st.plotly_chart(
    fig1,
    use_container_width=True
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "한 문장으로 작성해 보세요.",
    placeholder="예: 이 기간에는 ○○ 장르의 영화가 가장 많았다.",
    key="graph1_comment"
)


# ==========================================
# 그래프 2
# 장르 → 영화 트리맵
# ==========================================

st.divider()

st.header("그래프 2. 장르별 영화 총 관객수 트리맵")


treemap_df = df[
    ["genre_first", "movieNm", "total_audi"]
].copy()


treemap_df = treemap_df.dropna(
    subset=[
        "genre_first",
        "movieNm",
        "total_audi"
    ]
)


treemap_df = treemap_df[
    treemap_df["total_audi"] > 0
]


fig2 = px.treemap(
    treemap_df,
    path=[
        "genre_first",
        "movieNm"
    ],
    values="total_audi",
    title="장르별 영화와 총 관객수"
)


fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)


fig2.update_layout(
    height=700,
    margin=dict(
        t=60,
        l=10,
        r=10,
        b=10
    )
)


st.plotly_chart(
    fig2,
    use_container_width=True
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "한 문장으로 작성해 보세요.",
    placeholder="예: ○○ 장르에서 총 관객수가 많은 영화가 크게 나타난다.",
    key="graph2_comment"
)


# ==========================================
# 그래프 3
# 총 관객수 히스토그램
# ==========================================

st.divider()

st.header("그래프 3. 영화별 총 관객수 분포")


hist_df = df[
    ["movieNm", "total_audi"]
].copy()


hist_df = hist_df.dropna(
    subset=[
        "movieNm",
        "total_audi"
    ]
)


hist_df = hist_df[
    hist_df["total_audi"] > 0
]


fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객수 분포",
    labels={
        "total_audi": "총 관객수",
        "count": "영화 편수"
    }
)


fig3.update_traces(
    hovertemplate=(
        "총 관객수 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)


fig3.update_layout(
    height=600,
    xaxis_title="총 관객수",
    yaxis_title="영화 편수"
)


st.plotly_chart(
    fig3,
    use_container_width=True
)


# 가장 관객이 많은 영화
most_popular = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

most_popular_name = most_popular["movieNm"]
most_popular_audi = int(
    most_popular["total_audi"]
)


# 영화가 가장 많이 몰린 구간
counts, bins = pd.cut(
    hist_df["total_audi"],
    bins=20,
    retbins=True
)

bin_counts = counts.value_counts().sort_index()

most_common_bin = bin_counts.idxmax()

lower_bound = int(
    most_common_bin.left
)

upper_bound = int(
    most_common_bin.right
)


st.subheader("그래프에서 알 수 있는 내용")

st.write(
    f"대부분의 영화는 **{lower_bound:,}명 ~ "
    f"{upper_bound:,}명** 정도의 총 관객수 구간에 몰려 있습니다."
)

st.write(
    f"가장 관객이 많은 영화는 **{most_popular_name}**으로, "
    f"총 관객수는 **{most_popular_audi:,}명**입니다."
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "한 문장으로 작성해 보세요.",
    placeholder="예: 대부분의 영화는 ○○명 이하에 몰려 있으며, 일부 영화만 매우 높은 관객수를 기록했다.",
    key="graph3_comment"
)


# ==========================================
# 그래프 4
# 개봉일 스크린수와 총 관객의 관계
# ==========================================

st.divider()

st.header("그래프 4. 개봉일 스크린수와 총 관객의 관계")


scatter_df = df[
    [
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi"
    ]
].copy()


scatter_df = scatter_df.dropna(
    subset=[
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi"
    ]
)


scatter_df = scatter_df[
    (scatter_df["first_scrn"] > 0)
    & (scatter_df["total_audi"] > 0)
]


fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "genre_first": "장르"
    }
)


fig4.update_traces(
    marker=dict(
        size=10,
        opacity=0.75
    ),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객수: %{y:,}명"
        "<extra></extra>"
    )
)


fig4.update_layout(
    height=650,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    legend_title="장르"
)


st.plotly_chart(
    fig4,
    use_container_width=True
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "한 문장으로 작성해 보세요.",
    placeholder="예: 개봉일 스크린수가 많을수록 총 관객수가 증가하는 경향이 나타난다.",
    key="graph4_comment"
)


# ==========================================
# 그래프 5
# 장르별 총 관객수 박스플롯
# ==========================================

st.divider()

st.header("그래프 5. 장르별 총 관객수 분포")


genre_movie_count = (
    df["genre_first"]
    .value_counts()
)


# 영화가 10편 이상인 장르만 선택
valid_genres = genre_movie_count[
    genre_movie_count >= 10
].index


box_df = df[
    df["genre_first"].isin(valid_genres)
].copy()


box_df = box_df[
    [
        "genre_first",
        "movieNm",
        "total_audi"
    ]
].dropna(
    subset=[
        "genre_first",
        "movieNm",
        "total_audi"
    ]
)


box_df = box_df[
    box_df["total_audi"] > 0
]


fig5 = px.box(
    box_df,
    x="genre_first",
    y="total_audi",
    color="genre_first",
    points="outliers",
    title="영화가 10편 이상인 장르별 총 관객수 분포",
    labels={
        "genre_first": "장르",
        "total_audi": "총 관객수"
    },
    hover_name="movieNm"
)


fig5.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)


fig5.update_layout(
    height=650,
    xaxis_title="장르",
    yaxis_title="총 관객수",
    showlegend=False
)


st.plotly_chart(
    fig5,
    use_container_width=True
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "한 문장으로 작성해 보세요.",
    placeholder="예: ○○ 장르는 영화별 총 관객수의 차이가 크게 나타난다.",
    key="graph5_comment"
)


# ==========================================
# 그래프 6
# 첫 주 관객수를 반영한 버블 그래프
# ==========================================

st.divider()

st.header("그래프 6. 첫 주 관객수를 반영한 버블 그래프")


bubble_df = df[
    [
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
].copy()


bubble_df = bubble_df.dropna(
    subset=[
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
)


bubble_df = bubble_df[
    (bubble_df["first_scrn"] > 0)
    & (bubble_df["total_audi"] > 0)
    & (bubble_df["first_week_audi"] > 0)
]


fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객수 - 첫 주 관객수 버블",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "first_week_audi": "첫 주 관객수",
        "genre_first": "장르"
    },
    size_max=50
)


fig6.update_traces(
    marker=dict(
        opacity=0.7
    ),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객수: %{y:,}명<br>"
        "첫 주 관객수: %{marker.size:,.0f}명"
        "<extra></extra>"
    )
)


fig6.update_layout(
    height=700,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    legend_title="장르"
)


st.plotly_chart(
    fig6,
    use_container_width=True
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "한 문장으로 작성해 보세요.",
    placeholder="예: 첫 주 관객수가 많은 영화일수록 총 관객수도 높은 경향이 나타난다.",
    key="graph6_comment"
)


# ==========================================
# 그래프 7
# 제작 국가 → 장르 선버스트
# ==========================================

st.divider()

st.header("그래프 7. 제작 국가와 장르별 영화 분포")


sunburst_df = df[
    [
        "nation",
        "genre_first",
        "movieNm"
    ]
].copy()


# 필요한 값이 없는 행 제거
sunburst_df = sunburst_df.dropna(
    subset=[
        "nation",
        "genre_first",
        "movieNm"
    ]
)


# 국가 → 장르 → 영화 구조의 선버스트
# 각 영화가 1편으로 계산되므로 칸의 크기는 영화 편수를 나타냄
sunburst_df["영화 편수"] = 1


fig7 = px.sunburst(
    sunburst_df,
    path=[
        "nation",
        "genre_first",
        "movieNm"
    ],
    values="영화 편수",
    title="제작 국가 → 장르 → 영화별 분포"
)


fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)


fig7.update_layout(
    height=750,
    margin=dict(
        t=60,
        l=10,
        r=10,
        b=10
    )
)


st.plotly_chart(
    fig7,
    use_container_width=True
)


st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "한 문장으로 작성해 보세요.",
    placeholder="예: 국가별로 제작된 영화의 장르 분포에 차이가 나타난다.",
    key="graph7_comment"
)
