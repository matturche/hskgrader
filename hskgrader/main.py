import streamlit as st
from annotated_text import annotated_text
import pandas as pd
from requests.compat import urljoin
import argparse
from typing import Dict

from hsk_grader_statistics import HskGraderStatistics
from helpers import (
    draw_number_of_words_per_hsk_level,
    extand_hsk_df_with_custom_df,
    get_unique_hanzi_dataframe,
    get_hsk_version_word_differences,
    load_github_dataframe,
    load_github_text_files,
    load_text_files_from_dir,
    text_contains_hanzi,
)
from constants import (
    BASE_GITHUB_PATH,
    LEVEL_COLUMN_NAME,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--local",
        default=False,
        action="store_true",
        help="Running localy, defaults to False",
    )
    args = parser.parse_args()

    st.set_page_config(
        page_title="HSK Grader",
        page_icon=":dragon_face:",
    )

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

    text_tab, interpet_tab, hsk_stats_tab, vocab_lists_tab = st.tabs([
        "Text analysis",
        "How to interpret results",
        "HSK stats",
        "Vocabulary lists",
    ])
    with text_tab:
        if args.local:
            local_data_path = "../data/"
            # Load sample texts
            hsk_texts_folder_path = f"{local_data_path}texts/"
            hsk_sample_texts: Dict[str, str] = load_text_files_from_dir(
                hsk_texts_folder_path
            )
            text_names = list(hsk_sample_texts.keys())
            text_names.sort()

            # Loading hsk datasets, reference is copied in another variable in
            # case the df are extanded with the custom df
            hsk20_df = pd.read_csv(f"{local_data_path}new_hsk2-0.csv")
            hsk30_df = pd.read_csv(f"{local_data_path}new_hsk3-0.csv")
            # Uncomment if you want to read the original data, although note it
            # will break the app
            # hsk20_df = pd.read_csv("../data/hsk2-0.csv")
            # hsk30_df = pd.read_csv("../data/hsk3-0.csv")
            hsk_extansion_df = pd.read_csv(
                f"{local_data_path}hsk_dict_expansion.csv"
            ).sort_values(
                by=LEVEL_COLUMN_NAME
            )
        # Load datasets from the github repository
        else:
            # Load sample texts
            hsk_sample_texts: Dict[str, str] = load_github_text_files()
            text_names = list(
                hsk_sample_texts.keys()
            ) if hsk_sample_texts is not None else []
            text_names.sort()
            hsk20_df = load_github_dataframe(
                urljoin(BASE_GITHUB_PATH, "new_hsk2-0.csv")
            )
            hsk30_df = load_github_dataframe(
                urljoin(BASE_GITHUB_PATH, "new_hsk3-0.csv")
            )
            hsk_extansion_df = load_github_dataframe(
                urljoin(BASE_GITHUB_PATH, "hsk_dict_expansion.csv")
            ).sort_values(
                by=LEVEL_COLUMN_NAME
            )

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
        selected_text = "" if selected_text is None else hsk_sample_texts[
            selected_text
        ]
        hsk20_only_df = hsk20_df
        hsk20_unique_hanzi_df = get_unique_hanzi_dataframe(hsk20_only_df)
        hsk30_only_df = hsk30_df
        hsk30_unique_hanzi_df = get_unique_hanzi_dataframe(hsk30_only_df)
        hsk_word_differences_df = get_hsk_version_word_differences(
            hsk20_only_df, hsk30_only_df
        )
        hsk_hanzi_differences_df = get_hsk_version_word_differences(
            hsk20_unique_hanzi_df, hsk30_unique_hanzi_df
        )

        txt = st.text_area(
            "Text to analyze:",
            selected_text,
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

        if use_custom_epansion_dictionary:
            hsk20_df = extand_hsk_df_with_custom_df(hsk20_df, hsk_extansion_df)
            hsk30_df = extand_hsk_df_with_custom_df(hsk30_df, hsk_extansion_df)

        hsk20_statistics = HskGraderStatistics(hsk20_df)
        hsk30_statistics = HskGraderStatistics(hsk30_df)

        if st.button("Analyze", type="primary"):
            if text_contains_hanzi(txt):
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
                    st.subheader(
                        f"HSK2.0 ({hsk20_statistics.total_words} words)")
                    hsk20_statistics.draw_word_counts_chart(
                        as_bars=chart_choice)
                    st.subheader(
                        f"HSK3.0 ({hsk30_statistics.total_words} words)")
                    hsk30_statistics.draw_word_counts_chart(
                        as_bars=chart_choice)
            else:
                st.error(
                    """
                    Your text doesn't contain any hanzi, there is nothing to
                    analyze.
                    """
                )
    with interpet_tab:
        st.subheader("How to interpret readability?")
        st.markdown(
            """
            HSK Grader's main objective is to give HSK levels at which a text
            is most likely readable. When giving a HSK level for a given
            readability threshold, it means that if you passed, or studied all
            the vocabulary for this level, then you should be able to read the
            text with this threshold.

            For example, if the text is graded as having a readability of 80%
            at HSK5, you need to have mastered HSK5 content.
            """
        )
        st.subheader("What are 'intensive' and 'extensive' reading?")
        st.markdown(
            """
            Intensive reading sits at around 80% readability, and is generally
            what you would expect from texts at a learner's level that they
            would study in class. These texts are usually accompanied by a
            vocabulary list so that learners can read the text without too much
            trouble.

            If a learner were to read a text like this outside of textbook, it
            means they will probably be fine but will have to check every now
            and then a dictionary and may find it exhausting after a short
            period.

            This is why extensive reading is recommended for leisure reading,
            it sits at the right balance between known and unknown words. It
            allows learners to be able to guess from context some words'
            meaning without having to check a dictionary, although in Chinese
            it is a little different, as when you don't recognize a hanzi you
            still have to check it in a dictionary either way.
            """
        )
        st.subheader(
            """
            The app is showing 80/95/98% readability at a level higher than I should be but I can still read the text fine, why?
            """
        )
        st.markdown(
            """
            Between theoretical readability and actual readability
            exists a difference, specific to every individual. The grade
            given here is conservative, because there might be some undetected
            words, and it also takes HSK levels at face value. But in reality,
            the vocabulary people learn is influenced by factors outside of
            just HSK levels, including but not limited to: nationality, center
            of interests, exposure to the language, specific needs...

            Sometimes, a text might have few complicated words, but appearing
            often, raising the difficulty of the text only on a surface level.

            Thus the difference between 80%, 95% and 98% might be more blurry
            if you are already familiar with the text's context, or have
            already studied its topic previously.
            """
        )
        st.subheader(
            """
            The app is showing 80/95/98% readability at HSK7-9 but the actual score is lower, why?
            """
        )
        st.markdown(
            """
            HSK7-9 is the default maximum rating for each thresholds, because
            if you got to HSK7-9, then you should have no problem whatsoever
            in reading most texts. We could say that most of them
            have a readability of 100% at this level.

            The reason as to why it is not true with the app grading is simply
            because HSK entries are limited, and do not reflect completely the
            actual number of words one can read when reaching given levels,
            this is why HSK Grader is using a custom dictionnary. As it is
            expanded, the accuracy of grading will improve.
            """
        )
    with hsk_stats_tab:
        st.subheader("HSK2.0")
        draw_number_of_words_per_hsk_level(hsk20_only_df)
        st.divider()
        st.subheader("HSK3.0")
        draw_number_of_words_per_hsk_level(hsk30_only_df)
        st.divider()
        st.subheader(f"Custom vocabulary ({len(hsk_extansion_df)} words)")
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
        st.subheader("HSK2.0 unique hanzi by level")
        draw_number_of_words_per_hsk_level(
            hsk20_unique_hanzi_df,
            with_hsk7=False,
        )
        st.divider()
        st.subheader("HSK3.0 unique hanzi by level")
        draw_number_of_words_per_hsk_level(
            hsk30_unique_hanzi_df,
            with_hsk7=False,
        )
        st.subheader("Reflections on unique hanzi in HSK")
        st.markdown(
            """
            One of the biggest issue with HSK2.0 is that in early levels,
            despite a low word count, it introduced many hanzi. This is
            especially visible on HSK1 where 174 unique hanzi are
            introduced for only 150 words! This is very detrimental for
            a learner's understanding on how hanzi, and the Chinese
            writing system actually works. And as levels increase, more
            and more are introduced.

            This is something that the team behind the HSK must have
            acknowledged, because as we can see the distribution of new
            hanzi is completely different in HSK3.0. Every band until the
            last introduces exactly 300 unique hanzi and uses them to build
            its vocabulary bulk. This is a very good improvement, as it means
            learners can leverage more vocabulary using less hanzi: three times
            over the number of hanzi they have to learn at HSK5.

            However, this has for effect that while learners from HSK2.0 and
            HSK3.0 roughly have around the same number of hanzi at their
            disposal at HSK5, it is completely different at HSK6. HSK2.0 and
            HSK3.0 have a difference of more than 860 hanzi, in favor of
            HSK2.0. This difference accounts for the straight removal of 414
            words from HSK3.0 in HSK6 and the displacement of 1600 entries
            from inferior levels to HSK7-9.

            From a pure word count point of view, it would seem that while
            HSK2.0 and HSK3.0 HSK6 levels get you to the same amount of
            vocabulary, but when looking at individual hanzi introduced, it
            seems that HSK2.0's HSK6 band is much more advanced than its HSK3.0
            counterpart.
            """
        )
    with vocab_lists_tab:
        st.subheader("HSK2.0 vocabulary")
        st.dataframe(hsk20_only_df.set_index(LEVEL_COLUMN_NAME), width=600)
        st.subheader("HSK3.0 vocabulary")
        st.dataframe(hsk30_only_df.set_index(LEVEL_COLUMN_NAME), width=600)
        st.subheader(f"Custom vocabulary ({len(hsk_extansion_df)} words)")
        st.dataframe(hsk_extansion_df.set_index(LEVEL_COLUMN_NAME), width=600)
        st.divider()
        st.subheader(f"HSK2.0 unique hanzi list ({
                     len(hsk20_unique_hanzi_df)} hanzi)")
        st.dataframe(hsk20_unique_hanzi_df.set_index(
            LEVEL_COLUMN_NAME), width=600)
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
        st.subheader(
            f"HSK3.0 and HSK2.0 unique hanzi list ({len(
                hsk_hanzi_differences_df)} hanzi)"
        )
        st.dataframe(hsk_hanzi_differences_df.set_index(
            LEVEL_COLUMN_NAME), width=600)
