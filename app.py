import pandas as pd
import streamlit as st

from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.scrapper.scrape import ScrapeReviews


# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Myntra Review Scraper",
    page_icon="🛍️",
    layout="wide",
)


# ---------------------- CUSTOM CSS (FLOW UI) ----------------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
}

/* Gradient background */
.stApp {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

/* Glass card effect */
.glass {
    background: rgba(255,255,255,0.35);
    padding: 25px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    animation: fadeIn 0.8s ease-in-out;
}

/* smooth fade animation */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

/* buttons */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(90deg,#ff6a88,#ff99ac);
    color: white;
    font-weight: 600;
    height: 45px;
}

/* dataframe */
[data-testid="stDataFrame"] {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------- TITLE ----------------------
st.markdown(
    """
    <h1 style='text-align:center;'>🛍️ Myntra Review Scraper</h1>
    <p style='text-align:center;font-size:18px;'>
    Scrape → Store → Analyze product reviews instantly
    </p>
    """,
    unsafe_allow_html=True
)


# ---------------------- SESSION INIT ----------------------
if "data" not in st.session_state:
    st.session_state["data"] = False

if SESSION_PRODUCT_KEY not in st.session_state:
    st.session_state[SESSION_PRODUCT_KEY] = None


# ---------------------- SIDEBAR ----------------------
st.sidebar.title("⚙️ Settings")
st.sidebar.info("Control scraping options here")


# ---------------------- FORM ----------------------
def form_input():

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        product = st.text_input(
            "🔎 Product Name",
            placeholder="Nike Shoes, Puma T-shirt..."
        )

    with col2:
        no_of_products = st.number_input(
            "📦 Number of Products",
            min_value=1,
            step=1,
            value=5
        )

    submitted = st.button("🚀 Scrape Reviews")

    st.markdown('</div>', unsafe_allow_html=True)

    if not submitted:
        return

    if not product.strip():
        st.warning("⚠️ Please enter a product name")
        return

    st.session_state[SESSION_PRODUCT_KEY] = product

    # ---------------- SCRAPING ----------------
    with st.spinner("🔄 Scraping reviews..."):

        try:
            scraper = ScrapeReviews(
                product_name=product,
                no_of_products=int(no_of_products)
            )

            scrapped_data = scraper.get_review_data()

            if scrapped_data is None or scrapped_data.empty:
                st.error("❌ No reviews found")
                return

            mongoio = MongoIO()
            mongoio.store_reviews(product_name=product, reviews=scrapped_data)

            st.session_state["data"] = True

        except Exception as e:
            st.error("❌ Scraping failed")
            st.exception(e)
            return

    # ---------------- SUCCESS UI ----------------
    st.balloons()
    st.success("✅ Reviews scraped & stored successfully!")


    # ---------------- METRICS ----------------
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Total Reviews", len(scrapped_data))

    with c2:
        st.metric("Product", product)

    with c3:
        st.metric("Products Scraped", no_of_products)


    # ---------------- DATA PREVIEW ----------------
    st.markdown("### 📄 Scraped Data Preview")

    st.dataframe(scrapped_data, use_container_width=True)


    # ---------------- DOWNLOAD ----------------
    csv = scrapped_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download CSV",
        csv,
        file_name=f"{product}_reviews.csv",
        mime="text/csv"
    )


# ---------------------- MAIN ----------------------
def main():
    form_input()


if __name__ == "__main__":
    main()

