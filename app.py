import streamlit as st
import pandas as pd
import random

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load question bank from CSV without header and set first row as header."""
    # Đọc file CSV không có header
    df_raw = pd.read_csv("questions.csv", header=None)
    # Dòng đầu tiên chứa header thực sự
    header = df_raw.iloc[0]
    df = df_raw.iloc[1:].reset_index(drop=True)
    df.columns = header
    return df

def reset_state():
    """Reset session state variables."""
    for key in ("quiz_questions", "answers", "submitted"):
        if key in st.session_state:
            del st.session_state[key]

def main():
    st.set_page_config(page_title="Ứng dụng ôn tập & ôn thi", layout="wide")
    st.title("📚 Ôn tập & ôn thi cùng ''He'' ")
    st.write(
        "Chào mừng bạn đến với ứng dụng ôn tập. Ứng dụng này giúp bạn ôn tập "
        "bộ câu hỏi trắc nghiệm bằng cách tạo đề ngẫu nhiên và chấm điểm tự động."
    )

    # Load the full question bank and fix columns
    df = load_data()
    total_questions = len(df)
    st.write(f"Tổng số câu hỏi trong ngân hàng: **{total_questions}**")

    # Chọn số câu hỏi
    num_questions = st.number_input(
        "Chọn số câu hỏi muốn ôn:",
        min_value=1,
        max_value=int(total_questions),
        value=min(10, total_questions),
        step=1,
    )

    # Khởi tạo session state nếu chưa có
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = None
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Nút tạo đề ngẫu nhiên
    if st.button("🎲 Tạo đề ngẫu nhiên"):
        sampled_indices = random.sample(range(total_questions), int(num_questions))
        st.session_state.quiz_questions = df.iloc[sampled_indices].reset_index(drop=True)
        st.session_state.answers = {}
        st.session_state.submitted = False

    # Nếu có đề, hiển thị câu hỏi trong form
    if st.session_state.quiz_questions is not None:
        quiz_df = st.session_state.quiz_questions
        with st.form("quiz_form"):
            for idx, row in quiz_df.iterrows():
                st.markdown(f"### Câu {idx + 1}")
                # Cột chứa câu hỏi là 'Câu hỏi'
                st.markdown(f"**{row['Câu hỏi']}**")
                # Lấy các phương án (lọc bỏ giá trị trống)
                options = []
                letter_map = {}  # Lưu chữ cái tương ứng với phương án
                for letter, col_name in zip(
                    ["A", "B", "C", "D", "E"],
                    ["Phương án A", "Phương án B", "Phương án C", "Phương án D", "Phương án E"],
                ):
                    val = row[col_name]
                    if pd.notna(val) and str(val).strip() != "":
                        options.append(val)
                        letter_map[letter] = val
                # Hiển thị radio chọn đáp án
                selected = st.radio(
                    "Chọn phương án:",
                    options,
                    index=0,
                    key=f"q_{idx}",
                )
                st.session_state.answers[idx] = selected
                st.markdown("---")
            # Nút submit trong form
            submitted = st.form_submit_button("✅ Nộp bài")
            if submitted:
                st.session_state.submitted = True

    # Sau khi nộp, chấm điểm và hiển thị kết quả
    if st.session_state.submitted and st.session_state.quiz_questions is not None:
        quiz_df = st.session_state.quiz_questions
        correct_count = 0
        st.header("Kết quả")
        for idx, row in quiz_df.iterrows():
            user_answer = st.session_state.answers.get(idx)
            correct_letter = str(row["Đ.án đúng"]).strip().upper()
            # Map chữ cái sang phương án tương ứng
            correct_col_map = {
                "A": "Phương án A",
                "B": "Phương án B",
                "C": "Phương án C",
                "D": "Phương án D",
                "E": "Phương án E",
            }
            correct_option = row[correct_col_map[correct_letter]]
            st.markdown(f"**Câu {idx + 1}:** {row['Câu hỏi']}")
            if user_answer == correct_option:
                st.success("✔️ Đúng")
                correct_count += 1
            else:
                st.error(f"❌ Sai. Đáp án đúng: {correct_option}")
            # Tham khảo
            with st.expander("📝 Tham khảo"):
                st.write(f"**Số văn bản:** {row['Số văn bản tham chiếu (kèm trích yếu văn bản)']}")
                st.write(f"**Điều khoản:** {row['Điều khoản tham chiếu cụ thể']}")
            st.markdown("---")
        st.subheader(f"Bạn trả lời đúng **{correct_count}/{len(quiz_df)}** câu.")
        if st.button("🔄 Làm lại"):
            reset_state()

if __name__ == "__main__":
    main()
