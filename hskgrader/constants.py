from typing import Dict, List

BASE_GITHUB_PATH = """
    https://raw.githubusercontent.com/matturche/hskgrader/refs/heads/main/data/
"""
SIMPLIFIED_WORD_COLUMN_NAME: str = "Simplified"
LEVEL_COLUMN_NAME: str = "Level"
HSK_COLORBLING_COLORS: Dict[int, str] = {
    0: "#BFBFBF",  # For unrecognized words using HSK dict entries
    1: "#DC267F",
    2: "#FE6100",
    3: "#FFB000",
    4: "#35D040",
    5: "#648FFF",
    6: "#785EF0",
    7: "#8926B1",  # 7-9 levels are grouped together
}
HSK_DEFAULT_COLORS: Dict[int, str] = {
    0: "#E6E6E6",  # For unrecognized words using HSK dict entries
    1: "#FFCBCB",
    2: "#FDD6BE",
    3: "#FFE8C0",
    # There is a shif towards blue from here as levels are harder from here
    4: "#BEFFFE",
    5: "#B6E5FF",
    6: "#BBC5FF",
    7: "#DDBCFF",  # 7-9 levels are grouped together
}

PLT_HSK_COLORS: List[str] = [
    "silver",
    "lightcoral",
    "bisque",
    "lemonchiffon",
    "paleturquoise",
    "skyblue",
    "cornflowerblue",
    "plum",
]

HSK_LABELS: List[str] = [
    "Unknown",
    "HSK1",
    "HSK2",
    "HSK3",
    "HSK4",
    "HSK5",
    "HSK6",
    "HSK7-9",
]

AVAILABLE_TEXTS = [
    f"hsk5/text{i}.txt" for i in range(1, 6)
].extend([
    f"hsk6/text{i}.txt" for i in range(1, 12)
])
