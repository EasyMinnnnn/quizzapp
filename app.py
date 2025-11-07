import streamlit as st
import pandas as pd
import random


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load the question bank from the CSV file.

    The CSV file delivered with this repository does not include a header row.  To
    normalise the dataset we treat the first row as the header and all
    subsequent rows as data.  This helper returns a DataFrame with the header
    properly assigned.
    """
    df_raw = pd.read_csv("questions.csv", header=None)
    header = df_raw.iloc[0]
    df = df_raw.iloc[1:].reset_index(drop=True)
    df.columns = header
    return df


def reset_state() -> None:
    """
    Reset session state variables used to track the current quiz.

    When starting a new quiz or after finishing one, this helper removes
    ``quiz_questions``, ``answers`` and ``submitted`` from ``st.session_state``.
    Streamlit will recreate these keys on demand in subsequent runs.
    """
    for key in ("quiz_questions", "answers", "submitted"):
        if key in st.session_state:
            del st.session_state[key]


def inject_css() -> None:
    """
    Inject a custom stylesheet that recreates the emerald–gold palette and
    layout from the example geocoder application.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

        :root {
            /* Primary colour palette */
            --gold: #d4af37;        
            --gold-hi: #ffd700;    
            --emerald-900: #083d3b;
            --emerald-800: #0a4d4a; 
            --emerald-700: #0e6963; 
            --emerald: #066e68;     

            /* Text and panel colours */
            --text-main: #F5E8C7;  /* warm beige tone for primary text */
            --answer-text: #FFEB3B; /* Light yellow for answer text - updated color */
            
            /* Panel colours and effects */
            --panel: rgba(255, 255, 255, 0.12);
            --panel-bd: rgba(255, 255, 255, 0.24);
            --shadow: 0 14px 36px rgba(0, 0, 0, 0.26);
            --r-lg: 18px;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        }

        /* Application background */
        .stApp {
            background: radial-gradient(1200px 600px at 15% -10%, #0D5A56 0%, var(--emerald-800) 58%, var(--emerald-900) 100%);
            color: var(--text-main);
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] > div:first-child {
            background: var(--emerald-700);
            padding-top: 8px;
        }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
            color: var(--gold);
        }
        .brand-box {
            border: 2px solid var(--gold);
            border-radius: 12px;
            padding: 10px 12px;
            text-align: center;
            color: var(--gold);
            font-weight: 900;
            letter-spacing: .6px;
            margin: 2px 8px 14px;
        }

        /* Hero section */
        .hero {
            position: relative;
            padding: 22px 26px;
            border-radius: 22px;
            background: linear-gradient(135deg, #0F7B74 0%, var(--emerald-700) 55%, var(--emerald-800) 100%);
            border: 1px solid var(--panel-bd);
            box-shadow: var(--shadow);
            margin: 8px 0 20px;
            overflow: hidden;
        }
        .hero:after {
            content: "";
            position: absolute;
            left: 22px;
            right: 22px;
            top: 10px;
            height: 8px;
            background: linear-gradient(90deg, var(--gold), var(--gold-hi));
            border-radius: 10px;
        }
        .hero h1 {
            margin: .55rem 0 .3rem;
            font-weight: 900;
            letter-spacing: .2px;
            color: var(--gold);
        }
        .hero p {
            margin: 0;
            color: #CFE7E5;
        }

        /* Question cards */
        .question-card {
            background: var(--panel);
            border: 1px solid var(--panel-bd);
            border-radius: var(--r-lg);
            box-shadow: var(--shadow);
            padding: 14px 16px;
            margin-bottom: 14px;
            backdrop-filter: blur(6px);
        }

        /* Force all text inside a question card to use the warm beige */
        .question-card, .question-card * {
            color: var(--text-main) !important;
        }

        /* Override colours for all elements within each radio group */
        div[data-baseweb="radio"],
        div[data-baseweb="radio"] * {
            color: var(--answer-text) !important;  /* Updated to light yellow */
        }

        /* Bolden radio labels for better legibility */
        div[data-baseweb="radio"] label {
            font-weight: 600;
        }

        /* Style the selected and unselected radio indicators */
        div[data-baseweb="radio"] input:not(:checked) + label::before {
            border-color: var(--emerald-700);
        }
        div[data-baseweb="radio"] input:checked + label::before {
            border-color: var(--gold);
            background-color: var(--gold);
        }
        div[data-baseweb="radio"] input:checked + label::after {
            background-color: var(--emerald-900);
        }

        /* Make all text inside the sidebar bright */
        [data-testid="stSidebar"] * {
            color: var(--text-main) !important;
        }

        /* Buttons */
        .stButton > button {
            border: 0;
            border-radius: 12px;
            padding: 10px 16px;
            font-weight: 800;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
            transition: transform .05s, filter .15s;
        }
        .btn-primary > button {
            background: linear-gradient(90deg, var(--gold), var(--gold-hi)) !important;
            color: #111 !important;
        }
        .btn-ghost > button {
            background: rgba(255, 255, 255, .10) !important;
            color: #fff !important;
            box-shadow: none;
        }
        .stButton > button:hover {
            filter: brightness(.97);
        }
        .stButton > button:active {
            transform: translateY(1px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """
    Entry point for the Streamlit quiz application.
    """
    st.set_page_config(page_title="Ứng dụng ôn tập & ôn thi", layout="wide")
    inject_css()

    # Sidebar brand and options
    st.sidebar.markdown('<div class="brand-box">QUIZ</div>', unsafe_allow_html=True)
    st.sidebar.header("⚙️ Tùy chọn")

    df = load_data()
    total_questions = len(df)
    st.sidebar.write(f"Tổng số câu hỏi: **{total_questions}**")

    num_questions = st.sidebar.slider(
        "Chọn số câu hỏi muốn ôn:",
        min_value=1,
        max_value=int(total_questions),
        value=min(10, total_questions),
        step=1,
    )

    # Initialise session state variables on first run
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = None
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    with st.sidebar:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("🎲 Tạo đề ngẫu nhiên"):
            sampled_indices = random.sample(range(total_questions), int(num_questions))
            st.session_state.quiz_questions = df.iloc[sampled_indices].reset_index(drop=True)
            st.session_state.answers = {}
            st.session_state.submitted = False
        st.markdown('</div>', unsafe_allow_html=True)

    # Render the quiz
    if st.session_state.quiz_questions is not None:
        quiz_df: pd.DataFrame = st.session_state.quiz_questions

        with st.form("quiz_form"):
            for idx, row in quiz_df.iterrows():
                st.markdown("<div class='question-card'>", unsafe_allow_html=True)
                st.markdown(f"#### Câu {idx + 1}")
                st.markdown(f"**{row['Câu hỏi']}**")

                options = []
                for col_name in [
                    "Phương án A",
                    "Phương án B",
                    "Phương án C",
                    "Phương án D",
                    "Phương án E",
                ]:
                    val = row[col_name]
                    if pd.notna(val) and str(val).strip() != "":
                        options.append(val)

                selected = st.radio("Chọn phương án:", options, index=0, key=f"q_{idx}")
                st.session_state.answers[idx] = selected
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            submitted = st.form_submit_button("✅ Nộp bài")
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                st.session_state.submitted = True

    if st.session_state.submitted and st.session_state.quiz_questions is not None:
        quiz_df: pd.DataFrame = st.session_state.quiz_questions
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

        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("🔄 Làm lại"):
            reset_state()
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
