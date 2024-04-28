import logging
from typing import Tuple

import streamlit as st
from audiorecorder import audiorecorder
from PIL import Image
from streamlit_oauth import OAuth2Component

from auth import firebase_auth
from client.OpenAIClient import OpenAIClient


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def login_view():
  st.markdown("<h1 style='text-align: center; color: #03045e '>Ecco6</h1>", unsafe_allow_html=True)
  _, col2, _ = st.columns([1,2,1])

  # Add a divider
  st.markdown("---")
  
  # Add a button
  #if st.button("Sign-in with Google"):
  #    firebase_auth.redirect_and_call_function()

  # Define the authorization URL
  authorization_url = firebase_auth.authorization_url

  # Add a button to redirect to another page
  if st.button("Sign-in with Google"):
      # Redirect to Google OAuth2 authorization URL
      st.markdown(
          f"""
          <meta http-equiv="refresh" content="0;URL={authorization_url}">
          """,
          unsafe_allow_html=True
      )
      firebase_auth.get_logged_in_user_email()


  customized_button = st.markdown("""
    <style >
    .stDownloadButton, div.stButton {text-align:center}
    .stDownloadButton button, div.stButton > button:first-child {
        background-color: #48cae4;
        color:#000000;
        border-radius: 2px;
        border: 2px solid #48cae4;                                                   
    }
        }
    </style>""", unsafe_allow_html=True)
  
  # Authentication form layout
  do_you_have_an_account = col2.selectbox(
    label='Do you have an account?',
    options=('Yes','No','I forgot my password'))
  auth_form = col2.form(key='Authentication form', clear_on_submit=False)
  email = auth_form.text_input(label='Email')
  if do_you_have_an_account in ('Yes','No'):
    password = auth_form.text_input(label='Password',type='password')
  else:
    auth_form.empty()
  auth_notification = col2.empty()

  # Sign In
  if (do_you_have_an_account == 'Yes' and
      auth_form.form_submit_button(
        label='Sign In', use_container_width=True, type='primary')):
    with auth_notification, st.spinner('Signing in'):
      firebase_auth.sign_in(email,password)

  # Create Account
  elif (do_you_have_an_account == 'No' and
        auth_form.form_submit_button(
          label='Create Account', use_container_width=True, type='primary')):
    with auth_notification, st.spinner('Creating account'):
      firebase_auth.create_account(email,password)

  # Password Reset
  elif (do_you_have_an_account == 'I forgot my password' and
        auth_form.form_submit_button(
          label='Send Password Reset Email', use_container_width=True, type='primary')):
    with auth_notification, st.spinner('Sending password reset link'):
      firebase_auth.reset_password(email)

  # Authentication success and warning messages
  if 'auth_success' in st.session_state:
    auth_notification.success(st.session_state.auth_success)
    del st.session_state.auth_success
  elif 'auth_warning' in st.session_state:
    auth_notification.warning(st.session_state.auth_warning)
    del st.session_state.auth_warning

    
  if 'email' not in st.session_state:
      st.session_state.email = None

  if not st.session_state.email:
      # User is not authenticated, attempt to log in
      email = firebase_auth.get_logged_in_user_email()
      if email:
          st.session_state.email = email
          st.experimental_rerun()

