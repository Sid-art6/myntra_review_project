import streamlit as st
import pandas as pd
import plotly.express as px
import sys

from src.exception import CustomException


class DashboardGenerator:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self._clean_data()
        self._style()   # ⭐ inject styling


    # =========================================================
    # 🎨 STYLING (makes dashboard beautiful)
    # =========================================================
    def _style(self):

        st.markdown("""
        <style>

        /* remove white background */
        .main {background: transparent !important;}
        .block-container {padding-top: 1.5rem;}

        /* glass cards */
        .dash-card {
            background: rgba(255,255,255,0.96);
            padding: 22px;
            border-radius: 18px;
            box-shadow: 0 10px 28px rgba(0,0,0,0.12);
            margin-bottom: 25px;
        }

        .dash-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 12px;
        }

        </style>
        """, unsafe_allow_html=True)


    # =========================================================
    # 🧹 DATA CLEANING
    # =========================================================
    def _clean_data(self):

        try:
            self.data["Over_All_Rating"] = pd.to_numeric(
                self.data["Over_All_Rating"], errors="coerce"
            )

            self.data["Rating"] = pd.to_numeric(
                self.data["Rating"], errors="coerce"
            )

            self.data["Price"] = (
                self.data["Price"]
                .astype(str)
                .str.replace("₹", "", regex=False)
                .str.replace(",", "", regex=False)
            )

            self.data["Price"] = pd.to_numeric(self.data["Price"], errors="coerce")

        except Exception as e:
            raise CustomException(e, sys)


    # =========================================================
    # 📊 GENERAL INFO + KPI + 2 MAIN CHARTS
    # =========================================================
    def display_general_info(self):

        st.markdown('<div class="dash-title">📊 General Product Insights</div>', unsafe_allow_html=True)


        # ---------------- KPI CARDS ----------------
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Reviews", len(self.data))
        c2.metric("Avg Rating", round(self.data["Over_All_Rating"].mean(), 2))
        c3.metric("Avg Price", f"₹{round(self.data['Price'].mean(), 2)}")
        c4.metric("Products", self.data["Product Name"].nunique())


        # ---------------- CHART ROW ----------------
        col1, col2 = st.columns(2)


        # ⭐ Chart 1 → Rating donut
        with col1:
            st.markdown('<div class="dash-card">', unsafe_allow_html=True)

            rating_df = (
                self.data.groupby("Product Name", as_index=False)["Over_All_Rating"]
                .mean()
            )

            fig = px.pie(
                rating_df,
                values="Over_All_Rating",
                names="Product Name",
                hole=0.6,
                title="Average Rating Share",
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


        # ⭐ Chart 2 → Price bar
        with col2:
            st.markdown('<div class="dash-card">', unsafe_allow_html=True)

            price_df = (
                self.data.groupby("Product Name", as_index=False)["Price"]
                .mean()
            )

            fig2 = px.bar(
                price_df,
                x="Product Name",
                y="Price",
                text_auto=".2f",
                title="Average Price Comparison",
                template="plotly_white"
            )

            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


    # =========================================================
    # 🛍️ PRODUCT SECTIONS (2 MORE CHARTS ONLY)
    # =========================================================
    def display_product_sections(self):

        st.markdown('<div class="dash-title">🛍️ Product-wise Review Analysis</div>', unsafe_allow_html=True)


        # ⭐ Chart 3 → Overall rating distribution
        st.markdown('<div class="dash-card">', unsafe_allow_html=True)

        rating_counts = self.data["Rating"].value_counts().sort_index().reset_index()
        rating_counts.columns = ["Rating", "Count"]

        fig3 = px.bar(
            rating_counts,
            x="Rating",
            y="Count",
            title="Overall Rating Distribution",
            template="plotly_white"
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


        # ⭐ Chart 4 → Review count per product
        st.markdown('<div class="dash-card">', unsafe_allow_html=True)

        count_df = (
            self.data["Product Name"]
            .value_counts()
            .reset_index()
        )
        count_df.columns = ["Product Name", "Reviews"]

        fig4 = px.bar(
            count_df,
            x="Product Name",
            y="Reviews",
            title="Reviews per Product",
            template="plotly_white"
        )

        st.plotly_chart(fig4, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
