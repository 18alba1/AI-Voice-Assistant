import logging

import homepage_view
import login_view
import streamlit as st

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def main():
  if 'user_info' not in st.session_state:
    login_view.login_view()
  else:
    homepage_view.homepage_view()

if __name__ == "__main__":
    main()