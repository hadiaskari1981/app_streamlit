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


# Display the current topic or pie chart
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
    # Pie chart data
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

    st.write("#### Accepted Topics:", len(st.session_state.accepted))
    st.write("#### Rejected Topics:", len(st.session_state.rejected))
