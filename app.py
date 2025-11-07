import streamlit as st
import pandas as pd
import random


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the question bank from the CSV file."""
    df = pd.read_csv("questions.csv")
    return df


def reset_state() -> None:
    """Reset all session state variables used by the quiz."""
    for key in ("quiz_questions", "answers", "submitted"):
        if key in st.session_state:
            del st.session_state[key]


def display_sidebar():
    st.sidebar.title("Tùy chọn")
    num_questions = st.sidebar.slider("Chọn số câu hỏi", 1, 20, 10)  # Slider để chọn số câu hỏi
    return num_questions


def display_progress(progress: int, total: int):
    st.progress(progress / total)


def display_question(question, options, correct_answer, question_number, total_questions):
    st.subheader(f"Câu {question_number}/{total_questions}")
    st.write(question)
    answer = st.radio("Lựa chọn đáp án:", options)

    if answer:
        if answer == correct_answer:
            st.success("Đúng rồi!")
        else:
            st.error(f"Sai rồi! Đáp án đúng là: {correct_answer}")

    return answer == correct_answer


def display_results(correct_answers, total_questions):
    st.write(f"Bạn đã trả lời đúng {correct_answers}/{total_questions} câu.")
    st.button("Làm lại")


def main():
    st.set_page_config(page_title="Ứng dụng ôn tập & ôn thi", layout="wide")
    st.title("📚 Ôn tập & ôn thi cùng ''He'' ")
    st.write(
        "Chào mừng bạn đến với ứng dụng ôn tập. Ứng dụng này giúp bạn ôn tập "
        "bộ câu hỏi trắc nghiệm bằng cách tạo đề ngẫu nhiên và chấm điểm tự động."
    )

    # Load the full question bank once and cache it.
    df = load_data()
    total_questions = len(df)
    st.write(f"Tổng số câu hỏi trong ngân hàng: **{total_questions}**")

    # Choose how many questions to practice. Default to 10 or the total count.
    num_questions = display_sidebar()

    # Ensure persistent containers exist
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = None
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Button to create a new random quiz
    if st.button("🎲 Tạo đề ngẫu nhiên"):
        # Randomly sample unique question indices without replacement.
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
                # Đảm bảo cột câu hỏi tồn tại và truy cập đúng
                st.markdown(f"### Câu {idx + 1}")
                st.markdown(f"**{row['Unnamed: 1']}**")

                # Collect available answer options by filtering out empty cells
                options = []
                option_labels = []  # Keep track of original letters for mapping
                for letter, col_name in zip(
                    ["A", "B", "C", "D", "E"],
                    ["Unnamed: 2", "Unnamed: 3", "Unnamed: 4", "Unnamed: 5", "Unnamed: 6"],
                ):
                    val = row[col_name]
                    if pd.notna(val) and str(val).strip() != "":
                        options.append(val)
                        option_labels.append(letter)

                # Display the radio buttons. We use a unique key per question to avoid conflicts.
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
                "A": "Unnamed: 2",
                "B": "Unnamed: 3",
                "C": "Unnamed: 4",
                "D": "Unnamed: 5",
                "E": "Unnamed: 6",
            }
            correct_option = row[letter_map.get(correct_letter)]
            st.markdown(f"**Câu {idx + 1}:** {row['Unnamed: 1']}")
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
