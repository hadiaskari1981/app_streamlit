import ast
import os
import io
from collections import defaultdict
import matplotlib.ticker as ticker
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

app_password = os.getenv("STREAMLIT_APP_PASS")

# Password Protection
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False


def generate_csv(topics_list):

    # Create DataFrames for accepted and rejected topics
    dff = pd.DataFrame(topics_list, columns=["extracted_topic", "number_related_answers"])

    # accepted_df = pd.DataFrame({"Topic": topics_list, "Status": "Accepted"})

    # Save as CSV in memory buffer
    csv_buffer = io.StringIO()
    dff.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    csv_buffer.close()

    return csv_data

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
topics = defaultdict(list)
# topics_list = []
for i, row in df.iterrows():
    qa_id = row["question_answer_id"]
    answer = row["answer"]
    extracted_topics = ast.literal_eval(row["extracted_topics_10"])
    if len(extracted_topics) == 0:
        continue
    else:
        for t in extracted_topics:

            topics[t].append(answer)

            # k = (f"""**:blue[question answerer: ]**  {answer}
            # **:red[extracted topic: ]**  {t}""")
            # v = (qa_id, answer, t)
            # topics_list.append({
            #     k: v
            # })

flat_topics = []
for t, answers  in topics.items():
    nb_answers = len(answers)
    flat_topics.append((t, (t, nb_answers)))

flat_topics.sort(key=lambda x: x[1][1], reverse=True)



# flat_topics = [(key, value) for topic in topics for key, value in topic.items()]

# Initialize session state variables
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "accepted" not in st.session_state:
    st.session_state.accepted = []
if "rejected" not in st.session_state:
    st.session_state.rejected = []
if "ignored" not in st.session_state:
    st.session_state.ignored = []
if "stopped" not in st.session_state:
    st.session_state.stopped = False  # Tracks whether the process is stopped


# Function to handle button clicks
def handle_action(action):
    topic, t_nb_answers = flat_topics[st.session_state.current_index]
    if action == "accept":
        st.session_state.accepted.append(t_nb_answers)
    elif action == "reject":
        st.session_state.rejected.append(t_nb_answers)
    elif action == "ignore":
        st.session_state.ignored.append(t_nb_answers)
    st.session_state.current_index += 1


# Display the current topic
if not st.session_state.stopped and st.session_state.current_index < len(flat_topics):
    topic, topic_nb_answers = flat_topics[st.session_state.current_index]
    with st.container():

        st.markdown(f"""**:blue[extracted topic: ]**  {topic}   
            **:red[number of related answers : ]**  {topic_nb_answers[1]}""")

        # Buttons to accept, reject, or stop
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Accept", icon="👍", key="accept", use_container_width=True):
                handle_action("accept")
        with col2:
            if st.button("Reject", icon="👎", key="reject", use_container_width=True):
                handle_action("reject")
        with col3:
            if st.button("Ignore", icon="🙁", key="ignore", use_container_width=True):
                handle_action("ignore")
        with col4:
            if st.button("Stop"):
                st.session_state.stopped = True
else:
    st.write(f"### {len(st.session_state.accepted) + len(st.session_state.rejected) + len(st.session_state.ignored)} topics processed!")
    st.write(f"#### Accepted Values: {len(st.session_state.accepted)}")
    # st.write(len(st.session_state.accepted))
    st.write(f"#### Rejected Values: {len(st.session_state.rejected)}")
    # st.write(len(st.session_state.rejected))
    st.write(f"#### Ignored Values: {len(st.session_state.ignored)}")
    # st.write(len(st.session_state.rejected))

    # df_accepted = pd.DataFrame(st.session_state.accepted, columns=["question_answer_id", "answer", "extracted_topic"])
    # df_rejected = pd.DataFrame(st.session_state.rejected, columns=["question_answer_id", "answer", "extracted_topic"])

    # df_accepted.to_csv(os.path.join(project_abs_path, "app_streamlit/accepted_topics.csv"), index=False)
    # df_rejected.to_csv(os.path.join(project_abs_path, "app_streamlit/rejected_topics.csv"), index=False)


    labels = ["Accepted", "Rejected" , "Ignored"]
    sizes = [len(st.session_state.accepted), len(st.session_state.rejected), len(st.session_state.ignored)]
    colors = ["#4CAF50", "#FF5733", '#eeefff']  # Green for accepted, red for rejected

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

    import matplotlib.pyplot as plt

    # Example list of dictionaries with accepted and rejected topic frequencie

    # Extract topics (keys) and their corresponding frequencies (values) for accepted topics
    accepted_topics_names = [topic[0] for topic in st.session_state.accepted]
    accepted_frequencies = [topic[1] for topic in st.session_state.accepted]

    # Extract topics (keys) and their corresponding frequencies (values) for rejected topics
    rejected_topics_names = [topic[0] for topic in st.session_state.rejected]
    rejected_frequencies = [topic[1] for topic in st.session_state.rejected]

    fig, ax = plt.subplots()

    # Create a bar chart
    ax.bar(accepted_topics_names, accepted_frequencies, color='skyblue')

    # Adding labels and title
    # ax.set_xlabel('Topics')
    ax.set_ylabel('Number of Answers')
    ax.set_title('Accepted Topics')

    # Rotate x-axis labels to be vertical
    plt.xticks(rotation=90)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

    # Show the plot
    st.pyplot(fig)

    fig, ax = plt.subplots()

    # Create a bar chart
    ax.bar(rejected_topics_names, rejected_frequencies, color='salmon')

    # Adding labels and title
    # ax.set_xlabel('Topics')
    ax.set_ylabel('Number of Answers')
    ax.set_title('Rejected Topics')

    # Rotate x-axis labels to be vertical
    plt.xticks(rotation=90)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    # Show the plot
    st.pyplot(fig)

    # Create two columns for the buttons
    col1, col2 = st.columns(2)

    accepted_csv = generate_csv(st.session_state.accepted)
    rejected_csv = generate_csv(st.session_state.rejected)

    # Accepted topics download button in the first column (Green)
    with col1:
        st.download_button(
            label="Download Accepted Topics",
            data=accepted_csv,
            file_name="accepted_topics.csv",
            mime="text/csv",
            key="download_accepted"
        )

    # Rejected topics download button in the second column (Red)
    with col2:
        st.download_button(
            label="Download Rejected Topics",
            data=rejected_csv,
            file_name="rejected_topics.csv",
            mime="text/csv",
            key="download_rejected"
        )
