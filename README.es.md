# AudioHub Pro

Read this in: [English](README.md) | [Español](README.es.md)

Un enrutador de audio Bluetooth para Linux Mint para auriculares TWS y otros dispositivos de audio. Conecta tus parlantes/TWS a Linux y enruta el audio con una interfaz simple.

## ¿Por qué?

Este proyecto nació de la necesidad personal de unificar mi flujo de trabajo. Al cambiar constantemente entre mi PC y mi iPhone, me resultaba muy poco práctico tener que lidiar con el gestor nativo de Bluetooth, que en Linux Mint XFCE, es propenso a errores o fallos en los momentos más inoportunos.

AudioHub Pro busca eliminar esa fricción ofreciendo una interfaz más centralizada y facil para gestionar mis auriculares (TWS) y mi iPhone sin complicaciones ni configuraciones fallidas.

## Características

- Escaneo y conexión de dispositivos Bluetooth
- Enrutamiento de audio a múltiples dispositivos
- Visualizador de audio en tiempo real
- Guardar configuraciones de dispositivos
- Funciona con PulseAudio y PipeWire

## Requisitos

- Linux (probado en Linux Mint)
- `bluetoothctl` y `pactl` instalados
- Python 3.8+

## Inicio rápido

1. Creá un entorno virtual e instalá las dependencias:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Ejecutá la aplicación:

```bash
./run_app.sh
# o
python3 app.py
```

3. Para depurar problemas de audio y Bluetooth:

```bash
python3 debug_audio.py
```

Esto mostrará todos los dispositivos BT conectados, los sinks/sources de audio disponibles y te ayudará a identificar por qué el enrutamiento de audio podría fallar.

## Notas

- Asegúrate de que tu usuario tenga permisos para gestionar dispositivos Bluetooth y de audio.
- `settings.json` se crea en la carpeta del proyecto cuando guardas las MAC desde la interfaz.

## Solución de problemas

**"El audio no se enruta a los TWS"**

1. Asegúrate de que los TWS (auriculares) estén **activados y en modo de emparejamiento**.
2. Hacé clic en **🔍 Escanear dispositivos Bluetooth** para descubrirlos.
3. Seleccioná los TWS del menú desplegable y hacé clic en **BUILD & SYNC**.
   - Esto establece los TWS como tu dispositivo de salida de audio predeterminado.
4. Abrí cualquier aplicación de audio (navegador, reproductor multimedia, etc.) y reproducí algo.
   - El audio debería salir por los auriculares TWS.
5. Revisá los logs en la aplicación para ver mensajes de error.

**"Veo los dispositivos pero el audio aún no se reproduce"**

1. Ejecutá la herramienta de depuración para verificar el estado de PulseAudio:
   ```bash
   python3 debug_audio.py
   ```
   - Buscá tus TWS en la sección "Available Audio Sinks"
   - Si no aparecen, reiniciá Bluetooth: `bluetoothctl power off && bluetoothctl power on`

2. Establecé manualmente el sink predeterminado:
   ```bash
   pactl set-default-sink bluez_output.XX_XX_XX_XX_XX_XX.1
   ```
   (Reemplazá `XX_XX_...` con la MAC de tus TWS, usando guiones bajos)

3. Probá el audio:
   ```bash
   speaker-test -t wav -c 2
   ```

**"El audio se quedó bloqueado después de cerrar la app"**

Ejecutá el script de limpieza:
```bash
bash cleanup_audio.sh
```

O reiniciá PulseAudio:
```bash
systemctl --user restart pulseaudio
```

## Licencia

MIT — ver `LICENSE`.