# 📚 Ramcharitmanas Topic Explorer

A Streamlit app that lets you **interactively explore hidden themes** in the epic *Ramcharitmanas*, derived using **LDA Topic Modeling**. This app helps users analyze chapters, view verse clusters by topic, and gain deeper insights into the sacred text.

---

## 🚀 Features

- 🔍 **Topic-wise Exploration**: Browse verses grouped by LDA-inferred topics like *devotion*, *war*, *exile*, *philosophy*, etc.
- 📖 **Chapter (Kand) Filtering**: Optionally filter by specific chapters like बालकाण्ड, अयोध्याकाण्ड, etc.
- 🧠 **Verse + Meaning Display**: See the Awadhi verse and its Hindi translation with verse type and page info.
- 📊 **Ready for Expansion**: Plug in additional features like sentiment, keyword clouds, or question-answering.

---

## 📦 Requirements

Install dependencies (preferably in a virtual environment):

```bash
pip install streamlit pandas
```

---

## 📁 Files

| File | Description |
|------|-------------|
| `topic_explorer.py` | Main Streamlit app |
| `ramcharitmanas_topics.csv` | CSV with verse data + topic number + topic name |
| `README.md` | This documentation file |

---

## 📄 CSV Format

Your input file (`ramcharitmanas_topics.csv`) should include at least the following columns:

- `Kand`: Name of the chapter
- `Verse`: Awadhi verse
- `Meaning`: Hindi translation
- `Verse Type`: e.g., चौपाई, दोहा
- `Page Number`: Where it appears in original text
- `Verse Count`: Order of verse on page
- `Dominant_Topic`: Topic number from LDA
- `Dominant_Topic_Name`: Interpreted meaning of topic (e.g. "Devotion", "Exile")

---

## ▶️ How to Run

```bash
streamlit run topic_explorer.py
```

Then open the link shown in the terminal (usually http://localhost:8501/) in your browser.

---

## 🧠 How it Works

- Uses **LDA Topic Modeling** on the `Meaning` column to identify major themes.
- App lets you explore verses that belong to each discovered topic.
- Topics are **manually labeled** for interpretability (`Dominant_Topic_Name` column).

---

## 🙏 Credits

- Text Source: Ramcharitmanas (with Awadhi and Hindi Meaning)
- Topic Modeling: Gensim LDA
- UI Framework: Streamlit
