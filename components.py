import hmac
import streamlit as st
import random
import pandas as pd
from utils import put_text, generate_batch, send_mail

@st.experimental_dialog("Sample Image")
def sample_image(image, x_corr, y_corr, fontsize):
    data = st.session_state['data']
    random_index = random.randint(0, len(data)-1)
    text = data.iloc[random_index]['name']
    gen_image = put_text(image, text, (x_corr, y_corr), fontsize)
    st.image(gen_image, use_column_width=True)

def load_data(data):
    if data is None:
        st.toast("Data not loaded", icon="🚨")
        return None
    data = pd.read_csv(data)
    st.dataframe(data)
    if 'email' not in data.columns:
        st.toast("email column not found", icon="🚨")
        data = None
    elif 'name' not in data.columns:
        st.toast("name column not found", icon="🚨")
        data = None
    else:
        st.toast("Data Loaded", icon="✅")
    return data

def check_data():
    if 'data' not in st.session_state:
        st.toast("Data not loaded", icon="🚨")
    return 'data' in st.session_state

def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

def main_ui():
    st.title("Batch Certification Mailing System")

    uploaded_image = st.file_uploader("Choose a certificate template")
    col1, col2 = st.columns([5, 1])
    with col1:
        uploaded_data = st.file_uploader("Import Data")
    with col2:
        st.container(height=35, border=False)
        data_button = st.button("Load Data")

    col1, col2 = st.columns([4, 2])
    with col1:
        with st.container(border=True):
            col11, col12, col13 = st.columns(3)
            with col11:
                x_cor = st.number_input("X: ")
            with col12:
                y_cor = st.number_input("Y: ")
            with col13:
                font_size = st.number_input("Font Size: ", min_value=1, value=100)
    with col2:
        with st.container(border=True):
            st.write("Generate Certificate")
            col11, col12 = st.columns(2)
            with col11:
                gen_sample = st.button("Sample")
            with col12:
                gen_all = st.button("All", type="primary")

    if data_button:
        if 'data' not in st.session_state:
            st.session_state['data'] = load_data(uploaded_data)

    if gen_sample or gen_all:
        if uploaded_image is None:
            st.toast("Image not loaded", icon="🚨")
        if check_data():
            if gen_sample:
                sample_image(uploaded_image, x_cor, y_cor, font_size)
            if gen_all:
                generate_batch(uploaded_image, x_cor, y_cor, font_size)

    mail_sub = st.text_input("Mail Subject", "Insert subject here...")
    mail_body = st.text_area("Mail Body", "Insert your mail body here")
    mail_b = st.button("Send Mail", use_container_width=True)
    my_bar = st.empty()
    if mail_b and check_data():
        if uploaded_image is None:
            st.toast("Image not loaded", icon="🚨")
        else:
            send_mail(mail_sub, mail_body, my_bar)
