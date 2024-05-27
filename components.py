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

def load_data(data, ui_element):
    try:
        loaded_data = pd.read_csv(data)
        st.session_state['data'] = loaded_data
        ui_element = st.dataframe(loaded_data)
    except Exception as e:
        st.session_state['data'] = None
        st.error(e)
        return 
    if 'email' not in loaded_data.columns:
        st.toast("email column not found", icon="🚨")
        return
    elif 'name' not in loaded_data.columns:
        st.toast("name column not found", icon="🚨")
        return
    else:
        st.toast("Data Loaded", icon="✅")
    return

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
    if "clicked_genall" not in st.session_state:
        st.session_state.clicked_genall = False

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

    data_ui = st.empty()

    if data_button:
        load_data(uploaded_data, data_ui)

    if gen_sample or gen_all:
        if uploaded_image is None:
            st.toast("Image not loaded", icon="🚨")
        elif check_data():
            if gen_sample:
                sample_image(uploaded_image, x_cor, y_cor, font_size)
            if gen_all:
                st.session_state.clicked_genall = True
                generate_batch(uploaded_image, x_cor, y_cor, font_size)

    mail_sub = st.text_input("Mail Subject", "Insert subject here...")
    mail_body = st.text_area("Mail Body", "Insert your mail body here")
    mail_b = st.button("Send Mail", use_container_width=True)
    my_bar = st.empty()
    if mail_b and check_data():
        if not st.session_state.clicked_genall:
            st.toast("Generate All before sending the mail", icon="🚨")
        else:
            send_mail(mail_sub, mail_body, my_bar)
