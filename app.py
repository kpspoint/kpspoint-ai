import io
import os

import streamlit as st
import google.generativeai as genai
from PIL import Image
import replicate
import qrcode
from supabase import create_client, Client


# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="kpspoint AI Studio",
    page_icon="🚀",
    layout="wide",
)


# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.5-flash-lite")

os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]


# --- Supabase Configuration ---
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)


# --- Helper Functions ---
def generate_upi_qr():
    upi_id = "shoukathali.kalathingalpalliyali@federal"
    payee_name = "KPSPOINT"
    amount = "100"
    note = "10 Credits"
    upi_link = (
        f"upi://pay?pa={upi_id}&pn={payee_name}"
        f"&am={amount}&cu=INR&tn={note}"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(upi_link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def get_user_credits(email):
    try:
        response = (
            supabase.table("users")
            .select("credits")
            .eq("email", email)
            .execute()
        )

        if response.data:
            return int(response.data[0]["credits"])

        supabase.table("users").insert(
            {"email": email, "credits": 10}
        ).execute()
        return 10

    except Exception as e:
        st.error(f"Database Error: {e}")
        return 0


def deduct_credits(email, amount):
    current_credits = get_user_credits(email)

    if current_credits < amount:
        raise ValueError("Not enough credits.")

    new_credits = current_credits - amount
    (
        supabase.table("users")
        .update({"credits": new_credits})
        .eq("email", email)
        .execute()
    )
    return new_credits


def first_replicate_output(output):
    """Return the first item from Replicate output, or None."""
    if output is None:
        return None
