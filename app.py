# ==============================
# ZOMATO FEEDBACK ANALYSER
# ==============================

import streamlit as st
import pandas as pd
import plotly.express as px
import time
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Zomato Feedback Analyzer",
    page_icon="🍕",
    layout="wide"
)

st.title("🍕 Zomato Feedback Analyzer")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color: #fffaf0;
    font-family: Arial, sans-serif;
}
.review-box {
    border-left: 5px solid;
    padding: 10px;
    margin: 8px 0;
    border-radius: 5px;
    background-color: #f9f9f9;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "reviews" not in st.session_state:
    st.session_state.reviews = []

if "products" not in st.session_state:
    st.session_state.products = {
        "Pizza": {"total": 5, "count": 1, "price": 549.54},
        "Burger": {"total": 4, "count": 1, "price": 349.54},
        "French Fries": {"total": 2, "count": 1, "price": 249.54},
        "Nuggets": {"total": 5, "count": 1, "price": 149.54},
        "Biryanis": {"total": 4, "count": 1, "price": 449.54},
    }

# ---------------- SENTIMENT FUNCTION ----------------
def analyze(text):
    text = text.lower()

    positive = ["good", "best", "tasty", "love", "excellent", "amazing"]
    negative = ["bad", "worst", "cold", "slow", "disappointing"]

    p_score = sum(text.count(word) for word in positive)
    n_score = sum(text.count(word) for word in negative)

    if p_score > n_score:
        return "Positive 😊", "#2E7D32"
    elif n_score > p_score:
        return "Negative 😢", "#D32F2F"
    else:
        return "Neutral 😐", "#FFA000"

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation", ["Feedback", "Analytics"])

# ==================================================
# ================= FEEDBACK PAGE ==================
# ==================================================
if menu == "Feedback":

    st.subheader("🍽️ Menu")

    cols = st.columns(len(st.session_state.products))

    for i, (name, info) in enumerate(st.session_state.products.items()):
        with cols[i]:
            avg_rating = round(info["total"] / info["count"], 1)

            st.markdown(f"### {name}")
            st.write("⭐" * int(round(avg_rating)))
            st.write(f"Price: ₹{info['price']}")

            with st.expander("View Reviews"):
                product_reviews = [r for r in st.session_state.reviews if r["product"] == name]
                if product_reviews:
                    for r in product_reviews:
                        st.markdown(f"""
                        <div class="review-box" style="border-color:{r['color']};">
                        <b>{r['email']}</b> ({r['sentiment']})<br>
                        {"⭐"*r['rating']}<br>
                        "{r['text']}"
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No reviews yet.")

    st.divider()
    st.subheader("✍️ Share Your Feedback")

    col1, col2 = st.columns(2)

    with col1:
        email = st.text_input("Email")
        product = st.selectbox("Select Product", ["--Select--"] + list(st.session_state.products.keys()))
        rating = st.slider("Rating", 1, 5, 3)

    with col2:
        feedback = st.text_area("Write Review", height=150)

        if st.button("Submit Review", use_container_width=True):

            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                st.error("Enter valid email")

            elif product == "--Select--":
                st.error("Select product")

            elif any(r for r in st.session_state.reviews if r["email"] == email and r["product"] == product):
                st.warning("You already reviewed this product")

            elif feedback.strip() == "":
                st.error("Write something in review")

            else:
                sentiment, color = analyze(feedback)

                st.session_state.products[product]["total"] += rating
                st.session_state.products[product]["count"] += 1

                st.session_state.reviews.append({
                    "email": email,
                    "product": product,
                    "rating": rating,
                    "text": feedback,
                    "sentiment": sentiment,
                    "color": color,
                    "time": time.time()
                })

                st.success("Review Submitted Successfully!")
                st.rerun()

# ==================================================
# ================= ANALYTICS PAGE =================
# ==================================================
elif menu == "Analytics":

    st.subheader("📊 Analytics Dashboard")

    if not st.session_state.reviews:
        st.info("No reviews available yet.")
    else:
        df = pd.DataFrame(st.session_state.reviews)

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.histogram(
                df,
                x="product",
                color="sentiment",
                title="Sentiment Distribution"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            avg_df = df.groupby("product")["rating"].mean().reset_index()
            fig2 = px.bar(
                avg_df,
                x="product",
                y="rating",
                title="Average Rating"
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("🕒 Recent Reviews")

        df = df.sort_values("time", ascending=False)

        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="review-box" style="border-color:{row['color']};">
            <b>{row['email']}</b> ({row['sentiment']})<br>
            {"⭐"*row['rating']}<br>
            "{row['text']}"<br>
            <small>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row['time']))}</small>
            </div>
            """, unsafe_allow_html=True)
