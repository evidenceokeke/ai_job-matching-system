import streamlit as st
import json
import pandas as pd

st.set_page_config(layout="wide")

st.title("Top Job Matches")
st.divider()
top_matches = st.session_state.get("top_matches")
top_matches_df = pd.DataFrame(top_matches)
st.dataframe(top_matches_df, use_container_width=True, hide_index=True)
st.divider()

st.subheader("Recommendation")
data = st.session_state.get("recommendations")
# returns a string so change to dictionary
recommendation = json.loads(data['content'])
#st.write(recommendation) # check

st.markdown(f"**{recommendation['title']}**")
st.markdown(f"{recommendation['similarity_reason']}")
st.markdown(f"**Strengths:**")
strengths = recommendation['strengths']
for str in strengths:
    st.markdown(f"* {strengths[str]}")
st.markdown(f"**Weaknesses:**")
weakness = recommendation['weaknesses']
for weak in weakness:
    st.markdown(f"* {weakness[weak]}")

st.divider()