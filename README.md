# HSK Grader

## What is it?

It is a small app to analyze Chinese texts using the Hànyǔ Shuǐpǐng Kǎoshì (HSK) dictionnary entries.

Note that the author(s) of this tool are not affiliated in any way with the Hanban/Confucius Institute Headquarters, responsible for all things related to the HSK.

It is written in python using [Streamlit](https://streamlit.io/).

The app is deployed on the Streamlit Community Cloud, and is available at [hskgrader.streamlit.app](https://hskgrader.streamlit.app/).

## Sources

[Jieba](https://github.com/fxsjy/jieba/tree/master) is used as the segmentation tool for Chinese texts.

HSK2.0 and HSK3.0 lists were found on Github [here](https://github.com/ynot4/hsk-vocabulary/tree/master), and [there](https://github.com/ivankra/hsk30/tree/master) respectively.

Sample texts are from the [Standard Course](https://www.hskstandardcourse.com/) Workbooks or mock tests, edited by the Hanban.

## How to install the app and run it locally

You will need to know what a terminal is and how to use it.

It was written using Python3, so if you don't have it installed on your computer you can go [here](https://realpython.com/installing-python/).

It uses [Poetry](https://python-poetry.org/) to manage python packages and environments, once you have [installed Poetry](https://python-poetry.org/docs/#installation) you can run the following command:

```
poetry install
```

If you are not in China, then you will find useful, just before running the command above, to just delete the following lines in the `pyproject.toml` file:

```
[[tool.poetry.source]]
name = "mirrors"
url = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/"
priority = "primary"
```
 
From then you can start the environment:

```
poetry shell
```

And finally run the app in the terminal, from the second `hskgrader` directory (where the `main.py` script is located):

```
streamlit run main.py -- --local 
```

It should automatically open a new window on `"http://localhost:8501/"`, if not you can copy the address and paste it in your browser.
You can stop it by pressing `Ctrl-c` in your terminal, and exit poetry's environment by entering `exit`.

## Notes on usage

The HSK2.0 and HSK3.0 vocabulary entries are NOT complete by any means, and this is made relatively clear when using this app.
Many words are "missing", and thus the app resorts to two workarounds to make it work:

1. Breaking words down into subwords if no match is found (i.e. a word in the format ABCD will result in [A, AB, ABC, B, BC, BCD, C, CD, D]),
the resulting score being the highest level matched on any of the subcombination. It is not a perfect method, but it proves to be a very
good and simple heuristic to enhance matches.

2. Using custom vocabulary entries, they can be found in `data/hsk_dict_expansion.csv`, the entries are attributed an arbitrary level. It is
arbitrary because it is based on my judgment. I simply try to find the closest word(s) in the HSK2.0 entries and give it the corresponding level,
or 1 level higher if I find it to be a harder word. For complex compound words, I try to balance the moment each hanzi was seen in other words,
and the resulting complexity of the final word.

Both of these methods are optional, using checkboxes in the app, you will quickly see, however, that when not using them it is very rare to go above
70% readability, even with the addition of HSK7-9 for HSK2.0, even on texts made for HSK learners and edited by the Hanban.

## How to generate translations

Translations are genereated using the GETTEXT module.

First a `.pot` file has to be created for all translations with the following command:

```
xgettext -d base -o locales/hskgrader.pot hskgrader/main.py
```

Take care to replace the `CHARSET` section in the file with `UTF-8`.

Then, for each target language, a `.po` file has to be created, containing the content from the previously generated `.pot` file.

Finally, a `.mo` file has to be generated for each target language by running the following command:

```
msgfmt -o locales/{lang}/LC_MESSAGES/hskgrader.mo locales/{lang}/LC_MESSAGES/hskgrader.po"
```

Replace `{lang}` with the desired language folder.

An alternative can be to use a PO text editor like [Poedit](https://poedit.net/download) which will take care of the `.mo` conversion.
