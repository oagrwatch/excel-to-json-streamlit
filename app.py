import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel/ODS to JSON", layout="wide")

st.title("Μετατροπή Excel/ODS σε JSON")

uploaded_file = st.file_uploader("Ανέβασε το αρχείο σου (.xlsx ή .ods)", type=["xlsx", "ods"])

if uploaded_file is not None:
    try:
        # Διαβάζουμε το αρχείο με pandas
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:  # .ods
            df = pd.read_excel(uploaded_file, engine="odf")

        st.subheader("📊 Προεπισκόπηση δεδομένων")
        st.dataframe(df)

        # Μετατροπή σε JSON
        json_data = df.to_json(orient="records", force_ascii=False, indent=2)

        st.subheader("📝 JSON Output")
        st.code(json_data, language="json")

        # Δυνατότητα λήψης JSON αρχείου
        st.download_button(
            label="📥 Κατέβασε JSON",
            data=json_data,
            file_name=uploaded_file.name.rsplit(".", 1)[0] + ".json",
            mime="application/json"
        )

    except Exception as e:
        st.error(f"⚠️ Σφάλμα κατά την επεξεργασία: {e}")

