# ==============================
# ZOMATO FEEDBACK ANALYSER
# ==============================

import streamlit as st
import time
import pandas as pd
import plotly.express as px
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MyFeeds@ZOMATO.com",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🍕 Zomato Feeds")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color: ivory;
    font-family: 'Segoe UI', sans-serif;
}
.review-box {
    border-left: 5px solid;
    padding: 10px;
    margin: 5px 0;
    border-radius: 5px;
    background-color: #f9f9f9;
}
img {
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "reviews" not in st.session_state:
    st.session_state.reviews = []

if "products" not in st.session_state:
    st.session_state.products = {
        "Pizza": {
            "total_score": 5,
            "count": 1,
            "type": "Breads",
            "price": 549.54,
            "category": "Veg/Non-Veg",
            "ingredients": "Cheese, Mushroom, Chicken",
            "image": "https://www.schwartz.co.uk/-/media/project/oneweb/schwartz/recipes/recipe_image_update/march_18_2025/easy_pizza_recipe_800x800.webp"
        },
        "Burger": {
            "total_score": 4,
            "count": 1,
            "type": "Breads",
            "price": 349.54,
            "category": "Veg/Non-Veg",
            "ingredients": "Cheese, Onion, Patty",
            "image": "https://www.burgerdudes.se/wp-content/uploads/2025/06/crispy-chicken-burger-by-burgerdudes.jpg"
        },
        "French Fries": {
            "total_score": 2,
            "count": 1,
            "type": "Snacks",
            "price": 249.54,
            "category": "Veg",
            "ingredients": "Salted, Roasted",
            "image": "https://kirbiecravings.com/wp-content/uploads/2019/09/easy-french-fries-1.jpg"
        },
        "Nuggets": {
            "total_score": 5,
            "count": 1,
            "type": "Snacks",
            "price": 149.54,
            "category": "Veg/Non-Veg",
            "ingredients": "Crispy Chicken/Veg",
            "image": "https://www.acozykitchen.com/wp-content/uploads/2025/12/HomemadeChickenNuggets-06.jpg"
        },
        "Biryanis": {
            "total_score": 3.8,
            "count": 1,
            "type": "Main Course",
            "price": 449.54,
            "category": "Veg/Non-Veg",
            "ingredients": "Spiced Rice, Meat",
            "image": "https://www.cookwithmanali.com/wp-content/uploads/2019/09/Vegetable-Biryani-Restaurant-Style.jpg"
        }
    }

# ---------------- SENTIMENT FUNCTION ----------------
def analyze_sentiment(text):
    text = text.lower()

    positive_words = ["delicious", "good", "wonderful", "happy", "best", "tasty", "love"]
    negative_words = ["bad", "worst", "bitter", "salty", "regret", "slow", "cold", "disappointing"]

    positive_score = sum(text.count(word) for word in positive_words)
    negative_score = sum(text.count(word) for word in negative_words)

    if positive_score > negative_score:
        return "Positive 😊", "#2E7D32"
    elif negative_score > positive_score:
        return "Negative 😢", "#D32F2F"
    else:
        return "Neutral 😐", "#FFA000"

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation", ["Feedback", "Analytics"])

# ==================================================
# ================= FEEDBACK PAGE ==================
# ==================================================
if menu == "Feedback":

    st.subheader("Explore Our Menu")
    columns = st.columns(len(st.session_state.products))

    for i, (name, details) in enumerate(st.session_state.products.items()):
        with columns[i]:

            avg_rating = round(details["total_score"] / details["count"], 1)

            st.image(details["image"])
            st.markdown(f"### {name}")
            st.write("⭐" * int(round(avg_rating)))
            st.write(f"**{details['category']} | {details['type']}**")
            st.write(details["ingredients"])
            st.markdown(f"### ₹{details['price']}")

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
    st.subheader("Share Your Experience")

    col1, col2 = st.columns(2)

    with col1:
        email = st.text_input("Email Address")
        selected_product = st.selectbox("Select Item", ["--Select--"] + list(st.session_state.products.keys()))
        rating = st.slider("Rating", 1, 5, 3)

    with col2:
        feedback_text = st.text_area("Write your feedback here", height=150)

        if st.button("Submit Review", use_container_width=True):

            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                st.error("Please enter valid email")

            elif selected_product == "--Select--":
                st.error("Please select a product")

            elif any(r for r in st.session_state.reviews if r["email"] == email and r["product"] == selected_product):
                st.warning("You already reviewed this product")

            elif feedback_text:

                sentiment, color = analyze_sentiment(feedback_text)

                st.session_state.products[selected_product]["total_score"] += rating
                st.session_state.products[selected_product]["count"] += 1

                st.session_state.reviews.append({
                    "email": email,
                    "product": selected_product,
                    "text": feedback_text,
                    "rating": rating,
                    "sentiment": sentiment,
                    "color": color,
                    "time": time.time()
                })

                st.success("Review submitted successfully!")
                st.rerun()

# ==================================================
# ================= ANALYTICS PAGE =================
# ==================================================
elif menu == "Analytics":

    st.subheader("Performance Insights")

    if not st.session_state.reviews:
        st.info("No reviews submitted yet.")
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
            fig2 = px.area(avg_df, x="product", y="rating", title="Average Rating by Product")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Recent Reviews")

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
