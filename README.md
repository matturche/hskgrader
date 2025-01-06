# HSK Grader

## What is it?

It is a small app to analyze Chinese texts using the Hànyǔ Shuǐpǐng Kǎoshì (HSK) dictionnary entries.

Note that the author(s) of this tool are not affiliated in any way with the Hanban/Confucius Institute Headquarters, responsible for all things related to the HSK.

It is written in python using [streamlit](https://streamlit.io/).

## Sources

[Jieba](https://github.com/fxsjy/jieba/tree/master) is used as the segmented tool for Chinese texts.
HSK2.0 and HSK3.0 lists were found on Github [here](https://github.com/ynot4/hsk-vocabulary/tree/master), and [there](https://github.com/ivankra/hsk30/tree/master) respectively.
Sample texts are from the [Standard Course](https://www.hskstandardcourse.com/) Workbooks or mock tests, edited by the Hanban.

## How to install the app and run it locally

You will need to know what a terminal is and how to use it.
It was written using Python3, so if you don't have it installed on your computer you can go [here](https://realpython.com/installing-python/).
It uses [Poetry](https://python-poetry.org/) to manage python packages and environments, once you have [installed Poetry](https://python-poetry.org/docs/#installation) you can run the following command:

```
poetry install
```

From then you can start the environment:

```
poetry shell
```

And finally run the app in the terminal:

```
streamlit run main.py
```

It should automatically open a new window on `"http://localhost:8501/"`, if not you can copy the address and paste it in your browser.
You can stop it by pressing `Ctrl-C` in your terminal, and exit poetry's environment by entering `exit`.

## Notes on usage

The HSK2.0 and HSK3.0 vocabulary entries are NOT complete by any means, and this is made relatively clear when using this app.
Many words are "missing", and thus the app resorts to two workarounds to make it work:

1. Decomposing words into subwords if no match is found (i.e. a word in the format ABCD will result in [A, AB, ABC, B, BC, BCD, C, CD, D]),
the resulting score being the highest level matched on any of the subcombination. It is not a perfect method, but it proves to be a very
good and simple heuristic to enhance matches.

2. Using custom vocabulary entries, they can be found in `data/hsk_dict_expansion.csv`, the entries are attributed an arbitrary level. It is
arbitrary because it is based on my judgment. I simply try to find the closest word(s) in the HSK2.0 entries and give it the corresponding level,
or 1 level higher if I find it to be a harder word. For complex compound words, I try to balance the moment each hanzi was seen in other words,
and the resulting complexity of the final word.

Both of these methods are optional, using checkboxes in the app, you will quickly see, however, that when not using them it is very rare to go above
70% readability, even with the addition of HSK7-9 for HSK2.0, even on texts made for HSK learners and edited by the Hanban.
