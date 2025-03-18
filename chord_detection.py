from itertools import combinations
import re

# 🎵 MIDI ノート番号から音名へのマッピング
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_name(note):
    """MIDIノート番号を音名に変換 (Convert MIDI note number to note name)"""
    octave = (note // 12) - 1  # MIDIノートのオクターブ計算
    note_name = NOTE_NAMES[note % 12]
    return f"{note_name}{octave}"


# 🎹 **すべてのルート音に対応するコード定義**
CHORD_PATTERNS = {
    "": [4, 7],  # メジャー (C)
    "m": [3, 7],  # マイナー (Cm)
    "dim": [3, 6],  # ディミニッシュ (Cdim)
    "aug": [4, 8],  # オーギュメント (Caug)
    "sus4": [5, 7],  # サスペンデッド4 (Csus4)
    "sus2": [2, 7],  # サスペンデッド2 (Csus2)

    # 四和音
    "6": [4, 7, 9],  # メジャー6 (C6)
    "m6": [3, 7, 9],  # マイナー6 (Cm6)
    "M7": [4, 7, 11],  # メジャー7 (CM7)
    "m7": [3, 7, 10],  # マイナー7 (Cm7)
    "7": [4, 7, 10],  # ドミナント7 (C7)
    "dim7": [3, 6, 9],  # ディミニッシュ7 (Cdim7)
    "m7-5": [3, 6, 10],  # ハーフディミニッシュ (Cm7-5)
    "aug7": [4, 8, 10],  # オーギュメント7 (Caug7)
    "M7sus4": [5, 7, 11],  # メジャー7サス4 (CM7sus4)
    "7sus4": [5, 7, 10],  # 7サス4 (C7sus4)

    # テンションコード
    "9": [4, 7, 10, 14],  # 9 (C9)
    "M9": [4, 7, 11, 14],  # メジャー9 (CM9)
    "m9": [3, 7, 10, 14],  # マイナー9 (Cm9)
    "11": [4, 7, 10, 14, 17],  # 11 (C11)
    "M11": [4, 7, 11, 14, 17],  # メジャー11 (CM11)
    "m11": [3, 7, 10, 14, 17],  # マイナー11 (Cm11)
    "13": [4, 7, 10, 14, 17, 21],  # 13 (C13)
    "M13": [4, 7, 11, 14, 17, 21],  # メジャー13 (CM13)
    "m13": [3, 7, 10, 14, 17, 21],  # マイナー13 (Cm13)

    # オルタードコード
    "7(♭5)": [4, 6, 10],  # 7(♭5)
    "7(♯5)": [4, 8, 10],  # 7(♯5)
    "7(♭9)": [4, 7, 10, 13],  # 7(♭9)
    "7(♯9)": [4, 7, 10, 15],  # 7(♯9)
    "7(♭5,♭9)": [4, 6, 10, 13],  # 7(♭5,♭9)

    # その他
    "add9": [4, 7, 14],  # アド9 (Cadd9)
    "6/9": [4, 7, 9, 14],  # 6/9 (C6/9)
    "5": [7],  # パワーコード (C5)
}

# **すべてのルート音に対してコードを生成**
ALL_CHORDS = {}
for root_index, root in enumerate(NOTE_NAMES):
    for chord_name, intervals in CHORD_PATTERNS.items():
        chord_intervals = tuple(sorted([0] + intervals))  # ルート音を 0 として相対音程リストを作る
        ALL_CHORDS[chord_intervals] = f"{root}{chord_name}"


def extract_root_name(chord_name):
    """コード名からルート音を抽出（C, C#, D, ... を取得）"""
    match = re.match(r"([A-G]#?b?)", chord_name)
    return match.group(1) if match else ""


def detect_chord(notes):
    """現在のノートリストからコードを判定 (Detect chord from current notes)"""
    if len(notes) < 2:
        return "（単音）"

    # **最低音（ベース音）を取得**
    bass_note = min(notes)  # 一番低い音
    bass_name = NOTE_NAMES[bass_note % 12]  # ベース音の音名

    # **ルート音の候補（全ノートの音名リスト）**
    possible_roots = sorted(set(n % 12 for n in notes))

    best_match = None
    best_match_name = "不明なコード (Unknown Chord)"

    for root_index in possible_roots:
        root_name = NOTE_NAMES[root_index]

        # **ルート音を基準にした音程リストを作成**
        intervals = sorted([(n - root_index) % 12 for n in notes])

        # **パワーコード（5）の判定**
        if len(intervals) == 1 and intervals[0] == 7:
            return f"{root_name}5"  # **例外的にパワーコードを即確定**

        # **完全一致するコードを検索**
        if tuple(intervals) in ALL_CHORDS:
            best_match = tuple(intervals)
            best_match_name = f"{root_name}{ALL_CHORDS[tuple(intervals)][1:]}"
            break  # 完全一致なら即確定

        # **テンションコードの可能性を判定**
        for base_chord, base_name in ALL_CHORDS.items():
            if len(base_chord) < 3:
                continue  # 単音・パワーコードはスキップ

            base_intervals = set(base_chord)
            input_intervals = set(intervals)

            # 🎵 **基本コード（トライアド＋7th）が含まれていればテンションコードの可能性**
            if base_intervals.issubset(input_intervals):
                tension_notes = input_intervals - base_intervals
                tension_str = ""

                # **テンション音の解析**
                for tension in sorted(tension_notes):
                    if tension == 2:
                        tension_str += "(add9)"
                    elif tension == 9:
                        tension_str += "(9)"
                    elif tension == 10:
                        tension_str += "(♭9)"
                    elif tension == 11:
                        tension_str += "(♯9)"
                    elif tension == 5:
                        tension_str += "(11)"
                    elif tension == 6:
                        tension_str += "(♯11)"
                    elif tension == 7:
                        tension_str += "(♭13)"
                    elif tension == 8:
                        tension_str += "(13)"

                # **最も複雑なコードを優先**
                if len(base_intervals) > len(best_match or []):
                    best_match = base_chord
                    best_match_name = f"{root_name}{base_name[1:]}{tension_str}"

    # **分数コードの適正化**
    if best_match_name != "不明なコード (Unknown Chord)":
        # **コードのルート音を正しく取得**
        root_of_detected_chord = extract_root_name(best_match_name)

        # **ルート音とベース音が異なる場合に分数コードを適用**
        if root_of_detected_chord != bass_name:
            best_match_name = f"{best_match_name}/{bass_name}"

    return best_match_name
