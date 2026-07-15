import serial
import time

PUERTO = "COM3"   # Ajustar al puerto real (ver Administrador de Dispositivos)
puerto = serial.Serial(PUERTO, 9600, timeout=1)
time.sleep(2)   # Esperar a que Arduino reinicie

# Enviar trama de prueba: ID = 5
CABECERA = 0xAA
ID = 5
checksum = CABECERA ^ ID
trama = bytes([CABECERA, ID, checksum])

print(f"Enviando trama: {trama.hex(' ').upper()}")
puerto.write(trama)

time.sleep(0.5)
respuesta = puerto.read_all().decode('utf-8', errors='replace')
print("Respuesta del Arduino:")
print(respuesta)

puerto.close()
