import ast
import os

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

app_password = os.getenv("STREAMLIT_APP_PASS")

# Password Protection
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

def check_password():
    if st.session_state["password"] == app_password:
        st.session_state.password_correct = True
    else:
        st.error("Incorrect password")

if not st.session_state.password_correct:
    st.text_input("Enter the password", type="password", on_change=check_password, key="password")
    st.stop()

project_abs_path = os.path.dirname(os.getcwd())
print(project_abs_path)

st.title('Accept or Reject the topic')
@st.cache_data
def load_date():
    df = pd.read_csv(os.path.join(project_abs_path, "app_streamlit/test_topic_detection_10_AZ_answers_25_11.csv"))
    return df

df = load_date()
topics = []
for i, row in df.head(20).iterrows():
    qa_id = row["question_answer_id"]
    answer = row["answer"]
    extracted_topics = ast.literal_eval(row["extracted_topics_10"])
    if len(extracted_topics) == 0:
        continue
    else:
        for t in extracted_topics:
            k = (f"""**:blue[question answerer: ]**  {answer}   
            **:red[extracted topic: ]**  {t}""")
            v = (qa_id, answer, t)
            topics.append({
                k: v
            })

flat_topics = [(key, value) for topic in topics for key, value in topic.items()]

# Initialize session state variables
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "accepted" not in st.session_state:
    st.session_state.accepted = []
if "rejected" not in st.session_state:
    st.session_state.rejected = []
if "stopped" not in st.session_state:
    st.session_state.stopped = False  # Tracks whether the process is stopped


# Function to handle button clicks
def handle_action(action):
    key, value = flat_topics[st.session_state.current_index]
    if action == "accept":
        st.session_state.accepted.append(value)
    elif action == "reject":
        st.session_state.rejected.append(value)
    st.session_state.current_index += 1


# Display the current topic
if not st.session_state.stopped and st.session_state.current_index < len(flat_topics):
    key, value = flat_topics[st.session_state.current_index]
    with st.container():

        st.markdown(f"{key}")

        # Buttons to accept, reject, or stop
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Accept", icon="👍", key="accept", use_container_width=True):
                handle_action("accept")
        with col2:
            if st.button("Reject", icon="👎", key="reject", use_container_width=True):
                handle_action("reject")
        with col3:
            if st.button("Stop and Show Pie Chart"):
                st.session_state.stopped = True
else:
    st.write(f"### {len(st.session_state.accepted) + len(st.session_state.rejected)} topics processed!")
    st.write(f"#### Accepted Values: {len(st.session_state.accepted)}")
    # st.write(len(st.session_state.accepted))
    st.write(f"#### Rejected Values: {len(st.session_state.rejected)}")
    # st.write(len(st.session_state.rejected))

    df_accepted = pd.DataFrame(st.session_state.accepted, columns=["question_answer_id", "answer", "extracted_topic"])
    df_rejected = pd.DataFrame(st.session_state.rejected, columns=["question_answer_id", "answer", "extracted_topic"])

    # df_accepted.to_csv(os.path.join(project_abs_path, "app_streamlit/accepted_topics.csv"), index=False)
    # df_rejected.to_csv(os.path.join(project_abs_path, "app_streamlit/rejected_topics.csv"), index=False)


    labels = ["Accepted", "Rejected"]
    sizes = [len(st.session_state.accepted), len(st.session_state.rejected)]
    colors = ["#4CAF50", "#FF5733"]  # Green for accepted, red for rejected

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        textprops={"fontsize": 14}
    )
    ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular

    # Display the pie chart
    st.pyplot(fig)

    st.download_button(
        label="Download Accepted Topics as CSV",
        data=df_accepted,
        file_name="accepted_topics.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Download Rejected Topics as CSV",
        data=df_rejected,
        file_name="rejected_topics.csv",
        mime="text/csv"
    )