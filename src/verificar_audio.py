import sounddevice as sd

print("=== Dispositivos de audio disponibles ===\n")
print(sd.query_devices())
print("\n=== Dispositivo de entrada por defecto ===")
print(sd.default.device)
