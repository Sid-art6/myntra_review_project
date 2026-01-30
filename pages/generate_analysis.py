import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.data_report.generate_data_report import DashboardGenerator

mongo_con = MongoIO()


# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Review Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)


# ---------------------- STYLISH CSS ----------------------
st.markdown("""
<style>

/* ===============================
   FULL PAGE BACKGROUND FIX
   =============================== */

/* Remove Streamlit white background */
.main {
    background: transparent !important;
}

.block-container {
    background: transparent !important;
    padding-top: 2rem;
}


/* Gradient background for whole app */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Segoe UI', sans-serif;
}



/* ===============================
   CARDS
   =============================== */

.card {
    background: rgba(255,255,255,0.95);
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    margin-bottom: 25px;
    backdrop-filter: blur(6px);
}


/* Section titles */
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 15px;
    color: #333;
}



/* ===============================
   BUTTON STYLE
   =============================== */

.stButton>button {
    background: linear-gradient(90deg,#ff6a88,#ff99ac);
    color: white;
    border-radius: 14px;
    height: 48px;
    font-weight: 600;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
}



/* ===============================
   METRIC CARDS
   =============================== */

[data-testid="metric-container"] {
    background: white;
    padding: 15px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.1);
}



/* ===============================
   DATAFRAME
   =============================== */

[data-testid="stDataFrame"] {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)



# =========================================================
# ---------------------- CHART FUNCTIONS ------------------
# =========================================================

def rating_chart(df: pd.DataFrame):
    if "rating" not in df.columns:
        return

    fig, ax = plt.subplots()
    df["rating"].value_counts().sort_index().plot(kind="bar", ax=ax)
    ax.set_title("Rating Distribution")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Count")
    st.pyplot(fig)


def sentiment_chart(df: pd.DataFrame):
    if "sentiment" not in df.columns:
        return

    fig, ax = plt.subplots()
    df["sentiment"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    ax.set_title("Sentiment Split")
    st.pyplot(fig)


def reviews_per_product_chart(df: pd.DataFrame):
    if "product_name" not in df.columns:
        return

    fig, ax = plt.subplots()
    df["product_name"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Reviews per Product")
    ax.set_xlabel("Product")
    ax.set_ylabel("Reviews")
    st.pyplot(fig)


# =========================================================
# ---------------------- ANALYSIS PAGE --------------------
# =========================================================

def create_analysis_page(review_data: pd.DataFrame) -> None:

    if review_data is None or review_data.empty:
        st.warning("⚠️ No review data available for analysis.")
        return


    # ---------------- KPIs ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Overview</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Total Reviews", len(review_data))

    with c2:
        if "rating" in review_data.columns:
            st.metric("Average Rating", round(review_data["rating"].mean(), 2))

    with c3:
        if "sentiment" in review_data.columns:
            pos = (review_data["sentiment"] == "Positive").sum()
            st.metric("Positive Reviews", pos)

    st.markdown('</div>', unsafe_allow_html=True)


    # ---------------- DATA PREVIEW ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Dataset Preview</div>', unsafe_allow_html=True)

    st.dataframe(review_data, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


    # ---------------- CHARTS ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Visual Analytics</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        rating_chart(review_data)

    with col2:
        sentiment_chart(review_data)

    reviews_per_product_chart(review_data)

    st.markdown('</div>', unsafe_allow_html=True)


    # ---------------- DETAILED REPORT ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧠 Detailed Analysis</div>', unsafe_allow_html=True)

    if st.button("🚀 Generate Detailed Report"):
        dashboard = DashboardGenerator(review_data)
        dashboard.display_general_info()
        dashboard.display_product_sections()

    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# ---------------------- MAIN -----------------------------
# =========================================================

def main():

    st.title("📊 Product Review Analytics Dashboard")
    st.caption("Clean • Stylish • Professional • Insightful")


    # Check if data exists
    if "data" not in st.session_state or not st.session_state.get("data"):
        with st.sidebar:
            st.info(
                "🔍 No data selected.\n\n"
                "Go to **Search Page → Scrape Reviews → Come back here**"
            )
        st.stop()


    product_name = st.session_state.get(SESSION_PRODUCT_KEY)

    if not product_name:
        st.error("❌ Product not found in session.")
        st.stop()


    try:
        data = mongo_con.get_reviews(product_name=product_name)
        create_analysis_page(data)

    except Exception as e:
        st.error("❌ Failed to load review data.")
        st.exception(e)


# =========================================================
# ---------------------- ENTRY ----------------------------
# =========================================================

if __name__ == "__main__":
    main()
