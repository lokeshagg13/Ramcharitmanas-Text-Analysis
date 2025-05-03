import re
import json
import pandas as pd
import gradio as gr

from embeddings import fetch_embeddings
from semantic_matching import retrieve_semantic_matches
from hindi_transliterator import get_devanagari_suggestions

# Variables for searching
eng_word = None
eng_hindi_map = []
error_flag = False

# Variables for caching query results
max_suggestions = 10
max_pages = 10
ramayan_df = None
ramayan_db = None
current_query = None
current_padyas = None

# Function to process input text and generate suggestions
def get_suggestions(input_text, top_k=10):
    global eng_word
    words = input_text.lower().split()
    words = [word for word in words if word != '']
    if not words:
        return []
    eng_word = last_word = words[-1]
    suggestions = get_devanagari_suggestions(last_word)[:top_k]
    return suggestions

# Function to update suggestions interface
def update_suggestions_interface(input_text):
    suggestions = get_suggestions(input_text, max_suggestions)
    if len(suggestions) == 0:
        return [''] * max_suggestions + [gr.update(visible=False)]
    return suggestions + ([''] * (max_suggestions - len(suggestions))) + [gr.update(visible=True)]

# Function to handle suggestion selection
def handle_suggestion_button(selected_word):
    global eng_word, eng_hindi_map
    eng_hindi_map.append((eng_word, selected_word))
    full_text = f"{' '.join([tup[1] for tup in eng_hindi_map])}"
    return full_text

# Function to handle clear button
def handle_clear_button():
    global eng_hindi_map
    eng_hindi_map = []
    return ["", gr.update(visible=False)]

# Function to get ith search result
def get_ith_search_result(i):
    if current_padyas is None or len(current_padyas) == 0:
        return None
    i = max(0, min(i, max_pages))
    return {
        'Verse': current_padyas.loc[i, 'Verse'],
        'Meaning': current_padyas.loc[i, 'Meaning'],
        'Kand': current_padyas.loc[i, 'Kand'],
        'Verse Type': current_padyas.loc[i, 'Verse Type']
    }

# Function to handle search button
def handle_search_button(input_text):
    global current_query, current_padyas, ramayan_db, ramayan_df
    input_text = re.sub(r'[^0-9A-Za-z\u0900-\u097F\u200c\u200d]', '', input_text)
    if input_text == '':
        error_flag = True
        error_message = "Please enter a valid search text."
        return error_message
    if re.search(r'[^ \u0900-\u097F\u200c\u200d]', input_text):
        error_flag = True
        words = input_text.split()
        invalid_words = [word for word in words if word != '' and re.match(r'[^ \u0900-\u097F\u200c\u200d]', word)]
        invalid_words_str = [f"\"{word}\"" for word in invalid_words]
        error_message = f"Make sure all search text is in hindi (devanagari script)."
        if len(invalid_words_str) == 1:
            error_message += f" Invalid Word: {invalid_words_str[0]}"
        elif len(invalid_words_str) > 1 and len(invalid_words_str) <= 4:
            error_message += f" Multiple Invalid Words found including {', '.join(invalid_words_str[:-1])} and {invalid_words_str[-1]}"
        else:
            error_message += f" Multiple Invalid Words found including {', '.join(invalid_words_str[:4])}, etc."
        return error_message
    current_query = input_text
    current_padyas = retrieve_semantic_matches(
        input_text,
        max_pages,
        ramayan_db,
        ramayan_df
    )
    current_padyas = current_padyas.reset_index(drop=True)
    print('Current 1: ', current_padyas)
    padya_0 = get_ith_search_result(i)
    return [
        padya_0['Verse'], 
        padya_0['Meaning'], 
        gr.update(visible=True), 
        gr.update(interactive=False),  
        gr.update(interactive=True), 
        f"Page **1** of {max_pages}", 
        0
    ]

# Function to handle previous page button
def handle_prev_page_button(current_page_index):
    current_page_index = max(0, min(current_page_index, max_pages))
    
    prev_page_index = current_page_index - 1
    if current_page_index == 0:
        prev_page_index = max_pages
    
    padya_i = get_ith_search_result(prev_page_index)
    prev_button_interactive = True if prev_page_index != 0 else False
    next_button_interactive = True
    return [
        padya_i['Verse'], 
        padya_i['Meaning'], 
        gr.update(interactive=prev_button_interactive), 
        gr.update(interactive=next_button_interactive), 
        f"Page **{prev_page_index + 1}** of {max_pages}", 
        prev_page_index
    ]

# Function to handle next page button
def handle_next_page_button(current_page_index):
    current_page_index = max(0, min(current_page_index, max_pages))
    
    next_page_index = current_page_index + 1
    if current_page_index == max_pages - 1:
        next_page_index = 0
    
    padya_i = get_ith_search_result(next_page_index)
    prev_button_interactive = True
    next_button_interactive = True if next_page_index != (max_pages - 1) else False
    return [
        padya_i['Verse'], 
        padya_i['Meaning'], 
        gr.update(interactive=prev_button_interactive), 
        gr.update(interactive=next_button_interactive), 
        f"Page **{next_page_index + 1}** of {max_pages}", 
        next_page_index
    ]    

# Gradio app
if __name__ == '__main__':

    ramayan_df = pd.read_csv('datasets/ramcharitmanas_df.csv')
    ramayan_db = fetch_embeddings(ramayan_df)

    with gr.Blocks(theme=gr.themes.Base()) as app:

        current_page_index = gr.State(0)
        
        # Heading and Subheading
        gr.Markdown(
                    """
                    <div>
                        <div class="header"><span class="header-p1">मानस</span><span class="header-p2">वाणी</span></div>
                        <div class="subheader">रामचरितमानस के श्लोकों एवं उनके अर्थ को जानें।</div>
                    </div>
                    """,
                    elem_id="header-row"
                )
        
        # Search Row with Submit and Clear Btns
        with gr.Row(equal_height=True, elem_id="search-row"):
            with gr.Column(scale=9, elem_id="search-box"):  # 90% width for the Textbox
                input_text = gr.Textbox(
                    label="Search for Ramayana Shlokas", 
                    placeholder="Enter text (in Hinglish), e.g., Ram aur Sita ka vivah...", 
                    lines=1, 
                    elem_id="search-input"
                )
            with gr.Column(scale=1, elem_id="control-box"):  # 10% width for the Button
                with gr.Row():
                    search_btn = gr.Button(
                        value='Search', 
                        elem_id="search-button"
                    )
                    clear_btn = gr.Button(
                        value='Clear', 
                        elem_id="clear-button"
                    )
        
        # Search Suggestions
        suggestion_buttons = []
        with gr.Row(equal_height=True, elem_id="suggestion-row", visible=False) as suggestion_row:
            for i in range(max_suggestions):
                btn = gr.Button(value='', elem_id=f"btn_{i}")
                btn.click(fn=handle_suggestion_button, inputs=btn, outputs=input_text)
                suggestion_buttons.append(btn)

        # Search results
        current_page_index = gr.State(0) # State to keep track of the current index
        
        with gr.Group(elem_id="search-results-group", visible=False) as search_results_group:
            with gr.Row(elem_id="page-controls-row", equal_height=True) as page_ctrl_row:
                prev_page_btn = gr.Button(
                    value='Previous', 
                    elem_id="prev-page-button"
                )
                page_info_text = gr.Markdown(
                    value=f"Page **1** of {max_pages}", 
                    elem_id="page-info-text"
                )
                next_page_btn = gr.Button(
                    value='Next', 
                    elem_id="next-page-button"
                )

            with gr.Group(elem_id="page-text-group") as page_text_group:
                with gr.Row(elem_id="padya-text-row") as padya_text_row:
                    padya_text = gr.Markdown(
                        value=f"Sample page text", 
                        elem_id="padya-text"
                    )
                with gr.Row(elem_id="padya-meaning-row") as padya_meaning_row:
                    padya_meaning = gr.Markdown(
                        value=f"Sample meaning text", 
                        elem_id="padya-meaning"
                    )
                    
        search_btn.click(fn=handle_search_button, 
                         inputs=input_text, 
                         outputs=[padya_text, padya_meaning, search_results_group, prev_page_btn, next_page_btn, page_info_text, current_page_index])

        clear_btn.click(fn=handle_clear_button, 
                        inputs=None, 
                        outputs=[input_text, search_results_group])
                    
        input_text.change(fn=update_suggestions_interface, 
                          inputs=input_text, 
                          outputs=suggestion_buttons + [suggestion_row])

        prev_page_btn.click(fn=handle_prev_page_button, 
                         inputs=current_page_index, 
                         outputs=[padya_text, padya_meaning, prev_page_btn, next_page_btn, page_info_text, current_page_index])

        next_page_btn.click(fn=handle_next_page_button, 
                         inputs=current_page_index, 
                         outputs=[padya_text, padya_meaning, prev_page_btn, next_page_btn, page_info_text, current_page_index])


    app.css = """
        gradio-app {
            background: url("http://bharatswasthya.net/images/background.jpg") left top repeat !important;
        }

        main {
            padding: 0 !important;
            margin: 0 !important;
            max-width: none !important;
        }

        #header-row {
            background: url(http://bharatswasthya.net/images/top-background.jpg) repeat-x left top;
            padding-top: var(--size-4);
        }

        #search-row, #suggestion-row {
            padding: var(--size-2) var(--size-8);
            margin: auto;
            max-width: none;
        }
        
        .header {
            font-family: 'Noto Serif Devanagari', serif;
            font-size: 4.5rem;
            margin-left: var(--size-8);
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.5);
        }

        .header-p1 {
            color: #8da209;
        }

        .header-p2 {
            color: #59600c;
        }
        
        .subheader {
            font-family: 'Noto Serif Devanagari', sans-serif;
            font-size: 1.2rem;
            margin-left: var(--size-8);
            margin-top: 5px;
            color: #1c7d83;
        }

        #search-box > div {
            border: none;
        }

        #search-input {
            background-color: #b4d17f !important;
        }

        #search-input span {
            color: black !important;
        }

        #search-input textarea {
            background-color: white !important;
            color: black;
        }

        #search-button {
            background-color: #588157;
            border: none; 
            border-radius: 8px; 
            padding: 8px 16px; 
            cursor: pointer;
            transition: background-color 0.3s ease; 
        }

        #search-button:hover {
            background-color: #6f9c6b;
        }

        #search-button:active {
            background-color: #476b40;
        }
            
        #clear-button {
            background-color: #dad7cd;
            color: black;
            font-weight: bold; 
            border: none; 
            border-radius: 8px; 
            padding: 8px 16px; 
            cursor: pointer;
            transition: background-color 0.3s ease; 
        }
        
        #clear-button:hover {
            background-color: #c2c0a6;
        }
        
        #clear-button:active {
            background-color: #b0ad91;
        }

        #search-results-group {
            padding: var(--size-2) var(--size-8);
            margin: auto;
            background: none;
            border: none;
            margin-top: 2rem;
        }

        #search-results-group > div {
            background: none;
        }

        #prev-page-button, #next-page-button {
            background: rgb(88, 129, 87);
            max-width: fit-content;
            padding-left: 0;
            padding-right: 0;
        }

        #page-info-text {
            background: none;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        #page-info-text p, #page-info-text p strong {
            color: black;
        }
        
    """

    app.launch()
