import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Excel/ODS σε JSON", layout="wide")

st.title("Μετατροπή Excel/ODS σε JSON")

uploaded_file = st.file_uploader(
    "📂 Ανέβασε το αρχείο σου (.xlsx ή .ods)",
    type=["xlsx", "ods"]
)

if uploaded_file is not None:
    try:
        # Progress bar
        progress_text = "⏳ Γίνεται επεξεργασία του αρχείου..."
        my_bar = st.progress(0, text=progress_text)

        # Βήμα 1: Ανάγνωση αρχείου
        time.sleep(0.5)
        my_bar.progress(30, text="📖 Διαβάζω το αρχείο...")

        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:  # .ods
            df = pd.read_excel(uploaded_file, engine="odf")

        # Βήμα 2: Εμφάνιση δεδομένων
        time.sleep(0.5)
        my_bar.progress(60, text="📊 Δημιουργία προεπισκόπησης...")

        st.subheader("📊 Προεπισκόπηση δεδομένων")
        st.dataframe(df)

        # Βήμα 3: Μετατροπή σε JSON
        time.sleep(0.5)
        my_bar.progress(90, text="📝 Μετατροπή σε JSON...")

        json_data = df.to_json(orient="records", force_ascii=False, indent=2)

        # Βήμα 4: Έτοιμο
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

