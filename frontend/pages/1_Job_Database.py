import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("Job Database")

# Manage page navigation state
if 'page' not in st.session_state:
    st.session_state.page = 'main'

if 'selected_job' not in st.session_state:
    st.session_state.selected_job = None

# Search input
search_query = st.text_input("Search for jobs")

# Fetch jobs from backend
@st.cache_data
def fetch_jobs(query=""):
    params = {"search": query} if query else {}
    response = requests.get(url="http://127.0.0.1:8000/jobs", params=params)
    if response.status_code == 200:
        return response.json()['job_list']
    else:
        return []

# Update job list
job_data = fetch_jobs(search_query)

# Show job detail view
def show_job_detail(job):
    st.header(job['title'])
    st.subheader(f"Company: {job['company']}")
    st.text(f"Location: {job['location']}")
    st.markdown(f"**Description:**\n{job['description']}")
    st.caption(f"Posted on: {job['date_posted']}")

    if st.button("Delete", key="delete_btn"):
        delete_url = f"http://127.0.0.1:8000/delete_job/{job['job_id']}"
        response = requests.delete(delete_url)
        if response.status_code == 200:
            st.success("Job deleted successfully.")
            st.session_state.page = 'main'
            st.rerun()
        else:
            st.error("Failed to delete job.")

    if st.button("Back", key="back_btn"):
        st.session_state.page = 'main'
        st.rerun()


# Show job list view
def show_job_list():
    st.subheader("Available Jobs")

    if not job_data:
        st.info("No jobs found. Try adjusting your search.")
        return

    for idx, job in enumerate(job_data):
        with st.container(border=True):
            st.markdown(f"**{job['title']}**")
            st.caption(f"Location: {job['location']}")
            if st.button("Details", key=f"detail_btn_{idx}"):
                st.session_state.selected_job = job
                st.session_state.page = 'detail'
                st.rerun()


# Page navigation
if st.session_state.page == 'main':
    show_job_list()
elif st.session_state.page == 'detail' and st.session_state.selected_job:
    show_job_detail(st.session_state.selected_job)
