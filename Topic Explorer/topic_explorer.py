import streamlit as st
import pandas as pd

# Load data
df = pd.read_csv('ramcharitmanas_topics.csv')  # Your saved DataFrame with 'Dominant_Topic'

st.title("📚 Ramcharitmanas Topic Explorer")
st.markdown("Explore the hidden themes (topics) found using LDA Topic Modeling.")

df['Dominant_Topic_Display_Name'] = df['Dominant_Topic'].astype(str) + ': ' + df['Dominant_Topic_Name']
# Sidebar filter
topic = st.sidebar.selectbox("Choose Topic", [topic.split(': ')[1] for topic in sorted(df['Dominant_Topic_Display_Name'].unique(), key=lambda x: int(x.split(': ')[0]))])
kand_filter = st.sidebar.multiselect("Filter by Kand (optional)", df['Kand'].unique())

# Filtered Data
filtered_df = df[df['Dominant_Topic_Name'] == topic]
if kand_filter:
    filtered_df = filtered_df[filtered_df['Kand'].isin(kand_filter)]

st.markdown(f"### Showing {len(filtered_df)} verses for **Topic {topic}**")
for _, row in filtered_df.iterrows():
    st.markdown("---")
    st.markdown(f"""
        #### 📖 {row['Kand']}
        - **Verse Type**: {row['Verse Type']}
        - **Page**: {row['Page Number']}
        - **Verse Count**: {row['Verse Count']}
    """)
    
    st.markdown(f"> 🕉️ *{row['Verse']}*")

    st.markdown(f"**🗣️ Meaning**: {row['Meaning']}")

