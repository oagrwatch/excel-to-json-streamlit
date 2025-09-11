import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime

st.set_page_config(page_title="Excel/ODS σε JSON", layout="wide")

st.title("Μετατροπή Excel/ODS σε JSON")

uploaded_file = st.file_uploader(
    "📂 Ανέβασε το αρχείο σου (.xlsx ή .ods)",
    type=["xlsx", "ods"]
)

def convert_date_to_iso8601(date_value):
    """Μετατρέπει ημερομηνία από DD/MM/YYYY ή datetime object σε YYYY-MM-DD."""
    if pd.isna(date_value) or date_value == "null" or date_value == "":
        return "1970-01-01"
    try:
        # Αν είναι datetime object
        if isinstance(date_value, pd.Timestamp) or isinstance(date_value, datetime):
            return date_value.strftime("%Y-%m-%d")
        # Αν είναι string
        date_str = str(date_value).strip()
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return date_obj.strftime("%Y-%m-%d")
    except (ValueError, AttributeError) as e:
        st.warning(f"Σφάλμα μετατροπής ημερομηνίας: {date_value} - {e}")
        return "1970-01-01"

def convert_time_to_iso8601(time_value):
    """Μετατρέπει ώρα από HH:mm:ss ή datetime object σε PTnHnMnS."""
    if pd.isna(time_value) or time_value == "null" or time_value == "":
        return "PT0H0M0S"
    try:
        # Αν είναι datetime object
        if isinstance(time_value, pd.Timestamp) or isinstance(time_value, datetime):
            return f"PT{time_value.hour}H{time_value.minute}M{time_value.second}S"
        # Αν είναι string
        time_str = str(time_value).strip()
        hours, minutes, seconds = map(int, time_str.split(":"))
        return f"PT{hours}H{minutes}M{seconds}S"
    except (ValueError, AttributeError) as e:
        st.warning(f"Σφάλμα μετατροπής ώρας: {time_value} - {e}")
        return "PT0H0M0S"

def convert_timestamp_to_iso8601(timestamp_value):
    """Μετατρέπει timestamp από DD/MM/YYYY HH:mm:ss ή datetime object σε YYYY-MM-DDThh:mm:ss."""
    if pd.isna(timestamp_value) or timestamp_value == "null" or timestamp_value == "":
        return "1970-01-01T00:00:00"
    try:
        # Αν είναι datetime object
        if isinstance(timestamp_value, pd.Timestamp) or isinstance(timestamp_value, datetime):
            return timestamp_value.strftime("%Y-%m-%dT%H:%M:%S")
        # Αν είναι string
        timestamp_str = str(timestamp_value).strip()
        timestamp_obj = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
        return timestamp_obj.strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, AttributeError) as e:
        st.warning(f"Σφάλμα μετατροπής timestamp: {timestamp_value} - {e}")
        return "1970-01-01T00:00:00"

if uploaded_file is not None:
    try:
        # Progress bar
        progress_text = "⏳ Γίνεται επεξεργασία του αρχείου..."
        my_bar = st.progress(0, text=progress_text)

        time.sleep(0.5)
        my_bar.progress(30, text="📖 Διαβάζω το αρχείο...")

        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:  # .ods
            df = pd.read_excel(uploaded_file, engine="odf")

        time.sleep(0.5)
        my_bar.progress(60, text="📊 Δημιουργία προεπισκόπησης...")

        # Μετατροπή των στηλών 'created_at', 'time' και 'timestamp'
        if 'created_at' in df.columns:
            df['created_at'] = df['created_at'].apply(convert_date_to_iso8601)
        if 'time' in df.columns:
            df['time'] = df['time'].apply(convert_time_to_iso8601)
        if 'timestamp' in df.columns:
            df['timestamp'] = df['timestamp'].apply(convert_timestamp_to_iso8601)

        # Εξασφάλιση ότι οι αριθμητικές στήλες παραμένουν αριθμοί
        numeric_columns = [
            'favorite_count', 'retweet_count', 'bookmark_count',
            'quote_count', 'reply_count', 'views_count',
            'Engagement Score', 'Engagement Rate (%)'
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        st.subheader("📊 Προεπισκόπηση δεδομένων")
        st.dataframe(df)

        time.sleep(0.5)
        my_bar.progress(90, text="📝 Μετατροπή σε JSON...")

        # --- Custom JSON ---
        records = df.fillna("null").to_dict(orient="records")

        # Όλα τα values γίνονται string εκτός από τις αριθμητικές στήλες
        fixed_records = []
        for rec in records:
            new_rec = {}
            for k, v in rec.items():
                if k in numeric_columns and isinstance(v, (int, float)) and not pd.isna(v):
                    new_rec[k] = v
                else:
                    new_rec[k] = str(v)
            fixed_records.append(new_rec)

        json_data = json.dumps(fixed_records, ensure_ascii=False, indent=2)

        my_bar.progress(100, text="✅ Ολοκληρώθηκε!")

        # Δυνατότητα λήψης JSON αρχείου
        st.download_button(
            label="📥 Κατέβασε JSON",
            data=json_data,
            file_name=uploaded_file.name.rsplit(".", 1)[0] + ".json",
            mime="application/json"
        )

    except Exception as e:
        st.error(f"⚠️ Σφάλμα κατά την επεξεργασία: {e}")
