import rtmidi


def open_midi_port():
    """MIDI 入力ポートを開く (Open MIDI input port)"""
    midi_in = rtmidi.MidiIn(rtapi=rtmidi.API_UNSPECIFIED)  # ✅ API を明示的に指定 (Explicitly specify API)
    ports = midi_in.get_ports()

    if not ports:
        print("❌ MIDI デバイスが見つかりません。接続を確認してください。 (No MIDI device found. Check connection.)")
        exit()

    print(f"✅ MIDI ポートを開こうとしています: {ports[0]} (Attempting to open MIDI port: {ports[0]})")

    try:
        midi_in.open_port(0)
        print(f"🎹 MIDI ポートを開きました: {ports[0]} (MIDI port opened: {ports[0]})")
    except rtmidi.SystemError as e:
        print(f"❌ MIDI ポートを開けません: {e} (Failed to open MIDI port: {e})")
        if "error creating Windows MM MIDI input port" in str(e):
            print("🔄 MIDI ポートを閉じて1回だけ再試行... (Closing MIDI port and retrying once...)")
            try:
                midi_in.close_port()  # ✅ 既存の MIDI ポートを閉じる (Close existing MIDI port)
                midi_in.open_port(0)  # ✅ 1回だけリトライ (Retry once)
                print(f"🎹 MIDI ポートを開き直しました: {ports[0]} (MIDI port reopened: {ports[0]})")
            except rtmidi.SystemError:
                print("❌ MIDI ポートの再試行に失敗しました。終了します。 (MIDI port retry failed. Exiting.)")
                return None  # **ここで None を返すことで無限ループを防ぐ (Return None to prevent infinite loop)**
        else:
            return None  # **エラーが発生した場合は None を返す (Return None if error occurs)**

    return midi_in
