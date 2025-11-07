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
    # Read the raw CSV without a header.  Pandas will assign integer column
    # numbers (0, 1, …) in this case.
    df_raw = pd.read_csv("questions.csv", header=None)
    # Use the first row as column names
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

    This function defines a handful of CSS variables for colours and sizes,
    styles the application background, the sidebar, a hero section, cards for
    questions and buttons.  The palette is based on dark emerald tones and
    metallic gold accents: the variables ``--emerald-*`` hold progressively
    lighter teal shades while ``--gold`` and ``--gold-hi`` provide the warm
    accent colours.  Shadows, borders and blur effects help delineate panels
    without using heavy boxes.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

        :root {
            /* Primary colour palette */
            --gold: #d4af37;        /* moderate yellow – 83% red, 69% green, 22% blue【485677116544312†L16-L32】 */
            --gold-hi: #ffd700;    /* pure yellow with 100% red and 84% green【958241556107692†L16-L19】 */
            --emerald-900: #083d3b; /* very dark cyan – 3% red, 24% green, 23% blue【398182562603330†L16-L20】 */
            --emerald-800: #0a4d4a; /* dark teal rich in green (RGB 10,77,74)【694270922192189†L54-L62】 */
            --emerald-700: #0e6963; /* dark shade of cyan (RGB 14,105,99)【404727479287283†L54-L62】 */
            --emerald: #066e68;     /* very dark cyan (RGB 6,110,104)【501709117854018†L16-L19】 */

            /* Panel colours and effects */
            /*
            The default panel transparency was extremely low, resulting in
            insufficient contrast between the question cards and the
            dark teal page background. To improve readability we increase
            the white alpha values so the cards stand out more while
            retaining the frosted glass effect. Raising the transparency
            values effectively lightens the card backgrounds and borders.
            */
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
            color: #F3FBFA;
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

        /* Force all text inside a question card to use a high-contrast
        colour. Without this, many of the paragraphs and labels inside
        question cards inherit dark grey text from Streamlit's default
        theme and become nearly invisible against the dark emerald
        background. The '!important' flags ensure our override wins. */
        .question-card, .question-card * {
            color: #EAFBF9 !important;
        }

        /*
        Improve the contrast and legibility of radio button labels and other
        textual elements against the dark background. Streamlit renders
        radio widgets using the BaseWeb library, which wraps labels
        inside <label> elements under a div with a data-baseweb="radio"
        attribute. Targeting that structure allows us to override the
        default grey colour and set a brighter tone that matches the
        overall palette. We also bump up the font weight for better
        definition.
        */
        div[data-baseweb="radio"] label {
            color: #F3FBFA !important;
            font-weight: 600;
        }

        /* Style the selected and unselected radio indicators. The
        ::before pseudo-element of each label draws the outer circle,
        while ::after draws the inner dot when selected. We tint these
        with our gold gradient for the selected state and a lighter
        emerald tone for the unselected state. */
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

        /* Adjust slider label colours to match the overall palette. Without
        these overrides the slider labels were rendered in a dark grey
        that blended into the background, making the selected values
        difficult to read. */
        div[data-baseweb="slider"] p,
        div[data-baseweb="slider"] span,
        div[data-baseweb="slider"] label {
            color: #F3FBFA !important;
        }

        /* Make all text inside the sidebar bright. Streamlit's sidebar
        elements often inherit dark text colours that are hard to read
        against a dark background. This rule ensures labels, slider
        values and button text stand out clearly. */
        [data-testid="stSidebar"] * {
            color: #F3FBFA !important;
        }

        /* Narrow the main content area and centre it on wide screens to
        improve readability. Streamlit by default stretches the layout
        across the full width of the browser window in wide mode, which
        can result in very long lines of text. Constraining the width
        makes paragraphs and question cards easier to scan and gives a
        more balanced look. */
        section[data-testid="stAppViewContainer"] > section.main {
            max-width: 920px;
            margin-left: auto;
            margin-right: auto;
        }

        /* Ensure general markdown text and list items are bright enough
        against the dark background. */
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4,
        .stMarkdown h5,
        .stMarkdown h6 {
            color: #F3FBFA !important;
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
        /* Primary buttons use the gold gradient */
        .btn-primary > button {
            background: linear-gradient(90deg, var(--gold), var(--gold-hi)) !important;
            color: #111 !important;
        }
        /* Secondary (ghost) buttons */
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

    The main function orchestrates loading the data, rendering the hero section
    with a welcoming message, handling user input in the sidebar, presenting
    questions in styled cards and finally evaluating the user's answers.  The
    overall layout is inspired by a dark emerald palette with golden accents.
    """
    # Set up page configuration and inject custom CSS once at the beginning
    st.set_page_config(page_title="Ứng dụng ôn tập & ôn thi", layout="wide")
    inject_css()

    # Sidebar brand and options
    st.sidebar.markdown('<div class="brand-box">QUIZ</div>', unsafe_allow_html=True)
    st.sidebar.header("⚙️ Tùy chọn")

    # Load data and show total count of questions
    df = load_data()
    total_questions = len(df)
    st.sidebar.write(f"Tổng số câu hỏi: **{total_questions}**")

    # Slider in the sidebar to select number of questions to practice
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

    # Sidebar button to create a new random quiz.  Wrap the button in a div
    # using the primary class to apply the gold gradient styling.
    with st.sidebar:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("🎲 Tạo đề ngẫu nhiên"):
            # Sample a subset of question indices without replacement
            sampled_indices = random.sample(range(total_questions), int(num_questions))
            st.session_state.quiz_questions = df.iloc[sampled_indices].reset_index(drop=True)
            st.session_state.answers = {}
            st.session_state.submitted = False
        st.markdown('</div>', unsafe_allow_html=True)

    # Render a hero section at the top of the page
    st.markdown(
        """
        <div class="hero">
          <h1>📚 Ôn tập & ôn thi cùng ''He''</h1>
          <p>Chào mừng bạn đến với ứng dụng ôn tập. Ứng dụng này giúp bạn ôn tập bộ câu hỏi trắc nghiệm bằng cách tạo đề ngẫu nhiên và chấm điểm tự động.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display the quiz if a set of questions has been generated
    if st.session_state.quiz_questions is not None:
        quiz_df: pd.DataFrame = st.session_state.quiz_questions

        # Use a form to collect answers from all questions at once
        with st.form("quiz_form"):
            for idx, row in quiz_df.iterrows():
                # Start a question card
                st.markdown("<div class='question-card'>", unsafe_allow_html=True)
                st.markdown(f"#### Câu {idx + 1}")
                st.markdown(f"**{row['Câu hỏi']}**")

                # Build the list of answer options, ignoring empty cells
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

                # Display the radio buttons for the answer choices
                selected = st.radio(
                    "Chọn phương án:",
                    options,
                    index=0,
                    key=f"q_{idx}",
                )
                st.session_state.answers[idx] = selected
                st.markdown("</div>", unsafe_allow_html=True)

            # Submit button inside the form.  Wrap in the primary button styling.
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            submitted = st.form_submit_button("✅ Nộp bài")
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                st.session_state.submitted = True

    # After submission, evaluate answers and present feedback
    if st.session_state.submitted and st.session_state.quiz_questions is not None:
        quiz_df: pd.DataFrame = st.session_state.quiz_questions
        correct_count = 0
        st.header("Kết quả")
        for idx, row in quiz_df.iterrows():
            user_answer = st.session_state.answers.get(idx)
            correct_letter = str(row["Đ.án đúng"]).strip().upper()
            # Map answer letter to the corresponding option column
            letter_map = {
                "A": "Phương án A",
                "B": "Phương án B",
                "C": "Phương án C",
                "D": "Phương án D",
                "E": "Phương án E",
            }
            correct_option = row[letter_map[correct_letter]]
            st.markdown(f"**Câu {idx + 1}:** {row['Câu hỏi']}")
            # Provide immediate feedback on the answer
            if user_answer == correct_option:
                st.success("✔️ Đúng")
                correct_count += 1
            else:
                st.error(f"❌ Sai. Đáp án đúng: {correct_option}")
            # Expandable section for reference information
            with st.expander("📝 Tham khảo"):
                st.write(f"**Số văn bản:** {row['Số văn bản tham chiếu (kèm trích yếu văn bản)']}")
                st.write(f"**Điều khoản:** {row['Điều khoản tham chiếu cụ thể']}")
            st.markdown("---")
        # Display the total score
        st.subheader(f"Bạn trả lời đúng **{correct_count}/{len(quiz_df)}** câu.")

        # Button to restart the quiz, styled as a secondary action
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("🔄 Làm lại"):
            reset_state()
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
