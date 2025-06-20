import json
import yaml
import requests
import uuid
from typing import List, Dict, Optional, Any

# Floodlight controller configuration
CONTROLLER_IP = "192.168.200.200"
CONTROLLER_PORT = 8080
CONTROLLER_URL = f"http://{CONTROLLER_IP}:{CONTROLLER_PORT}"

class Alumno:
    """Clase para representar un alumno"""
    def __init__(self, nombre: str, codigo: int, mac: str):
        self.nombre = nombre
        self.codigo = codigo
        self.mac = mac

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'codigo': self.codigo,
            'mac': self.mac
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['nombre'], int(data['codigo']), data['mac'])


class Servicio:
    def __init__(self, nombre: str, protocolo: str, puerto: int):
        self.nombre = nombre
        self.protocolo = protocolo
        self.puerto = puerto

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'protocolo': self.protocolo,
            'puerto': self.puerto
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['nombre'], data['protocolo'], data['puerto'])

class Servidor:
    def __init__(self, nombre: str, ip: str, servicios: list[Servicio]):
        self.nombre = nombre
        self.ip = ip
        self.servicios = servicios

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'ip': self.ip,
            'servicios': [s.to_dict() for s in self.servicios]
        }

    @classmethod
    def from_dict(cls, data):
        servicios = [Servicio.from_dict(s) for s in data['servicios']]
        return cls(data['nombre'], data['ip'], servicios)
    

class Curso:
    def __init__(self, codigo: str, estado: str, nombre: str, alumnos: list[str], servidores: list[dict]):
        self.codigo = codigo
        self.estado = estado
        self.nombre = nombre
        self.alumnos = alumnos
        self.servidores = servidores  # lista de dicts

    def to_dict(self):
        return {
            'codigo': self.codigo,
            'estado': self.estado,
            'nombre': self.nombre,
            'alumnos': self.alumnos,
            'servidores': self.servidores
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['codigo'], data['estado'], data['nombre'], data.get('alumnos', []), data.get('servidores', []))


def importar_yaml(nombre_archivo):
    global alumnos, cursos, servidores
    with open(nombre_archivo, 'r') as f:
        data = yaml.safe_load(f)

    alumnos = [Alumno.from_dict(a) for a in data.get('alumnos', [])]
    cursos = [Curso.from_dict(c) for c in data.get('cursos', [])]
    servidores = [Servidor.from_dict(s) for s in data.get('servidores', [])]

def exportar_yaml(nombre_archivo, alumnos, cursos, servidores):
    data = {
        'alumnos': [a.to_dict() for a in alumnos],
        'cursos': [c.to_dict() for c in cursos],
        'servidores': [s.to_dict() for s in servidores]
    }
    with open(nombre_archivo, 'w') as f:
        yaml.dump(data, f)


#opcion 3 menu cursos
def menu_cursos():
    global cursos, alumnos

    while True:
        print("\n--- MENÚ CURSOS ---")
        print("1) Listar cursos")
        print("2) Mostrar detalle de un curso")
        print("3) Actualizar curso (agregar/eliminar alumno)")
        print("0) Volver")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            print("\n--- Lista de cursos ---")
            for c in cursos:
                print(f"- {c.codigo}: {c.nombre} [{c.estado}]")

        elif opcion == '2':
            codigo = input("Ingrese el código del curso: ").strip()
            curso = next((c for c in cursos if c.codigo == codigo), None)
            if curso:
                print(f"\nCurso: {curso.nombre}")
                print(f"Estado: {curso.estado}")
                print("Alumnos:")
                for cod in curso.alumnos:
                    alumno = next((a for a in alumnos if a.codigo == cod), None)
                    if alumno:
                        print(f"  - {alumno.nombre} ({alumno.codigo})")
                print("Servidores:")
                for s in curso.servidores:
                    print(f"  - {s['nombre']}: servicios {', '.join(s['servicios_permitidos'])}")
            else:
                print("Curso no encontrado.")

        elif opcion == '3':
            codigo = input("Ingrese el código del curso a modificar: ").strip()
            curso = next((c for c in cursos if c.codigo == codigo), None)
            if not curso:
                print("Curso no encontrado.")
                continue

            print("1) Agregar alumno")
            print("2) Eliminar alumno")
            accion = input("Seleccione acción: ").strip()

            if accion == '1':
                cod_alumno_str = input("Código del alumno a agregar: ").strip()
                try:
                    cod_alumno = int(cod_alumno_str)
                except ValueError:
                    print("El código debe ser un número.")
                    continue

                if cod_alumno in curso.alumnos:
                    print("El alumno ya está en el curso.")
                elif any(a.codigo == cod_alumno for a in alumnos):
                    curso.alumnos.append(cod_alumno)
                    print("Alumno agregado.")
                else:
                    print("Alumno no registrado en el sistema.")
            elif accion == '2':
                cod_alumno_str = input("Código del alumno a eliminar: ").strip()
                try:
                    cod_alumno = int(cod_alumno_str)
                except ValueError:
                    print("El código debe ser un número.")
                    continue

                if cod_alumno in curso.alumnos:
                    curso.alumnos.remove(cod_alumno)
                    print("Alumno eliminado.")
                else:
                    print("El alumno no está en este curso.")
            else:
                print("Opción inválida.")
        
        elif opcion == '0':
            break
        else:
            print("Opción inválida.")

#opcion 4 menu alumnos
def menu_alumnos():
    global alumnos, cursos

    while True:
        print("\n--- MENU ALUMNOS ---")
        print("1) Crear")
        print("2) Listar")
        print("3) Mostrar detalle")
        print("4) Actualizar")
        print("5) Borrar")
        print("0) Volver")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            print("\n--- Crear nuevo alumno ---")
            codigo_str = input("Código PUCP: ").strip()
            try:
                codigo = int(codigo_str)
            except ValueError:
                print("El código debe ser un número.")
                continue
            if any(a.codigo == codigo for a in alumnos):
                print("Ya existe un alumno con ese código.")
                continue
            nombre = input("Nombre completo: ").strip()
            mac = input("Dirección MAC (ej. 44:11:22:44:A7:2A): ").strip()
            nuevo = Alumno(nombre, codigo, mac)
            alumnos.append(nuevo)
            print("Alumno creado exitosamente.")

        elif opcion == '2':
            print("\n--- Lista de alumnos ---")
            for a in alumnos:
                print(f"- {a.codigo} | {a.nombre} | {a.mac}")

        elif opcion == '3':
            try:
                codigo = int(input("Ingrese el código del alumno: ").strip())
            except ValueError:
                print("Código inválido. Debe ser un número.")
                continue

            alumno = next((a for a in alumnos if a.codigo == codigo), None)
            if alumno:
                print(f"\nDetalles del alumno:")
                print(f"- Código : {alumno.codigo}")
                print(f"- Nombre : {alumno.nombre}")
                print(f"- MAC    : {alumno.mac}")
            else:
                print("Alumno no encontrado.")

        elif opcion == '4':
            codigo = input("Ingrese el código del alumno a actualizar: ").strip()
            alumno = next((a for a in alumnos if a.codigo == codigo), None)
            if alumno:
                nuevo_nombre = input(f"Nuevo nombre (enter para mantener '{alumno.nombre}'): ").strip()
                nueva_mac = input(f"Nueva MAC (enter para mantener '{alumno.mac}'): ").strip()
                if nuevo_nombre:
                    alumno.nombre = nuevo_nombre
                if nueva_mac:
                    alumno.mac = nueva_mac
                print("Alumno actualizado.")
            else:
                print("Alumno no encontrado.")

        elif opcion == '5':
            codigo = input("Ingrese el código del alumno a eliminar: ").strip()
            alumno = next((a for a in alumnos if a.codigo == codigo), None)
            if alumno:
                confirm = input(f"¿Está seguro de eliminar al alumno {alumno.nombre}? (s/n): ").lower()
                if confirm == 's':
                    alumnos = [a for a in alumnos if a.codigo != codigo]
                    # Además, eliminarlo de todos los cursos
                    for c in cursos:
                        if codigo in c.alumnos:
                            c.alumnos.remove(codigo)
                    print("Alumno eliminado de la lista y de todos los cursos.")
            else:
                print("Alumno no encontrado.")

        elif opcion == '0':
            break

        else:
            print("Opción inválida.")



#opcion 5 menu servidores
def menu_servidores():
    global servidores

    while True:
        print("\n--- MENÚ SERVIDORES Y SERVICIOS ---")
        print("1) Listar servidores")
        print("2) Mostrar detalle de un servidor")
        print("0) Volver")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            print("\n--- Lista de servidores ---")
            for s in servidores:
                print(f"- {s.nombre} | IP: {s.ip}")

        elif opcion == '2':
            nombre = input("Ingrese el nombre del servidor: ").strip()
            servidor = next((s for s in servidores if s.nombre.lower() == nombre.lower()), None)
            if servidor:
                print(f"\nServidor: {servidor.nombre}")
                print(f"IP: {servidor.ip}")
                print("Servicios brindados:")
                for serv in servidor.servicios:
                    print(f"  - {serv.nombre} | Protocolo: {serv.protocolo} | Puerto: {serv.puerto}")
            else:
                print("Servidor no encontrado.")

        elif opcion == '0':
            break
        else:
            print("Opción inválida.")



def menu_principal():
    while True:
        print("\n--- MENÚ SDN ---")
        print("1. Importar")
        print("2. Exportar")
        print("3. Cursos")
        print("4. Alumnos")
        print("5. Servidores")
        print("6. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            archivo = input("Nombre de archivo a importar: ")
            importar_yaml(archivo)
            print(f"Importados {len(alumnos)} alumnos, {len(cursos)} cursos y {len(servidores)} servidores.")
        elif opcion == '2':
            archivo = input("Nombre de archivo para exportar: ")
            exportar_yaml(archivo, alumnos, cursos, servidores)
            print("Archivo exportado correctamente.")
        elif opcion == '3':
            menu_cursos()
        elif opcion == '4':
            menu_alumnos()
        elif opcion == '5':
            menu_servidores()
        elif opcion == '6':
            print("Cerrando programa.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu_principal()