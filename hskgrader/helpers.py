import os
import requests
from requests.compat import urljoin
from io import StringIO
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List

from constants import (
    AVAILABLE_TEXTS,
    BASE_GITHUB_PATH,
    DATAFRAMES_TTL,
    LEVEL_COLUMN_NAME,
    PLT_HSK_COLORS,
    SIMPLIFIED_WORD_COLUMN_NAME,
)


@st.cache_data(ttl=DATAFRAMES_TTL)
def load_github_dataframe(url: str) -> pd.DataFrame:
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error("Failed to load data from GitHub.")
        return pd.DataFrame()


def load_github_text_files() -> Dict[str, str]:
    files = []
    texts = {}
    for key, value in AVAILABLE_TEXTS.items():
        for i in range(1, value + 1):
            files.append(f"{key}/text{i}.txt")
    for file in files:
        name = f"{file.replace('/', '-')}"
        text = load_github_text_file(
            urljoin(BASE_GITHUB_PATH, f"texts/{file}")
        )
        texts[name] = text
    return texts


@st.cache_data
def load_github_text_file(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        st.error("Failed to load data from GitHub.")
        return ""


@st.cache_data
def load_text_files_from_dir(path: str) -> Dict[str, str]:
    text_dict = {}
    for root, _, files in os.walk(path):
        for file in files:
            name = f"{root.split('/')[-1]}-{file.split('.')[0]}"
            fullpath = os.path.join(root, file)
            if file.endswith(".txt"):
                with open(fullpath, "r") as f:
                    text_dict[name] = f.read()
    return text_dict


def character_is_hanzi(text: str) -> bool:
    return "\u4E00" <= text[0] <= "\u9FFF"


@st.cache_data
def extand_hsk_df_with_custom_df(
    hsk_df: pd.DataFrame, custom_df: pd.DataFrame
) -> pd.DataFrame:
    extanded_df = pd.concat([hsk_df, custom_df])
    # Clean the dupplicates if necessary (especially for HSK3.0)
    extanded_df.drop_duplicates(
        subset=[SIMPLIFIED_WORD_COLUMN_NAME], keep="first", inplace=True
    )
    return extanded_df.sort_values(by=LEVEL_COLUMN_NAME)


def get_hanzi_sub_combinations(word: str) -> List[str]:
    sub_combinations: List[str] = []
    if len(word) == 2:
        sub_combinations.extend([hanzi for hanzi in word])
    elif len(word) > 2:
        next_word = word[1:]
        sub_combinations.extend([word[0:i] for i in range(1, len(word))])
        sub_combinations.append(next_word)
        sub_combinations.extend(get_hanzi_sub_combinations(next_word))
    return sub_combinations


@st.cache_data
def draw_number_of_words_per_hsk_level(
    df: pd.DataFrame, with_hsk7: bool = True
):
    words_per_level = df.groupby(LEVEL_COLUMN_NAME).size()
    hsk_cumsum = list(words_per_level.cumsum())
    fig1, ax1 = plt.subplots()
    ax1.set_ylabel("Number of words")
    ax1.set_xlabel("HSK level")
    if with_hsk7:
        ax1.set_ylim(0, 6000)
        ax1.set_yticks(list(range(0, 6000, 500)))
    else:
        lim = max(words_per_level) + 50
        ax1.set_ylim(0, lim)
        ax1.set_yticks(list(range(0, lim, 50)))
    plt.grid(axis="y", color="gainsboro")
    levels = df[LEVEL_COLUMN_NAME].unique()
    labels = [f"HSK{i}" if i > 0 and i < 7 else "HSK7-9" for i in levels]
    colors = [PLT_HSK_COLORS[int(i)] for i in levels]
    ax1.bar(
        labels,
        list(words_per_level),
        color=colors,
    )
    st.pyplot(fig1)
    st.markdown("#### Cumulative sums:")
    cols = st.columns(len(labels) - 1)
    for i, col in enumerate(cols):
        if len(hsk_cumsum) > i + 1:
            col.metric(
                label=labels[i + 1],
                value=hsk_cumsum[i + 1],
                delta=hsk_cumsum[i + 1] - hsk_cumsum[i],
            )


@st.cache_data
def get_hsk_version_word_differences(
    hsk20_df: pd.DataFrame, hsk30_df: pd.DataFrame
) -> pd.DataFrame:
    version_col_name = "Version"
    hsk20_col = ["2.0" for _ in range(len(hsk20_df))]
    hsk30_col = ["3.0" for _ in range(len(hsk30_df))]
    hsk20_df_cp = hsk20_df.copy()
    hsk30_df_cp = hsk30_df.copy()
    hsk20_df_cp[version_col_name] = hsk20_col
    hsk30_df_cp[version_col_name] = hsk30_col
    concat_df = pd.concat([hsk20_df_cp, hsk30_df_cp])
    concat_df.drop_duplicates(
        subset=[SIMPLIFIED_WORD_COLUMN_NAME], keep=False, inplace=True
    )
    return concat_df.sort_values(by=LEVEL_COLUMN_NAME)


@st.cache_data
def get_unique_hanzi_dataframe(hsk_df: pd.DataFrame) -> pd.DataFrame:
    unique_hanzis = {col: [] for col in list(hsk_df)}
    for _, row in hsk_df.iterrows():
        for hanzi in row[SIMPLIFIED_WORD_COLUMN_NAME]:
            for col in list(hsk_df):
                if col == SIMPLIFIED_WORD_COLUMN_NAME:
                    unique_hanzis[SIMPLIFIED_WORD_COLUMN_NAME].append(hanzi)
                else:
                    unique_hanzis[col].append(row[col])
    unique_hanzis = (
        pd.DataFrame(unique_hanzis)
        .drop_duplicates(subset=[SIMPLIFIED_WORD_COLUMN_NAME], keep="first")
        .reset_index(drop=True)
    )
    return unique_hanzis


@st.cache_data
def reformat_hsk_dfs_and_extend_hsk20_with_level_7(
    hsk20_df: pd.DataFrame, hsk30_df: pd.DataFrame
):
    # Filter columns names
    column_names = ["Simplified", "Pinyin", "Level"]
    hsk20_df = hsk20_df[column_names].copy()
    hsk30_df = hsk30_df[column_names].copy()
    hsk30_df['Level'] = hsk30_df['Level'].apply(
        lambda x: 7 if x == "7-9" else x
    )
    hsk30_7 = hsk30_df[hsk30_df['Level'] == 7].copy()
    st.write(hsk30_7)
    st.write(hsk20_df)
    new_hsk2_df = pd.concat([hsk20_df, hsk30_7])
    new_hsk2_df.drop_duplicates(
        subset=['Simplified'], keep="first", inplace=True)
    st.write(new_hsk2_df)
    new_hsk2_df.to_csv("../data/new_hsk2-0.csv", sep=',', index=False)
    hsk30_df.to_csv("../data/new_hsk3-0.csv", sep=',', index=False)
