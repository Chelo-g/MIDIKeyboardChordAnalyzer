import sys
import time
import keyboard
from soundfont_manager import select_sf2, select_preset, reload_soundfont, init_fluidsynth
from midi_handler import open_midi_port
from chord_detection import detect_chord, note_to_name

# ✅ **MIDI ポートを最初に開く**
midi_in = open_midi_port()
if midi_in is None:
    print("❌ MIDI ポートの取得に失敗しました。プログラムを終了します。 (Failed to open MIDI port. Exiting...)")
    sys.exit(1)  # ✅ **エラーコード 1 で明示的に終了**

# ✅ **FluidSynth の初期化**
fs, sfid, sf2_path = select_sf2()

# 🎵 現在押されているノートを管理
active_notes = set()
last_display = ""  # **前回の表示内容を保存 (Previous display content)**

while True:
    # ✅ `a` を押したら SoundFont を再選択
    if keyboard.is_pressed("a"):
        sys.stdout.write("\b \b")  # ✅ **BSで `a` を削除 (Remove 'a' with Backspace)**
        fs, sfid, sf2_path = reload_soundfont(fs)

    # ✅ MIDI メッセージの取得（複数取得でラグを削減）
    while True:
        msg = midi_in.get_message()
        if msg is None:
            break  # **メッセージがなくなったら次のループへ (No more messages, move to next loop)**

        raw_message, deltatime = msg
        status, note, velocity = raw_message[0], raw_message[1], raw_message[2]

        # 🎵 Note ON
        if status == 144 and velocity > 0:
            fs.noteon(0, note, velocity)
            active_notes.add(note)

        # 🔇 Note OFF
        elif status == 128 or (status == 144 and velocity == 0):
            fs.noteoff(0, note)
            active_notes.discard(note)

    # 🎹 **現在のコードを表示 (Display current notes and chord)**
    if active_notes:  # ✅ **ノートがある場合のみ表示 (Show only if notes are active)**
        chord = detect_chord(list(active_notes))
        note_names = [note_to_name(n) for n in sorted(active_notes)]
        output_text = f"🎶 現在のノート: {', '.join(note_names)} | コード: {chord} (Current Notes & Chord)"
    else:
        output_text = "🎵 待機中... (キーを押してください) (Waiting... Press a key)"  # ✅ **キーが押されていないときの表示 (Show when no key is pressed)**

    # ✅ **前回の表示内容と同じなら更新しない (Update only if content changes)**
    if output_text != last_display:
        sys.stdout.write("\r\033[K" + output_text)
        sys.stdout.flush()
        last_display = output_text  # **最新の表示内容を保存 (Save latest display content)**

    # ✅ **待機時間を最適化 (Optimize wait time)**
    time.sleep(0.005)  # **0.01 → 0.005 に短縮し、より即時反応 (Reduce delay for better response)**
