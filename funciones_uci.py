import os
import json
import csv

def crear_carpetas():
    carpeta_principal = "sistema_uci"
    json_dir = os.path.join(carpeta_principal, "exportaciones_json")
    csv_dir = os.path.join(carpeta_principal, "exportaciones_csv")
    
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
        
    return json_dir, csv_dir

def leer_paciente_hl7(ruta_archivo):
    info_paciente = {"nombre": "N/A", "id": "N/A", "ubicacion": "N/A"}
    
    if not os.path.exists(ruta_archivo):
        print("El archivo no existe.")
        return info_paciente

    archivo = open(ruta_archivo, "r", encoding="utf-8")
    for linea in archivo:
        linea = linea.strip()
        
        if "PID" in linea:
            partes = linea.split("|")
            if len(partes) > 3:
                info_paciente["id"] = partes[3].strip()
            if len(partes) > 5:
                info_paciente["nombre"] = partes[5].replace("^", " ").strip()
        elif "PV1" in linea:
            partes = linea.split("|")
            if len(partes) > 3:
                info_paciente["ubicacion"] = partes[3].strip()
    archivo.close()
    
    return info_paciente


def leer_signos_vitales_xml(ruta_archivo):
    lista_signos = []
    
    if not os.path.exists(ruta_archivo):
        print("El archivo no existe.")
        return lista_signos

    archivo = open(ruta_archivo, "r", encoding="utf-8")
    contenido = archivo.read()
    archivo.close()

    for linea in contenido.splitlines():
        if "<sign " in linea or "<sign>" in linea:
            nombre = "N/A"
            valor = "N/A"
            unidad = "N/A"

            if 'name="' in linea:
                nombre = linea.split('name="')[1].split('"')[0]
            elif 'nombre="' in linea:
                nombre = linea.split('nombre="')[1].split('"')[0]

            if 'value="' in linea:
                valor = linea.split('value="')[1].split('"')[0]
            elif 'valor="' in linea:
                valor = linea.split('valor="')[1].split('"')[0]
                
            if 'unit="' in linea:
                unidad = linea.split('unit="')[1].split('"')[0]
            elif 'unidad="' in linea:
                unidad = linea.split('unidad="')[1].split('"')[0]

            lista_signos.append({"nombre": nombre, "valor": valor, "unidad": unidad})

    return lista_signos


def leer_diagnostico_xml(ruta_archivo):
    info_fhir = {"Categoria": "N/A", "Conclusion": "N/A", "Medico": "N/A"}
    
    if not os.path.exists(ruta_archivo):
        print("El archivo no existe.")
        return info_fhir

    archivo = open(ruta_archivo, "r", encoding="utf-8")
    contenido = archivo.read()
    archivo.close()

    if "<category>" in contenido and "</category>" in contenido:
        info_fhir["Categoria"] = contenido.split("<category>")[1].split("</category>")[0].strip()
    if "<conclusion>" in contenido and "</conclusion>" in contenido:
        info_fhir["Conclusion"] = contenido.split("<conclusion>")[1].split("</conclusion>")[0].strip()
    if "<physician>" in contenido and "</physician>" in contenido:
        info_fhir["Medico"] = contenido.split("<physician>")[1].split("</physician>")[0]

    return info_fhir


def leer_telemetria_txt(ruta_archivo):
    lista_telemetria = []
    
    if not os.path.exists(ruta_archivo):
        print("El archivo no existe.")
        return lista_telemetria

    archivo = open(ruta_archivo, "r", encoding="utf-8")
    for linea in archivo:
        linea = linea.strip()
        if not linea:
            continue
        partes = linea.split("|")
        if len(partes) >= 5:
            lista_telemetria.append({"fecha_hora": partes[0].strip(), "id_paciente": partes[1].strip(), "sensor": partes[2].strip(), "valor": partes[3].strip(), "estado": partes[4].strip()})
    archivo.close()
    
    return lista_telemetria


def exportar_a_json(id_paciente, diccionario_historia, carpeta_json):
    ruta = os.path.join(carpeta_json, "paciente_" + str(id_paciente) + ".json")
    archivo = open(ruta, "w", encoding="utf-8")
    json.dump(diccionario_historia, archivo, indent=4, ensure_ascii=False)
    archivo.close()
    print("Exportado a JSON correctamente en:", ruta)
    

def exportar_a_csv(historia_clinica_general, carpeta_csv):
    ruta = os.path.join(carpeta_csv, "signos_vitales_unificados.csv")
    archivo = open(ruta, "w", newline="", encoding="utf-8")
    escritor = csv.writer(archivo, delimiter=";")
    
    escritor.writerow(["ID_Paciente", "Nombre_Signo", "Valor", "Unidad"])
    
    for id_paciente in historia_clinica_general:
        paciente = historia_clinica_general[id_paciente]
        signos = paciente.get("signos_vitales", [])
        for s in signos:
            escritor.writerow([id_paciente, s["nombre"], s["valor"], s["unidad"]])
            
    archivo.close()
    print("Exportado a CSV correctamente en:", ruta)