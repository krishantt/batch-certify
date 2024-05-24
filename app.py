import streamlit as st
from components import check_password, main_ui

if not check_password():
    st.stop()

main_ui()
