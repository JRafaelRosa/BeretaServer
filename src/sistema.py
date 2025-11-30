import psutil
import os
from src.config import app, add_log

try:
    import wmi
except ImportError:
    wmi = None


@app.route('/status')
def get_status():
    """Retorna JSON com uso de CPU, RAM e Temperatura (Tentativa Windows)"""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent

    temp = "--"

    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if entries:
                    temp = round(entries[0].current)
                    break
    except:
        pass

    if temp == "--" and wmi:
        try:
            w = wmi.WMI(namespace="root\\wmi")
            temperature_info = w.MSAcpi_ThermalZoneTemperature()
            if temperature_info:

                kelvin = temperature_info[0].CurrentTemperature
                temp_celsius = (kelvin - 2732) / 10.0
                temp = round(temp_celsius)
        except:
            pass

    return {"cpu": cpu, "ram": ram, "temp": temp}


@app.route('/timer/<minutos>')
def set_timer(minutos):
    try:
        min = int(minutos)
        if min == 0:
            os.system("shutdown /a")
            add_log("Timer Cancelado")
        else:
            segundos = min * 60
            os.system(f"shutdown /s /t {segundos}")
            add_log(f"Desligamento em {min} min")
    except:
        pass
    return "OK"