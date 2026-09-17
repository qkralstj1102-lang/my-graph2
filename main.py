# -------------------------
# 일곱 번째 그래프
# 제작 국가 → 장르 선버스트
# -------------------------

st.header("7. 제작 국가별 장르 분포")

sunburst_df = df.copy()

# 제작 국가와 장르의 빈 값 처리
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

# 제작 국가 → 장르 구조의 영화 편수 계산
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

st.plotly_chart(fig7, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="제작 국가별 영화 장르 분포의 특징을 한 문장으로 적어 보세요.",
    key="graph7_note"
)

st.divider()

# -------------------------
# 이후 그래프 추가 영역
# -------------------------

st.header("8. 다음 그래프")
st.info("여덟 번째 그래프를 이 아래에 추가할 수 있습니다.")
