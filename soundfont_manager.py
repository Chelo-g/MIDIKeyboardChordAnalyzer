import os
import fluidsynth

SF2_FOLDER = "C:/tools/sf2"
SYNTH_GAIN = 1.0 # 例: 0.5（半分の音量）、2.0（倍の音量）# Example: 0.5 (half volume), 2.0 (double volume)

def list_sf2_files():
    """フォルダ内の .sf2 ファイルをリストアップ (List available .sf2 files in the folder)"""
    return [f for f in os.listdir(SF2_FOLDER) if f.endswith(".sf2")]


def select_sf2():
    """ユーザーに SoundFont を選ばせる (Let the user choose a SoundFont)"""
    sf2_files = list_sf2_files()
    if not sf2_files:
        print("❌ .sf2 ファイルが見つかりません。 (No .sf2 files found.)")
        exit()

    print("\n🎵 使用する SoundFont を選択 (Select a SoundFont):")
    for i, sf2 in enumerate(sf2_files):
        print(f"  [{i}] {sf2}")

    while True:
        try:
            choice = int(input("\n🔹 選択 (番号を入力): (Enter a number): "))
            if 0 <= choice < len(sf2_files):
                sf2_path = os.path.join(SF2_FOLDER, sf2_files[choice])
                return init_fluidsynth(sf2_path)
            else:
                print("❌ 無効な番号です。もう一度選択してください。 (Invalid number. Please try again.)")
        except ValueError:
            print("❌ 数字を入力してください。 (Please enter a number.)")


def list_presets(fs, sfid):
    """SoundFont のプリセット一覧を取得 (Get a list of available presets in the SoundFont)"""
    presets = []
    for bank in range(128):
        for program in range(128):
            preset_name = fs.sfpreset_name(sfid, bank, program)
            if preset_name:
                presets.append((bank, program, preset_name))
    return presets


def select_preset(fs, sfid):
    """ユーザーにプリセットを選ばせる (Let the user choose a preset)"""
    presets = list_presets(fs, sfid)
    if not presets:
        print("❌ プリセットが見つかりません！ (No presets found!)")
        exit()

    print("\n🎵 使用する音色（プリセット）を選択 (Select an instrument preset):")
    for i, (bank, program, name) in enumerate(presets):
        print(f"  [{i}] {name} (Bank {bank}, Program {program})")

    while True:
        try:
            choice = int(input("\n🔹 選択 (番号を入力): (Enter a number): "))
            if 0 <= choice < len(presets):
                return presets[choice]
            else:
                print("❌ 無効な番号です。もう一度選択してください。 (Invalid number. Please try again.)")
        except ValueError:
            print("❌ 数字を入力してください。 (Please enter a number.)")


def init_fluidsynth(sf2_path):
    """FluidSynth の初期化 (Initialize FluidSynth)"""
    fs = fluidsynth.Synth()
    fs.start(driver="dsound")
    fs.setting("synth.gain", SYNTH_GAIN)
    fs.setting("midi.driver", "none")  # ✅ MIDI 競合を防ぐため "none" を設定 (Set "none" to avoid MIDI conflicts)

    sfid = fs.sfload(sf2_path)
    if sfid == -1:
        print(f"❌ SoundFont のロードに失敗しました: {sf2_path} (Failed to load SoundFont: {sf2_path})")
        exit()

    fs.program_reset()  # 既存の SoundFont をリセット (Reset existing SoundFont)

    # ✅ `select_preset()` を呼び出してプリセットを選択 (Call `select_preset()` to choose a preset)
    bank, program, preset_name = select_preset(fs, sfid)
    fs.program_select(0, sfid, bank, program)
    print(f"✅ 選択されたプリセット: {preset_name} (Bank {bank}, Program {program}) (Selected preset: {preset_name})")
    print("\n🎹 MIDI キーボードを監視中（Ctrl+C で終了）... (Monitoring MIDI keyboard... Press Ctrl+C to exit.)")
    print("🔄 SoundFont を変更するには `a` を押してください。 (Press `a` to change SoundFont.)")
    return fs, sfid, sf2_path


def reload_soundfont(fs):
    """SoundFont を変更する (Change SoundFont)"""
    print("\n🔄 SoundFont を変更中... (Changing SoundFont...)\n")

    # ✅ 既存の SoundFont をリセット (Reset existing SoundFont)
    fs.program_reset()

    # ✅ 新しい SoundFont を選択 (Select a new SoundFont)
    return select_sf2()
