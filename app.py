# FeedBack analyser


# import
import streamlit as st
import time
import pandas as pd
import plotly.express as px
import re


# Step -1: Page_setup with CSS
st.set_page_config(
    page_title="MyFeeds@ZOMATO.com",
    page_icon=":postbox:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Zomato Feedback Analysis Tool"
    }
)


st.title(":red[Zomato|]Feeds :pizza:")


# Injecting Custom CSS
st.markdown('''
            <style>  
                .stApp {
                    background-color: ivory;
                    color: #2e7d32;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                h3 { color: #d32f2f; margin-bottom: 5px; }
                h6 { color: #555; margin-top: 5px; }
                .price-tag {
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                    background-color: #d32f2f;
                    padding: 5px 15px;
                    border-radius: 20px;
                    display: inline-block;
                }
                .features span {
                    background-color: #f1f1f1;
                    padding: 2px 8px;
                    border-radius: 5px;
                    margin-right: 5px;
                    font-size: 12px;
                    color: #333;
                }
                img {
                    border-radius: 15px;
                    width: 100%;
                    height: 180px;
                    object-fit: cover;
                }
                .review-box {
                    border-left: 5px solid;
                    padding: 10px;
                    margin: 5px 0;
                    background-color: #f9f9f9;
                    border-radius: 5px;
                }
            </style>
            ''', unsafe_allow_html=True)


# Step -2: Data Initialization and Sentiment Engine
if 'db' not in st.session_state:
    st.session_state.db = []


if 'p' not in st.session_state:
    st.session_state.p = {
        "Pizza": {
            "ts": 5.0, "c": 1, "type": "Breads", "price": 549.54, "vnv": "Veg/Non-Veg", "data": "Cheese, Mushroom, Chicken",
            "icon": "https://www.schwartz.co.uk/-/media/project/oneweb/schwartz/recipes/recipe_image_update/march_18_2025/easy_pizza_recipe_800x800.webp"
        },
        "Burger": {
            "ts": 4.0, "c": 1, "type": "Breads", "price": 349.54, "vnv": "Veg/Non-Veg", "data": "Cheese, Onion, Patty",
            "icon": "https://www.burgerdudes.se/wp-content/uploads/2025/06/crispy-chicken-burger-by-burgerdudes.jpg"
        },
        "French fries": {
            "ts": 2.0, "c": 1, "type": "Snacks", "price": 249.54, "vnv": "Veg", "data": "Salted, Roasted",
            "icon": "https://kirbiecravings.com/wp-content/uploads/2019/09/easy-french-fries-1.jpg"
        },
        "Nuggets": {
            "ts": 5.0, "c": 1, "type": "Snacks", "price": 149.54, "vnv": "Veg/Non-Veg", "data": "Crispy Chicken/Veg",
            "icon": "https://www.acozykitchen.com/wp-content/uploads/2025/12/HomemadeChickenNuggets-06.jpg"
        },
        "Biryanis": {
            "ts": 3.8, "c": 1, "type": "Main Course", "price": 449.54, "vnv": "Veg/Non-Veg", "data": "Spiced Rice, Meat",
            "icon": "https://www.cookwithmanali.com/wp-content/uploads/2019/09/Vegetable-Biryani-Restaurant-Style.jpg"
        }
    }


def analyse(t):
    t = t.lower()
    p_words = ["delicious", "good", "wonderful", "happy", "best", "tasty", "love"]
    n_words = ["bad", "worst", "bitter", "salty", "regret", "slow", "cold", "disappointing"]
    p = sum(t.count(w) for w in p_words)
    n = sum(t.count(w) for w in n_words)
    if p > n: return "Positive☺️", "#2E7D32"
    elif n > p: return "Negative🥲", "#D32F2F"
    else: return "Neutral🫠", "#FFA000"


# Step -3: Sidebar Navigation
option = st.sidebar.radio("Navigation", ["Feedback", "Analytics"])


if option == "Feedback":
    st.subheader("Explore Our Menu")
    cols = st.columns(5)
   
    for i, (name, info) in enumerate(st.session_state.p.items()):
        with cols[i]:
            avg = round(info['ts'] / info['c'])
            st.markdown(f'''
                <div class="Product_items">
                    <img src="{info['icon']}" style="border-radius: 15px; width: 100%; height: 180px; object-fit: cover;">
                    <h3>{name}</h3>
                    <p>{"🌟" * int(avg)}</p>
                    <div class="features">
                        <span>{info['vnv']}</span>
                        <span>{info['type']}</span>
                    </div>
                    <h6>{info['data']}</h6>
                    <div class="price-tag">₹{info['price']}</div>
                </div>
            ''', unsafe_allow_html=True)
           
            with st.expander("View Reviews"):
                product_reviews = [r for r in st.session_state.db if r['prod'] == name]
                if product_reviews:
                    for r in product_reviews:
                        st.markdown(f'''
                            <div class="review-box" style="border-color: {r['color']}; background-color: {r['color']}20;">
                                <small><b>{r['email']}</b> <br> ({r['sent']})</small>
                                <small>{"⭐" * r['rating']}</small> <br>
                                <b><i>"{r['txt']}"</i></b>
                            </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.caption("No reviews yet.")


    st.divider()
    st.subheader("Share Your Experience")
    c1, c2 = st.columns(2)
    with c1:
        em = st.text_input("Email Address:")
        pr = st.selectbox("Which item did you try?", ["--select--"] + list(st.session_state.p.keys()))
        sr = st.select_slider("Rate the Item", options=[1, 2, 3, 4, 5], value=3)
    with c2:
        tx = st.text_area("Write your feedback here:", height=150)
        if st.button("Submit Review", use_container_width=True):
                if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", em):
                    st.error("Please enter a valid email address.")
                elif pr == "--select--":
                    st.error("Please select a dish to submit your review.")
                elif any(r for r in st.session_state.db if r['email'] == em and r['prod'] == pr):
                    st.warning("You have already submitted a review for this item.")
                elif tx:
                    st.session_state.p[pr]['ts'] += sr
                    st.session_state.p[pr]['c'] += 1
                    st.session_state.db.append({"email":em,
                                                "prod":pr,
                                                "txt":tx,
                                                "rating":sr,
                                                "sent":analyse(tx)[0],
                                                "color":analyse(tx)[1],
                                                "time":time.time()})
                    time.sleep(2)
                    st.success("Thank you for your feedback!")
                    st.rerun()


# Step -4: Analytics Section
elif option == "Analytics":
    st.subheader("Performance Insights")
    if not st.session_state.db:
        st.info("No reviews submitted yet. Please share your feedback in the Feedback section.")
    else:
        df = pd.DataFrame(st.session_state.db)
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.histogram(df, x="prod", color="sent", title="Sentiment Distribution by Item",
                                category_orders={"sent": ["Positive☺️", "Neutral🫠", "Negative🥲"]})
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig1 = px.area(df.groupby("prod")["rating"].mean().reset_index(), x="prod", y="rating", title="Average Rating by Item")
            st.plotly_chart(fig1, use_container_width=True)


        df = df.sort_values("time", ascending=True)
        st.subheader("| Recent Reviews")
        for _, row in df.iterrows():
            st.markdown(f'''
                <div class="review-box" style="border-color: {row['color']}20; background-color: {row['color']}20;">
                    <small><b>{row['email']}</b> <br> ({row['sent']})</small>
                    <small>{"⭐" * row['rating']}</small> <br>                  
                    <b><i>"{row['txt']}"</i></b>
                    <div style="text-align: right; font-size: 10px; color: #777;">{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row['time']))}</div>
                </div>
            ''', unsafe_allow_html=True)


