import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 중 "
    "해당 기간에 개봉한 216편의 데이터를 분석합니다."
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# ==================================================
# 데이터 불러오기
# ==================================================

try:
    df = pd.read_csv(DATA_URL)
except Exception:
    st.error("데이터를 불러오는 데 문제가 발생했습니다.")
    st.stop()


# ==================================================
# 데이터 전처리
# ==================================================

df["openDt"] = pd.to_datetime(
    df["openDt"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)

# 여러 장르가 있는 경우 첫 번째 장르만 사용
df["genre_main"] = (
    df["genre"]
    .fillna("미분류")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

# 숫자 데이터 변환
for col in ["total_audi", "first_scrn", "first_week_audi"]:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)


# ==================================================
# 1. 장르별 영화 편수 도넛 차트
# ==================================================

st.header("1. 장르별 영화 편수")

genre_count = (
    df["genre_main"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["genre", "영화 편수"]

fig1 = px.pie(
    genre_count,
    names="genre",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig1.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="가장 많은 영화가 어떤 장르인지 적어 보세요.",
    key="graph1_note"
)

st.divider()


# ==================================================
# 2. 장르 → 영화 트리맵
# ==================================================

st.header("2. 장르별 영화 총관객 분포")

fig2 = px.treemap(
    df,
    path=["genre_main", "movieNm"],
    values="total_audi",
    title="장르에서 영화로 내려가는 총관객 분포"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="어떤 장르에 관객이 많이 몰려 있는지 적어 보세요.",
    key="graph2_note"
)

st.divider()


# ==================================================
# 3. 총 관객 수 히스토그램
# ==================================================

st.header("3. 영화별 총 관객 수 분포")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 분포"
)

fig3.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 수: %{x:,.0f}명<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# 가장 많이 몰린 관객 구간
try:
    categories = pd.cut(
        df["total_audi"],
        bins=20
    )

    interval_counts = categories.value_counts().sort_index()

    if len(interval_counts) > 0:
        most_common_interval = interval_counts.idxmax()

        lower = int(most_common_interval.left)
        upper = int(most_common_interval.right)

        st.write(
            f"대부분의 영화는 약 {lower:,}명 ~ {upper:,}명의 "
            f"총 관객 구간에 가장 많이 몰려 있습니다."
        )

except Exception:
    pass

# 총 관객이 가장 많은 영화
if len(df) > 0:
    max_movie = df.loc[df["total_audi"].idxmax()]

    st.write(
        f"총 관객이 가장 많은 영화는 「{max_movie['movieNm']}」으로, "
        f"총 {int(max_movie['total_audi']):,}명의 관객을 기록했습니다."
    )

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="영화들의 총 관객 수가 어느 구간에 많이 분포하는지 적어 보세요.",
    key="graph3_note"
)

st.divider()


# ==================================================
# 4. 개봉 첫날 스크린 수 vs 총 관객 산점도
# ==================================================

st.header("4. 개봉 첫날 스크린 수와 총 관객의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    title="개봉 첫날 스크린 수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉 첫날 스크린 수",
        "total_audi": "총 관객 수",
        "genre_main": "장르"
    },
    custom_data=[
        "first_scrn",
        "total_audi"
    ]
)

fig4.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉 첫날 스크린: %{customdata[0]:,.0f}개<br>"
        "총 관객: %{customdata[1]:,.0f}명"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="스크린 수와 총 관객 사이에 어떤 관계가 있는지 적어 보세요.",
    key="graph4_note"
)

st.divider()


# ==================================================
# 5. 장르별 총 관객 박스플롯
# ==================================================

st.header("5. 장르별 총 관객 분포")

genre_movie_counts = df["genre_main"].value_counts()

valid_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index

box_df = df[
    df["genre_main"].isin(valid_genres)
].copy()

if len(box_df) > 0:

    fig5 = px.box(
        box_df,
        x="genre_main",
        y="total_audi",
        points="outliers",
        hover_name="movieNm",
        title="영화가 10편 이상인 장르의 총 관객 분포",
        labels={
            "genre_main": "장르",
            "total_audi": "총 관객 수"
        }
    )

    fig5.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "총 관객: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

else:
    st.info("영화가 10편 이상인 장르가 없습니다.")

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="장르별 총 관객 분포의 차이를 적어 보세요.",
    key="graph5_note"
)

st.divider()


# ==================================================
# 6. 첫 주 관객을 크기로 나타낸 버블 그래프
# ==================================================

st.header("6. 첫 주 관객을 크기로 나타낸 버블 그래프")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_main",
    hover_name="movieNm",
    size_max=50,
    title="개봉 첫날 스크린 수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉 첫날 스크린 수",
        "total_audi": "총 관객 수",
        "first_week_audi": "첫 주 관객",
        "genre_main": "장르"
    },
    custom_data=[
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉 첫날 스크린: %{customdata[0]:,.0f}개<br>"
        "총 관객: %{customdata[1]:,.0f}명<br>"
        "첫 주 관객: %{customdata[2]:,.0f}명"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="버블의 크기와 총 관객의 관계를 적어 보세요.",
    key="graph6_note"
)

st.divider()


# ==================================================
# 7. 제작 국가 → 장르 선버스트
# ==================================================

st.header("7. 제작 국가별 장르 분포")

sunburst_df = df.copy()

sunburst_df["nation"] = (
    sunburst_df["nation"]
    .fillna("미분류")
    .astype(str)
    .str.strip()
)

sunburst_df["genre_main"] = (
    sunburst_df["genre_main"]
    .fillna("미분류")
    .astype(str)
    .str.strip()
)

sunburst_data = (
    sunburst_df
    .groupby(["nation", "genre_main"])
    .size()
    .reset_index(name="영화 편수")
)

fig7 = px.sunburst(
    sunburst_data,
    path=["nation", "genre_main"],
    values="영화 편수",
    title="제작 국가에서 장르로 내려가는 영화 분포"
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    height=700
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="제작 국가별 영화 장르 분포의 특징을 한 문장으로 적어 보세요.",
    key="graph7_note"
)

st.divider()


# ==================================================
# 8. 장르별 평균 첫 주 관객 수
# ==================================================

st.header("8. 장르별 평균 첫 주 관객 수")

genre_first_week = (
    df.groupby("genre_main")["first_week_audi"]
    .mean()
    .reset_index()
)

genre_first_week.columns = [
    "genre_main",
    "평균 첫 주 관객"
]

genre_first_week = genre_first_week.sort_values(
    "평균 첫 주 관객",
    ascending=False
)

fig8 = px.bar(
    genre_first_week,
    x="genre_main",
    y="평균 첫 주 관객",
    title="장르별 평균 첫 주 관객 수",
    labels={
        "genre_main": "장르",
        "평균 첫 주 관객": "평균 첫 주 관객 수"
    }
)

fig8.update_traces(
    hovertemplate=(
        "<b>%{x}</b><br>"
        "평균 첫 주 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig8.update_layout(
    xaxis_title="장르",
    yaxis_title="평균 첫 주 관객 수",
    height=600
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

# 가장 높은 평균을 기록한 장르
if len(genre_first_week) > 0:
    top_genre = genre_first_week.iloc[0]

    st.write(
        f"평균 첫 주 관객 수가 가장 높은 장르는 "
        f"「{top_genre['genre_main']}」이며, "
        f"평균 약 {top_genre['평균 첫 주 관객']:,.0f}명의 "
        f"첫 주 관객을 기록했습니다."
    )

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="장르별 평균 첫 주 관객 수의 차이를 적어 보세요.",
    key="graph8_note"
)

st.divider()


# ==================================================
# 다음 그래프
# ==================================================

st.header("9. 다음 그래프")
st.info("아홉 번째 그래프를 이 아래에 추가할 수 있습니다.")
