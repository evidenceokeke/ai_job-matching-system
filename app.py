import streamlit as st
import json
import requests
import pandas as pd

st.set_page_config(layout="wide")

st.title("Job Match")
st.markdown("Job Matching System. Upload the resume to see if the candidate matches with any job in the system")
st.divider()

# to display if i navigate back and forth pages after i have uploaded a file?
parsed_data = st.session_state.get("parsed_data")
resume_id = st.session_state.get("resume_id")

if 'process_done' not in st.session_state:
    st.session_state['process_done'] = False

uploaded_file = st.file_uploader(label="Select a file. Only accepts pdf", type="pdf", accept_multiple_files=False)
if uploaded_file and not st.session_state.process_done:
    with st.spinner("Parsing resume... please wait"):
        try:
            # Send file to FastAPI backend
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            response = requests.post(url= "http://127.0.0.1:8000/resumes", files=files)

            if response.status_code == 200:
                data = response.json()
                st.success("Resume parsed successfully!")

                # Save in session state
                st.session_state["parsed_data"] = data["parsed_data"]
                st.session_state["resume_id"] = data["parsed_data"]["resume_id"]

                # so that the match button can show
                st.session_state["process_done"] = True
                st.rerun() # Rerun to update the UI
            else:
                st.error(f"Error: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Failed to upload to parse resume: {e}")

# Show parsed data
if st.session_state.get("parsed_data"):
    st.subheader("Parsed Resume Data:")
    container = st.container(border=True)
    with container:
        st.write(f"**Name**: {parsed_data['resume_data']['name']}")
        st.write(f"**Email**: {parsed_data['resume_data']['email']}")
        st.write(f"**Phone Number**: {parsed_data['resume_data']['phone']}")
        st.write(f"**Location**: {parsed_data['resume_data'].get('location', 'Not Provided')}")
        st.write("**Education**")
        edu_df = pd.DataFrame(parsed_data['resume_data']['education'])
        st.table(edu_df)
        st.write("**Experience**")
        for exp in parsed_data['resume_data']['experience']:
            st.write(f"Company: {exp.get('Company', 'Not Provided')}")
            st.write(f"Position: {exp.get('position', 'Not Provided')}")
            st.write(f"Location: {exp.get('location', 'Not Provided')}")
            st.write(f"Duration: {exp.get('duration', 'Not Provided')}")
            st.write("Responsibilities")
            r = ''
            for res in exp['responsibilities']:
                r += "- " + res + "\n"
            st.markdown(r)
            st.divider()
        st.write("**Skills**")
        s = ''
        for skill in parsed_data['resume_data']['skills']:
            s += "- " + skill + "\n"
        st.markdown(s)
        st.write("**Certifications**")
        if parsed_data['resume_data'].get('certifications', 0) != 0:
            cert_df = pd.DataFrame(parsed_data['resume_data']['certifications'])
            st.table(cert_df)
        else:
            st.write("Not Provided")


# Matching button appears after resume data is parsed and displayed
if st.session_state.process_done:
    if st.button("Initialize Matching Process"):
        with st.spinner("Searching for Job Matches..."):
            # Get the resume id
            resume_id = st.session_state.get("resume_id")

            # Send the request to FASTAPI
            response = requests.post(url= f"http://127.0.0.1:8000/match_candidate/{resume_id}")

            if response.status_code == 200:
                data = response.json()
                st.success("Matching Algorithm Complete.")

                # save to session state
                st.session_state['top_matches'] = data["top_matches"]

                # if there were any top matches, the recommendations will be part of the result
                data.get("recommendations", 0)

                if data["recommendations"] != 0:
                    st.session_state["recommendations"] = data["recommendations"]
                else:
                    st.session_state["recommendations"] = "No jobs to recommend."

                # switch to results page
                st.switch_page("pages/2_Job_Results.py")