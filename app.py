import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="💾 Data Nest", layout='wide')
st.title("🌐 DataFlex")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization.")

# File Uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()  # Corrected file extension handling

        # Read file
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine="openpyxl")  # Ensure Excel reading works
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue  
        except Exception as e:
            st.error(f"⚠️ Error reading file {file.name}: {e}")
            continue  

        # Display file details
        st.write(f"**📂 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")

        # Preview Data (Check if DataFrame is empty)
        if df.empty:
            st.warning(f"⚠ File {file.name} is empty or unreadable.")
            continue

        st.write("🔎 **Preview of Data:**")
        st.dataframe(df.head())

        # Data Cleaning
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}", key=f"dup_{file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}", key=f"fill_{file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing Values Filled!")

        # Column Selection
        st.subheader("📌 Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            numeric_cols = df.select_dtypes(include='number')
            if not numeric_cols.empty:
                st.bar_chart(numeric_cols.iloc[:, :2])
            else:
                st.warning("⚠ No numeric data available for visualization.")

        # File Conversion
        st.subheader("📥 File Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"convert_{file.name}")

        if st.button(f"Convert {file.name}", key=f"btn_{file.name}"):
            buffer = BytesIO()
            output_file_name = os.path.splitext(file.name)[0]  # Corrected filename handling

            try:
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = output_file_name + ".csv"
                    mime_type = "text/csv"

                elif conversion_type == "Excel":
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                        writer.close()  # Ensure Excel file is saved
                    file_name = output_file_name + ".xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                # Provide download button
                st.download_button(
                    label=f"⬇ Download {file_name}",
                    data=buffer.getvalue(),
                    file_name=file_name,
                    mime=mime_type
                )
            except Exception as e:
                st.error(f"⚠️ Error in file conversion: {e}")

st.success("🎉 All files processed successfully!")
