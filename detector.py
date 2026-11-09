from datetime import datetime

def analizar_logs():
    intentos_fallidos = {}

    try:
        with open("eventos.log", "r") as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print("El archivo eventos.log aún no existe. Haz algunos intentos de login fallidos primero.")
        return

    for linea in lineas:
        partes = [p.strip() for p in linea.split(",")]
        if len(partes) < 3:
            continue
        
        fecha_str, evento, usuario = partes[0], partes[1], partes[2]
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")

        if evento == "login_fallido":
            if usuario not in intentos_fallidos:
                intentos_fallidos[usuario] = []
            intentos_fallidos[usuario].append(fecha_obj)

            # Si acumula 3 o más intentos fallidos
            if len(intentos_fallidos[usuario]) >= 3:
                primer_intento = intentos_fallidos[usuario][0]
                deteccion = datetime.now()
                
                # Cálculo del MTTD
                mttd = (deteccion - primer_intento).total_seconds()
                
                print(f"Alerta de seguridad, usuario: {usuario}, intentos fallidos: {len(intentos_fallidos[usuario])}, primer intento: {primer_intento}, detección: {deteccion}")
                print(f"MTTD: {mttd} segundos")
                
                # Simulación de respuesta y cálculo del MTTR
                respuesta_tiempo = datetime.now()
                mttr = (respuesta_tiempo - deteccion).total_seconds()
                print(f"MTTR: {mttr} segundos")
                
                # Registrar en respuesta.log
                with open("respuesta.log", "a") as resp_file:
                    resp_file.write(f"{respuesta_tiempo.strftime('%Y-%m-%d %H:%M:%S')} usuario bloqueado {usuario}\n")
                
                # Reiniciar lista para este usuario
                intentos_fallidos[usuario] = []

if __name__ == "__main__":
    analizar_logs()