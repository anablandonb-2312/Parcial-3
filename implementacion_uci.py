import os
import funciones_uci as f_uci

# Estructura del diccionario historia_clinica_general:
# {
#   "ID_PACIENTE": {
#       "paciente_hl7": {"nombre": ..., "id": ..., "ubicacion": ...},
#       "signos_vitales": [{"nombre": ..., "valor": ..., "unidad": ...}, ...],
#       "diagnostico_fhir": {"Categoria": ..., "Conclusion": ..., "Medico": ...},
#       "telemetria": [{"fecha_hora": ..., "id_paciente": ..., "sensor": ..., "valor": ..., "estado": ...}, ...]
#   }
# }
historia_clinica_general = {}

while True:
    print("\n" + "=" * 55)
    print("    MÓDULO DE INTEROPERABILIDAD Y PROCESAMIENTO - HOSPITAL CENTRAL -UCI")
    print("=" * 55)
    print("1. Cargar e integrar archivos de paciente")
    print("2. Visualizar HCE consolidada")
    print("3. Exportar datos")
    print("4. Salir del programa")
    print("=" * 55)

    opcion = input("Seleccione una opción (1-4): ").strip()

    if opcion == "1":
        print("\n--- INGRESO DE RUTAS DE ARCHIVOS DEL PACIENTE ---")
        r_hl7 = input("Ruta de archivo HL7 (.txt): ").strip()
        r_signos = input("Ruta de archivo Signos Vitales (.xml): ").strip()
        r_fhir = input("Ruta de archivo Diagnostico (.xml): ").strip()
        r_telem = input("Ruta de archivo Telemetría (.txt): ").strip()

        # Verificar si todos los archivos existen antes de leer
        if os.path.exists(r_hl7) and os.path.exists(r_signos) and os.path.exists(r_fhir) and os.path.exists(r_telem):
            info_hl7 = f_uci.leer_paciente_hl7(r_hl7)
            id_paciente = info_hl7.get("id", "DESCONOCIDO")

            if id_paciente == "N/A" or not id_paciente:
                id_paciente = "PACIENTE_DESCONOCIDO"

            signos_vitales = f_uci.leer_signos_vitales_xml(r_signos)
            diagnostico_fhir = f_uci.leer_diagnostico_xml(r_fhir)
            registros_telemetria = f_uci.leer_telemetria_txt(r_telem)

            historia_clinica_general[id_paciente] = {
                "paciente_hl7": info_hl7,
                "signos_vitales": signos_vitales,
                "diagnostico_fhir": diagnostico_fhir,
                "telemetria": registros_telemetria
            }

            print(f"\n Paciente ID [{id_paciente}] integrado correctamente a la Historia Clínica.")
        else:
            print("\n Error: Una o más rutas de archivo no existen. Verifique los nombres e intente de nuevo.")

    elif opcion == "2":
        if not historia_clinica_general:
            print("\n No hay historias clínicas registradas en el sistema.")
        else:
            print("\n" + "=" * 75)
            print("      HISTORIA CLÍNICA ELECTRÓNICA CONSOLIDADA - SISTEMA UCI")
            print("=" * 75)

            for id_paciente, hc in historia_clinica_general.items():
                hl7 = hc.get("paciente_hl7", {})
                fhir = hc.get("diagnostico_fhir", {})
                signos = hc.get("signos_vitales", [])
                telem = hc.get("telemetria", [])

                print(f"\n PACIENTE ID: {id_paciente}")
                print(f"   • Nombre         : {hl7.get('nombre', 'N/A')}")
                print(f"   • Ubicación UCI  : {hl7.get('ubicacion', 'N/A')}")
                print("   • Diagnóstico FHIR:")
                print(f"       - Categoría  : {fhir.get('Categoria', 'N/A')}")
                print(f"       - Conclusión : {fhir.get('Conclusion', 'N/A')}")
                print(f"       - Médico     : {fhir.get('Medico', 'N/A')}")

                print("   • Signos Vitales Registrados:")
                if signos:
                    for s in signos:
                        print(f"       - {s.get('nombre')}: {s.get('valor')} {s.get('unidad')}")
                else:
                    print("       - Sin registros.")

                print("   • Telemetría Continua:")
                if telem:
                    for t in telem[:3]:
                        print(f"       - [{t.get('fecha_hora')}] Sensor: {t.get('sensor')} | Valor: {t.get('valor')} | Estado: {t.get('estado')}")
                    if len(telem) > 3:
                        print(f"       - ... ({len(telem) - 3} registros más)")
                else:
                    print("       - Sin registros.")

                print("-" * 75)

    
    elif opcion == "3":
        if not historia_clinica_general:
            print("\n La historia clínica está vacía. Cargue información antes de exportar.")
        else:
            # Creación de directorios con el módulo
            json_dir, csv_dir = f_uci.crear_carpetas()

            print("\n Exportando información del sistema...")

            for id_paciente, hc in historia_clinica_general.items():
                f_uci.exportar_a_json(id_paciente, hc, json_dir)

            f_uci.exportar_a_csv(historia_clinica_general, csv_dir)

            print("\n Exportación completada exitosamente")
            print(f"   • JSONs guardados en : {json_dir}")
            print(f"   • CSV guardado en   : {csv_dir}")


    elif opcion == "4":
        print("\n Cerrando el Módulo de Interoperabilidad UCI. ¡Hasta pronto!")
        break

    else:
        print(" Opción inválida. Seleccione un número entre 1 y 4.")
