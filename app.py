import streamlit as st
import pandas as pd
import random

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("questions.csv")
    return df

def reset_state() -> None:
    for key in ("quiz_questions", "answers", "submitted"):
        if key in st.session_state:
            del st.session_state[key]

def display_sidebar():
    st.sidebar.title("Tùy chọn")
    num_questions = st.sidebar.slider("Chọn số câu hỏi", 1, 20, 10)
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

    # Load data
    df = load_data()
    total_questions = len(df)
    st.write(f"Tổng số câu hỏi trong ngân hàng: **{total_questions}**")

    num_questions = display_sidebar()
    correct_answers = 0
    questions = df.sample(n=num_questions)

    # Display questions
    for idx, row in questions.iterrows():
        question = row['Câu hỏi']
        options = [row['A'], row['B'], row['C'], row['D'], row['E']]
        correct_answer = row['A']
        correct = display_question(question, options, correct_answer, idx + 1, total_questions)
        if correct:
            correct_answers += 1
        display_progress(idx + 1, total_questions)
    
    display_results(correct_answers, total_questions)

if __name__ == "__main__":
    main()
