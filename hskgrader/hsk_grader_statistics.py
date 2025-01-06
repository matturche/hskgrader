import streamlit as st
import numpy as np
import pandas as pd
import jieba
import matplotlib.pyplot as plt
from typing import Dict, Generator, List, Tuple, Union

from constants import (
    HSK_DEFAULT_COLORS,
    HSK_LABELS,
    LEVEL_COLUMN_NAME,
    PLT_HSK_COLORS,
    SIMPLIFIED_WORD_COLUMN_NAME,
)

from helpers import (
    character_is_hanzi,
    get_hanzi_sub_combinations,
)


class HskGraderStatistics:

    def __init__(self, hsk_df: pd.DataFrame) -> None:
        self.text: str
        self.hsk_df: pd.DataFrame = hsk_df
        self.seg_text: Generator[str]
        self.words_with_level: List[Tuple[str, int]] = []
        self.annotated_text: List[Union[Tuple[str, str, str], str]] = []
        self.total_words: int = 0
        self.readability_eighty: int = 0
        self.readability_ninety_five: int = 0
        self.readability_ninety_eight: int = 0
        # The 0 entry is for unkown words
        self.hsk_word_counts: Dict[int, int] = {i: 0 for i in range(8)}
        self.additive_hsk_word_counts: Dict[int, int] = {
            i: 0 for i in range(1, 8)}
        self.hsk_readability: Dict[int, float] = {i: 0.0 for i in range(1, 8)}

    def draw_readability_thresholds(self):
        readability_columns = st.columns(3)
        readability_text = "Readability: HSK"
        readability_columns[0].markdown(
            f"### :orange[80%] {readability_text}{
                self.readability_eighty} ({
                self.hsk_readability[self.readability_eighty]
            }%)"
        )
        readability_columns[1].markdown(
            f"### :green[95%] {readability_text}{
                self.readability_ninety_five
            } ({
                self.hsk_readability[self.readability_ninety_five]}%)"
        )
        readability_columns[2].markdown(
            f"### :blue[98%] {readability_text}{
                self.readability_ninety_eight
            } ({
                self.hsk_readability[self.readability_ninety_eight]}%)"
        )
        st.caption(
            """Note that **Intensive Reading** starts at 80%,
            and that **Extensive Reading** starts at 95-98%"""
        )

    def draw_readability_bar_plot(self):
        fig1, ax1 = plt.subplots()
        readabilities = [val * 100 for val in self.hsk_readability.values()]
        ax1.bar(
            HSK_LABELS[1:],
            readabilities,
            color=PLT_HSK_COLORS[1:],
        )
        ticks = [i for i in range(0, 91, 10)]
        ticks.extend([95, 98])
        ax1.set_ylabel("readability (%)")
        ax1.set_xlabel("HSK level")
        ax1.set_yticks(ticks)
        ax1.set_ylim(0, 100)
        plt.grid(axis="y", color="gainsboro")
        st.pyplot(fig1)

    def draw_word_counts_chart(self, as_bars: bool = True):
        def func(pct, allvals):
            absolute = int(np.round(pct / 100.0 * np.sum(allvals)))
            return f"{pct:.1f}%\n({absolute:d})"

        fig1, ax1 = plt.subplots()
        word_counts = list(self.hsk_word_counts.values())
        percentages = [
            round(count / sum(word_counts), 2) * 100 for count in word_counts
        ]
        if as_bars:
            bars = ax1.bar(
                HSK_LABELS,
                word_counts,
                color=PLT_HSK_COLORS,
            )
            for bar, count, percentage in zip(bars, word_counts, percentages):
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f"{count}\n{percentage:.0f}%",
                    ha="center",
                    va="bottom",
                )
            # ax1.bar_label(bars)
            ax1.set_ylabel("Number of words")
            ax1.set_xlabel("HSK level")
            plt.grid(axis="y", color="gainsboro")

        else:
            ax1.pie(
                word_counts,
                labels=HSK_LABELS,
                autopct=lambda pct: func(pct, word_counts),
                startangle=0,
                colors=PLT_HSK_COLORS,
            )
            ax1.axis("equal")
        st.pyplot(fig1)

    def analyze_text(self, text: str, use_word_sub_combinations: bool = True):
        self.text = text
        self._parse_text(use_word_sub_combinations)
        self._compute_word_counts()
        self._compute_readabilities()

    def _parse_text(self, use_word_sub_combinations: bool):
        self.seg_text = jieba.cut(self.text)
        for word in self.seg_text:
            if character_is_hanzi(word):
                level: int = self._get_word_level_from_hsk_df(
                    word, use_word_sub_combinations
                )
                self.words_with_level.append((word, level))
                self.annotated_text.append(
                    (word, str(level), HSK_DEFAULT_COLORS[level])
                )
            else:
                self.annotated_text.append(word)
        self.total_words = len(self.words_with_level)

    def _get_word_level_from_hsk_df(
        self, word: str, use_word_sub_combinations: bool
    ) -> int:
        # The default word level is 0, and is the value returned when the word
        # is not find within the HSK dataframe
        word_level = 0
        words = self.hsk_df[self.hsk_df[SIMPLIFIED_WORD_COLUMN_NAME] == word]
        if len(words) > 0:
            word_level = words.iloc[0][LEVEL_COLUMN_NAME]
            if type(word_level) is str:
                # The original HSK3 df has the level 7 as '7-9'
                # the new one was corrected
                word_level = int(word_level.split("-")[0])
            else:
                word_level = int(word_level)
        # If the word level is still 0 then we cut it more and we try to find
        # the best matching element
        # The problem with this method is that it still fails to detect some
        # words like 野兔 because both hanzi
        # are learnt as part of bigger words, it could also recognize falsy a
        # complicated word as HSK1 because of
        # it being negated. The best would be to have a custom dictionary that
        # enhances the HSK entries but it is
        # enough for our current usage.
        if use_word_sub_combinations and word_level == 0 and len(word) > 1:
            seg_list = get_hanzi_sub_combinations(word)
            w_levels = [self._get_word_level_from_hsk_df(
                w, False) for w in seg_list]
            word_level = max(w_levels)
        return word_level

    def _compute_word_counts(self):
        for _, level in self.words_with_level:
            self.hsk_word_counts[level] += 1
        for hsk_level in range(1, 8):
            if hsk_level == 1:
                self.additive_hsk_word_counts[
                    hsk_level
                ] = self.hsk_word_counts[
                    hsk_level
                ]
            else:
                self.additive_hsk_word_counts[hsk_level] = (
                    self.hsk_word_counts[hsk_level]
                    + self.additive_hsk_word_counts[hsk_level - 1]
                )

    def _compute_readabilities(self):
        default_readability_value: int = 0
        for hsk_level in range(1, 8):
            readability = round(
                self.additive_hsk_word_counts[hsk_level] / self.total_words, 2
            )
            self.hsk_readability[hsk_level] = readability
            if (
                readability >= 0.8
                and self.readability_eighty == default_readability_value
            ):
                self.readability_eighty = hsk_level
            if (
                readability >= 0.95
                and self.readability_ninety_five == default_readability_value
            ):
                self.readability_ninety_five = hsk_level
            if (
                readability >= 0.98
                and self.readability_ninety_eight == default_readability_value
            ):
                self.readability_ninety_eight = hsk_level
        if self.readability_eighty == 0:
            self.readability_eighty = 7
        if self.readability_ninety_five == 0:
            self.readability_ninety_five = 7
        if self.readability_ninety_eight == 0:
            self.readability_ninety_eight = 7
