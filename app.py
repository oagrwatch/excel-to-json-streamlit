import streamlit as st
import pandas as pd
import json
import time

st.set_page_config(page_title="Excel/ODS σε JSON", layout="wide")

st.title("Μετατροπή Excel/ODS σε JSON")

uploaded_file = st.file_uploader(
    "📂 Ανέβασε το αρχείο σου (.xlsx ή .ods)",
    type=["xlsx", "ods"]
)

def convert_time_to_iso8601(time_str):
    """Μετατρέπει ώρα από μορφή HH:mm:ss σε ISO 8601 duration (PTnHnMnS)."""
    if pd.isna(time_str) or time_str == "null" or time_str == "":
        return "PT0H0M0S"  # Επιστροφή προεπιλεγμένης τιμής για κενές ή μη έγκυρες τιμές
    try:
        # Υποθέτουμε ότι η ώρα είναι σε μορφή HH:mm:ss
        hours, minutes, seconds = map(int, time_str.split(":"))
        return f"PT{hours}H{minutes}M{seconds}S"
    except (ValueError, AttributeError):
        return "PT0H0M0S"  # Επιστροφή προεπιλεγμένης τιμής σε περίπτωση σφάλματος

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

        # Μετατροπή της στήλης 'time' σε μορφή ISO 8601
        if 'time' in df.columns:
            df['time'] = df['time'].apply(convert_time_to_iso8601)

        st.subheader("📊 Προεπισκόπηση δεδομένων")
        st.dataframe(df)

        time.sleep(0.5)
        my_bar.progress(90, text="📝 Μετατροπή σε JSON...")

        # --- Custom JSON ---
        records = df.fillna("null").to_dict(orient="records")

        # Όλα τα values γίνονται string εκτός από αριθμούς
        fixed_records = []
        for rec in records:
            new_rec = {}
            for k, v in rec.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
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
