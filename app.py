import streamlit as st
import pandas as pd
import random


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the question bank from the CSV file.

    The CSV is expected to live alongside this script under the name
    ``questions.csv`` and to contain the following columns:

    - ``TT``: ordinal number of the question.
    - ``Câu hỏi``: the question text.
    - ``Phương án A`` … ``Phương án E``: up to five answer options.  Not all
      questions have five options; empty cells are ignored.
    - ``Đ.án đúng``: the letter (A–E) identifying the correct option.
    - ``Số văn bản tham chiếu (kèm trích yếu văn bản)``: reference text.
    - ``Điều khoản tham chiếu cụ thể``: specific clause reference.

    The dataset is cached using Streamlit’s ``@st.cache_data`` decorator to
    avoid reloading on every page refresh.  See the Streamlit documentation
    for details on how session caching works.
    """
    df = pd.read_csv("questions.csv")
    return df


def reset_state() -> None:
    """Reset all session state variables used by the quiz.

    When starting a new quiz or after finishing one, this helper resets
    ``quiz_questions``, ``answers`` and ``submitted``.  Using Streamlit’s
    session state API allows variables to persist across reruns of the app
    while still being mutable.  The documentation notes that session state
    provides a way to share variables between reruns for each user session
    【878874102014481†L186-L190】.
    """
    for key in ("quiz_questions", "answers", "submitted"):
        if key in st.session_state:
            del st.session_state[key]


def main() -> None:
    """Entry point for the Streamlit quiz app.

    This function sets up the layout, loads the data, allows the user to
    generate a random set of questions and tracks the user’s answers.  After
    submission, it displays correctness feedback and shows reference
    information for each question.
    """
    st.set_page_config(page_title="Ứng dụng ôn tập & ôn thi", layout="wide")
    st.title("📚 Ôn tập & ôn thi cùng "He"")
    st.write(
        "Chào mừng bạn đến với ứng dụng ôn tập. Ứng dụng này giúp bạn ôn tập "
        "bộ câu hỏi trắc nghiệm bằng cách tạo đề ngẫu nhiên và chấm điểm tự động."
    )

    # Load the full question bank once and cache it.
    df = load_data()
    total_questions = len(df)
    st.write(f"Tổng số câu hỏi trong ngân hàng: **{total_questions}**")

    # Choose how many questions to practice. Default to 10 or the total count.
    num_questions = st.number_input(
        "Chọn số câu hỏi muốn ôn:",
        min_value=1,
        max_value=int(total_questions),
        value=min(10, total_questions),
        step=1,
    )

    # Ensure persistent containers exist
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = None
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Button to create a new random quiz
    if st.button("🎲 Tạo đề ngẫu nhiên"):
        # Randomly sample unique question indices without replacement.  Using
        # ``random.sample`` guarantees that each selected index is unique
        # 【483697754635941†L25-L33】.  This avoids repeating the same question
        # within a single quiz session.
        sampled_indices = random.sample(range(total_questions), int(num_questions))
        # Save the subset into session state and reset answers
        st.session_state.quiz_questions = df.iloc[sampled_indices].reset_index(drop=True)
        st.session_state.answers = {}
        st.session_state.submitted = False

    # If there is an active quiz, display the questions
    if st.session_state.quiz_questions is not None:
        quiz_df: pd.DataFrame = st.session_state.quiz_questions
        # Use a form to collect all answers before submission
        with st.form("quiz_form"):
            for idx, row in quiz_df.iterrows():
                st.markdown(f"### Câu {idx + 1}")
                st.markdown(f"**{row['Câu hỏi']}**")
                # Collect available answer options by filtering out empty cells
                options = []
                option_labels = []  # Keep track of original letters for mapping
                for letter, col_name in zip(
                    ["A", "B", "C", "D", "E"],
                    ["Phương án A", "Phương án B", "Phương án C", "Phương án D", "Phương án E"],
                ):
                    val = row[col_name]
                    if pd.notna(val) and str(val).strip() != "":
                        options.append(val)
                        option_labels.append(letter)
                # Display the radio buttons.  The ``st.radio`` widget returns
                # the chosen option as a string 【838013446759973†L240-L348】.  We use
                # a unique key per question to avoid conflicts.
                selected = st.radio(
                    "Chọn phương án:",
                    options,
                    index=0,
                    key=f"q_{idx}",
                )
                # Store the selected answer in session state
                st.session_state.answers[idx] = selected
                st.markdown("---")
            # Submit button inside form
            submitted = st.form_submit_button("✅ Nộp bài")
            if submitted:
                st.session_state.submitted = True

    # After submission, evaluate answers and show feedback
    if st.session_state.submitted and st.session_state.quiz_questions is not None:
        quiz_df: pd.DataFrame = st.session_state.quiz_questions
        correct_count = 0
        st.header("Kết quả")
        for idx, row in quiz_df.iterrows():
            user_answer = st.session_state.answers.get(idx)
            correct_letter = str(row["Đ.án đúng"]).strip().upper()
            # Map letter to the actual text of the correct option
            letter_map = {
                "A": "Phương án A",
                "B": "Phương án B",
                "C": "Phương án C",
                "D": "Phương án D",
                "E": "Phương án E",
            }
            correct_option = row[letter_map.get(correct_letter)]
            st.markdown(f"**Câu {idx + 1}:** {row['Câu hỏi']}")
            # Compare the user's answer to the correct one
            if user_answer == correct_option:
                st.success("✔️ Đúng")
                correct_count += 1
            else:
                st.error(f"❌ Sai. Đáp án đúng: {correct_option}")
            # Show reference information in an expander
            with st.expander("📝 Tham khảo"):
                doc = row[
                    "Số văn bản tham chiếu (kèm trích yếu văn bản)"
                ]
                clause = row["Điều khoản tham chiếu cụ thể"]
                st.write(f"**Số văn bản:** {doc}")
                st.write(f"**Điều khoản:** {clause}")
            st.markdown("---")
        st.subheader(
            f"Bạn trả lời đúng **{correct_count}/{len(quiz_df)}** câu."
        )
        # Allow restarting the quiz
        if st.button("🔄 Làm lại"):
            reset_state()


if __name__ == "__main__":
    main()
