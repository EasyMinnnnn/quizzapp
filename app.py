import streamlit as st
import pandas as pd
import random

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("questions.csv")
    return df

def display_sidebar():
    st.sidebar.title("Tùy chọn")
    num_questions = st.sidebar.slider("Chọn số câu hỏi", 1, 20, 10)  # Slider để chọn số câu hỏi
    return num_questions

def display_progress(progress: int, total: int):
    st.write(f"Tiến trình: {progress}/{total}")
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
    st.title("Ứng dụng Ôn Tập Trắc Nghiệm")
    
    num_questions = display_sidebar()
    df = load_data()
    total_questions = len(df)

    correct_answers = 0
    questions = df.sample(n=num_questions)

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
