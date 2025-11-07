import streamlit as st
import pandas as pd
import random

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load question bank from CSV without header and set first row as header."""
    df_raw = pd.read_csv("questions.csv", header=None)
    # Use the first row as the header
    header = df_raw.iloc[0]
    df = df_raw.iloc[1:].reset_index(drop=True)
    df.columns = header
    return df

def reset_state():
    """Reset session state variables."""
    for key in ("quiz_questions", "answers", "submitted"):
        if key in st.session_state:
            del st.session_state[key]

def inject_css():
    """Inject custom CSS for better styling."""
    st.markdown("""
        <style>
            /* Hide the default Streamlit footer */
            footer {visibility: hidden;}
            /* Set a gentle gradient background */
            .stApp {
                background: linear-gradient(to bottom right, #eef2f7, #ffffff);
            }
            /* Style the cards for each question */
            .question-card {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            /* Style for buttons */
            .stButton>button {
                background-color: #0072B5;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            .stButton>button:hover {
                background-color: #005A94;
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Ứng dụng ôn tập & ôn thi", layout="wide")
    inject_css()

    st.title("📚 Ôn tập & ôn thi cùng ''He''")
    st.write(
         "Chào mừng bạn đến với không gian ôn tập của He. "
         "Cùng nhau luyện tập với những câu hỏi trắc nghiệm ngẫu nhiên, "
         "tự động chấm điểm và luôn đồng hành cùng nhau trên hành trình học tập này nhé!"
    )

    df = load_data()
    total_questions = len(df)
    st.sidebar.write(f"Tổng số câu hỏi: **{total_questions}**")

    # Tùy chọn ở sidebar
    num_questions = st.sidebar.slider(
        "Chọn số câu hỏi muốn ôn:",
        min_value=1,
        max_value=int(total_questions),
        value=min(10, total_questions),
        step=1,
    )

    # Khởi tạo session state
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = None
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Nút tạo đề ngẫu nhiên
    if st.sidebar.button("🎲 Tạo đề ngẫu nhiên"):
        sampled_indices = random.sample(range(total_questions), int(num_questions))
        st.session_state.quiz_questions = df.iloc[sampled_indices].reset_index(drop=True)
        st.session_state.answers = {}
        st.session_state.submitted = False

    # Hiển thị câu hỏi
    if st.session_state.quiz_questions is not None:
        quiz_df = st.session_state.quiz_questions
        with st.form("quiz_form"):
            for idx, row in quiz_df.iterrows():
                # Bắt đầu thẻ câu hỏi
                st.markdown("<div class='question-card'>", unsafe_allow_html=True)
                st.markdown(f"#### Câu {idx + 1}")
                st.markdown(f"**{row['Câu hỏi']}**")
                # Tạo danh sách đáp án
                options = []
                for col_name in ["Phương án A", "Phương án B", "Phương án C", "Phương án D", "Phương án E"]:
                    val = row[col_name]
                    if pd.notna(val) and str(val).strip() != "":
                        options.append(val)
                # Radio chọn đáp án
                selected = st.radio(
                    "Chọn phương án:",
                    options,
                    index=0,
                    key=f"q_{idx}",
                )
                st.session_state.answers[idx] = selected
                st.markdown("</div>", unsafe_allow_html=True)
            # Nút submit
            submitted = st.form_submit_button("✅ Nộp bài")
            if submitted:
                st.session_state.submitted = True

    # Chấm điểm và hiển thị kết quả
    if st.session_state.submitted and st.session_state.quiz_questions is not None:
        quiz_df = st.session_state.quiz_questions
        correct_count = 0
        st.header("Kết quả")
        for idx, row in quiz_df.iterrows():
            user_answer = st.session_state.answers.get(idx)
            correct_letter = str(row["Đ.án đúng"]).strip().upper()
            letter_map = {
                "A": "Phương án A",
                "B": "Phương án B",
                "C": "Phương án C",
                "D": "Phương án D",
                "E": "Phương án E",
            }
            correct_option = row[letter_map[correct_letter]]
            st.markdown(f"**Câu {idx + 1}:** {row['Câu hỏi']}")
            if user_answer == correct_option:
                st.success("✔️ Đúng")
                correct_count += 1
            else:
                st.error(f"❌ Sai. Đáp án đúng: {correct_option}")
            with st.expander("📝 Tham khảo"):
                st.write(f"**Số văn bản:** {row['Số văn bản tham chiếu (kèm trích yếu văn bản)']}")
                st.write(f"**Điều khoản:** {row['Điều khoản tham chiếu cụ thể']}")
            st.markdown("---")
        st.subheader(f"Bạn trả lời đúng **{correct_count}/{len(quiz_df)}** câu.")
        if st.button("🔄 Làm lại"):
            reset_state()

if __name__ == "__main__":
    main()
