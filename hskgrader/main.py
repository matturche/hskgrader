import streamlit as st
from annotated_text import annotated_text
import pandas as pd
from typing import Dict

from hsk_grader_statistics import HskGraderStatistics
from helpers import (
    draw_number_of_words_per_hsk_level,
    extand_hsk_df_with_custom_df,
    get_unique_hanzi_dataframe,
    get_hsk_version_word_differences,
    load_text_files_from_dir,
)
from constants import (
    LEVEL_COLUMN_NAME,
)


if __name__ == "__main__":
    st.title("WELCOME TO HSK GRADER :snake:")

    st.subheader("What is it?")
    st.markdown(
        """
    It is a small app to analyze Chinese texts using the **Hànyǔ Shuǐpǐng
    Kǎoshì (HSK)** dictionnary entries.\n
    :red[*Note that the author(s) of this tool are not affiliated in any way
    with the Hanban/Confucius Institute Headquarters, responsible for all
    things related to the HSK.*]
        """
    )
    st.subheader("Who is it for?")
    st.markdown(
        """
    For teachers who want to evaluate the difficulty of a text that they want
    to give to their students, or for
    learners who want to start reading real world texts but are unsure if they
    are up to the task.
        """
    )

    expander = st.expander("Learn more")
    expander.write(
        """
    The test is divided into 6 main levels (or bands), with the recent addition
    of the 7 to 9th levels, in a single block. Each level reflects what is
    expected from a learner's abilities in Chinese, and they also serve as
    frameworks for learners when they study Chinese. Thus, knowing what is the
    expected HSK content in a text can be a good indicator when wanting to read
    a text.

    However, there existed no tool to my knowledge which allowed to analyse the
    content of a text and map it to an existing HSK level, which poses problem
    as a learner might want to know whether a text is accessible to them right
    now, if they will need a lot of effort to understand it, or if it's going
    to be an easy read.

    Most textbooks provide texts with a readability of around 80% (the number
    of words a learner knows), which generally makes the text challenging and
    require the learner's focus, and is pretty exhausting, having to check
    definitions at almost every sentences. On the other hand, a good text for
    extensive reading will sit at around 98% of known words, allowing the
    learner to guess from context the new words that get introduced, and is
    generally better for assimilating grammar structures, as you don't have to
    stop to check a dictionnary all the time.

    If you want to get a feeling of what it's like to read something at a given
    readability percentage, I recommend this
    [article](https://www.hackingchinese.com/introduction-extensive-reading-chinese-learners/).
    The main takeway is that 80% readability does not necessarily translate to
    80% comprehension, sometimes, it can even be closer to 0.
        """
    )

    text_tab, hsk_stats_tab = st.tabs(["Text analysis", "HSK stats"])
    with text_tab:
        # Load sample texts
        hsk_texts_folder_path = "../data/texts/"
        hsk_sample_texts: Dict[str, str] = load_text_files_from_dir(
            hsk_texts_folder_path
        )
        text_names = list(hsk_sample_texts.keys())
        text_names.sort()

        selected_text = st.selectbox(
            "You can pick a sample text to analyze",
            text_names,
            index=None,
            placeholder="No text selected",
            help="""
            All texts are from HSK2.0 **mock tests** or from the **Standard
            Course Workbooks** (edited by the Hanban)
            """,
        )

        txt = st.text_area(
            "Text to analyze:",
            "" if selected_text is None else hsk_sample_texts[selected_text],
            placeholder="Write your text here, ex: 我是法国人。",
            height=200,
            help="The textbox can be resized on the bottom right corner.",
        )
        use_word_sub_combinations = st.checkbox(
            "Use sub-words combinations in case matching fails",
            value=True,
            help="""
            e.g. given a word ABCD, it is broken down into: [ABC, AB, A, BCD,
            BC, B, CD, C, D], and we match against all of them, the final score
            corresponds to the maximum level found.
            """,
        )
        use_custom_epansion_dictionary = st.checkbox(
            "Use custom expansion dictionary",
            value=True,
            help="""
            Words that are not included in the HSK2.0 list but have been added
            because they are merely extansions of other words already learned.
            """,
        )
        chart_choice = True
        # Uncomment if desired
        # chart_choice = st.checkbox(
        #     "Draw word counts plots as bar plots",
        #     value=True,
        #     help="Otherwise as pies"
        # )
        # Loading hsk datasets, reference is copied in another variable in case
        # the df are extanded with the custom df
        hsk20_df = pd.read_csv("../data/new_hsk2-0.csv")
        hsk20_only_df = hsk20_df
        hsk20_unique_hanzi_df = get_unique_hanzi_dataframe(hsk20_only_df)
        hsk30_df = pd.read_csv("../data/new_hsk3-0.csv")
        hsk30_only_df = hsk30_df
        hsk30_unique_hanzi_df = get_unique_hanzi_dataframe(hsk30_only_df)
        hsk_word_differences_df = get_hsk_version_word_differences(
            hsk20_only_df, hsk30_only_df
        )
        hsk_hanzi_differences_df = get_hsk_version_word_differences(
            hsk20_unique_hanzi_df, hsk30_unique_hanzi_df
        )
        hsk_extansion_df = pd.read_csv(
            "../data/hsk_dict_expansion.csv"
        ).sort_values(
            by=LEVEL_COLUMN_NAME
        )
        # Uncomment if you want to read the original data, although note it
        # will break the app
        # hsk20_df = pd.read_csv("../data/hsk2-0.csv")
        # hsk30_df = pd.read_csv("../data/hsk3-0.csv")
        if use_custom_epansion_dictionary:
            hsk20_df = extand_hsk_df_with_custom_df(hsk20_df, hsk_extansion_df)
            hsk30_df = extand_hsk_df_with_custom_df(hsk30_df, hsk_extansion_df)

        hsk20_statistics = HskGraderStatistics(hsk20_df)
        hsk30_statistics = HskGraderStatistics(hsk30_df)

        if st.button("Analyze", type="primary"):

            hsk30_statistics.analyze_text(txt, use_word_sub_combinations)
            hsk20_statistics.analyze_text(txt, use_word_sub_combinations)

            readability_tab, annot_tab, word_count_tab = st.tabs(
                [
                    "Readability",
                    "Annotated text",
                    "Word counts",
                ]
            )

            with readability_tab:
                st.subheader("HSK2.0")
                hsk20_statistics.draw_readability_thresholds()
                hsk20_statistics.draw_readability_bar_plot()
                st.subheader("HSK3.0")
                hsk30_statistics.draw_readability_thresholds()
                hsk30_statistics.draw_readability_bar_plot()
            with annot_tab:
                hsk20_tab, hsk30_tab, both_tab = st.tabs(
                    [
                        "HSK2.0 annotated text",
                        "HSK3.0 annotated text",
                        "Both texts",
                    ]
                )
                with hsk20_tab:
                    annotated_text(hsk20_statistics.annotated_text)
                with hsk30_tab:
                    annotated_text(hsk30_statistics.annotated_text)
                with both_tab:
                    st.subheader("HSK2.0:")
                    annotated_text(hsk20_statistics.annotated_text)
                    st.subheader("HSK3.0:")
                    annotated_text(hsk30_statistics.annotated_text)
            with word_count_tab:
                st.subheader("HSK2.0")
                hsk20_statistics.draw_word_counts_chart(as_bars=chart_choice)
                st.subheader("HSK3.0")
                hsk30_statistics.draw_word_counts_chart(as_bars=chart_choice)
    with hsk_stats_tab:
        st.subheader("HSK2.0")
        draw_number_of_words_per_hsk_level(hsk20_only_df)
        st.divider()
        st.subheader("HSK3.0")
        draw_number_of_words_per_hsk_level(hsk30_only_df)
        st.divider()
        st.subheader("Custom vocabulary")
        draw_number_of_words_per_hsk_level(hsk_extansion_df, with_hsk7=False)
        st.divider()
        st.subheader("Reflections on word counts")
        st.write(
            """
        As we can see, the main difference between HSK2.0 and HSK3.0 is the
        number of words per level. The HSK2.0 doesn't catch up in vocabulary
        bulk up until the 6th level, which used to be the highest level
        available.

        The main issue with each band of HSK2.0 was that from HSK2 onward, the
        amount of vocabulary required doubled, marking huge spikes in later
        levels. HSK3.0 seems to solve this issue, by leveling each band to
        around 1000 vocabulary.

        By looking at numbers alone, one could think that the addition of so
        many words in early levels of HSK3.0 translates to a higher difficulty.
        While this may be true for the very beginning, when looking at the
        actual words introduced, one realise that they have added many variants
        of words already present in HSK2.0, or extended them. This makes the
        HSK3.0 a better dictionnary for raw entries, but the actual perceived
        difficulty is most probably not as great as we think between the two
        versions.

        Another thing to notice, is that out of the 5657 introduced words
        inside the HSK7-9 band, more than 1600 are already in use in HSK2.0.
        """
        )
        st.divider()
        st.subheader("Words introduced by HSK3.0 (without HSK7-9)")
        draw_number_of_words_per_hsk_level(
            pd.DataFrame(
                hsk_word_differences_df[
                    hsk_word_differences_df["Version"] == "3.0"
                ]
            ),
            with_hsk7=False,
        )
        st.divider()
        st.subheader("HSK2.0 words removed from HSK3.0")
        draw_number_of_words_per_hsk_level(
            pd.DataFrame(
                hsk_word_differences_df[
                    hsk_word_differences_df["Version"] == "2.0"
                ]
            ),
            with_hsk7=False,
        )
        st.divider()
        st.subheader(f"HSK2.0 unique hanzi list ({
                     len(hsk20_unique_hanzi_df)} hanzi)")
        st.dataframe(hsk20_unique_hanzi_df.set_index(
            LEVEL_COLUMN_NAME), width=600)
        st.divider()
        st.subheader(f"HSK3.0 unique hanzi list ({
                     len(hsk30_unique_hanzi_df)} hanzi)")
        st.dataframe(hsk30_unique_hanzi_df.set_index(
            LEVEL_COLUMN_NAME), width=600)
        st.divider()
        st.subheader(
            f"HSK3.0 and HSK2.0 unique vocabulary words ({len(
                hsk_word_differences_df)} words)"
        )
        st.dataframe(hsk_word_differences_df.set_index(
            LEVEL_COLUMN_NAME), width=600)
        st.divider()
        st.subheader(
            f"HSK3.0 and HSK2.0 unique hanzi list ({len(
                hsk_hanzi_differences_df)} hanzi)"
        )
        st.dataframe(hsk_hanzi_differences_df.set_index(
            LEVEL_COLUMN_NAME), width=600)
        st.divider()
        st.subheader("HSK2.0 vocabulary")
        st.dataframe(hsk20_only_df.set_index(LEVEL_COLUMN_NAME), width=600)
        st.subheader("HSK3.0 vocabulary")
        st.dataframe(hsk30_only_df.set_index(LEVEL_COLUMN_NAME), width=600)
        st.subheader(f"Custom vocabulary ({len(hsk_extansion_df)} words)")
        st.dataframe(hsk_extansion_df.set_index(LEVEL_COLUMN_NAME), width=600)
