from datetime import datetime

class CajeroAutomatico:
    def __init__(self):
        self.usuarios = {}

    def cargar_usuarios(self):
        try:
            with open("usuarios.txt", "r") as file:
                usuario_actual = None
                for line in file:
                    if line.strip() == '---':  # Separador entre usuarios
                        usuario_actual = None
                    else:
                        if usuario_actual is None:
                            datos = line.strip().split(",")
                            if len(datos) >= 5:
                                nombre = datos[1]
                                self.usuarios[nombre] = {
                                    "dni": datos[0],
                                    "correo": datos[2],
                                    "clave": datos[3],
                                    "saldo": float(datos[4]),
                                    "movimientos": []
                                }
                                usuario_actual = nombre
                        else:
                            partes_movimiento = line.strip().split(":")
                            if len(partes_movimiento) == 2:
                                fecha = datetime.strptime(partes_movimiento[0], "%Y-%m-%d %H:%M:%S")
                                descripcion = partes_movimiento[1]
                                self.usuarios[usuario_actual]["movimientos"].append((fecha, descripcion))
                            else:
                                print(f"Formato incorrecto para movimiento: {line}. Se omitirá.")
        except FileNotFoundError:
            print("El archivo 'usuarios.txt' no existe. Creando nuevo archivo...")
            open("usuarios.txt", "w").close()

    def guardar_usuarios(self):
        with open("usuarios.txt", "w") as file:
            for nombre, datos in self.usuarios.items():
                movimientos = "\n".join([f"{fecha.strftime('%Y-%m-%d %H:%M:%S')}:{descripcion}" for fecha, descripcion in datos["movimientos"]])
                linea = f"{datos['dni']},{nombre},{datos['correo']},{datos['clave']},{datos['saldo']}\n{movimientos}\n"
                file.write(linea)
                file.write("---\n")  # Separador entre usuarios

    def validar_dni(self, dni):
        return dni.isdigit() and len(dni) >= 10

    def validar_correo(self, correo):
        partes = correo.split("@")
        if len(partes) != 2:
            return False
        username, dominio = partes
        if not username or not dominio:
            return False
        if not username.replace(".", "").isalnum():
            return False
        if not dominio.endswith(".com"):
            return False
        if not dominio[:-4].replace(".", "").isalnum():
            return False
        return True

    def validar_nombre_usuario(self, nombre):
        return all(caracter.isalpha() or caracter.isdigit() for caracter in nombre)

    def registrar_usuario(self):
        print("Registro de Usuario")
        while True:
            try:
                dni = input("Ingrese su número de identificación (DNI): ").strip()
                if not dni:
                    raise ValueError("Debe ingresar un valor para el DNI.")
                if not self.validar_dni(dni):
                    raise ValueError("El DNI debe contener al menos 10 números.")

                nombre_valido = False
                while not nombre_valido:
                    nombre = input("Ingrese su nombre de usuario: ").strip()
                    if not nombre:
                        print("Debe ingresar un valor para el nombre de usuario.")
                    elif nombre in self.usuarios:
                        print("El nombre de usuario ya está en uso. Intente con otro.")
                    elif not self.validar_nombre_usuario(nombre):
                        print("El nombre de usuario solo puede contener letras y, opcionalmente, números.")
                    else:
                        nombre_valido = True

                correo_valido = False
                while not correo_valido:
                    correo = input("Ingrese su dirección de correo electrónico: ").strip()
                    if not correo:
                        print("Debe ingresar un valor para el correo electrónico.")
                    elif not self.validar_correo(correo):
                        print("La dirección de correo electrónico no es válida. Inténtelo nuevamente.")
                    else:
                        correo_valido = True

                clave_valida = False
                while not clave_valida:
                    clave = input("Ingrese su clave: ").strip()
                    if not clave:
                        print("Debe ingresar un valor para la clave.")
                    else:
                        clave_repetida = input("Vuelva a ingresar su clave: ").strip()
                        if not clave_repetida:
                            print("Debe ingresar un valor para la clave repetida.")
                        elif clave == clave_repetida:
                            clave_valida = True
                        else:
                            print("Las claves no coinciden. Inténtelo nuevamente.")

                print("\nRegistro completado:")
                print(f"DNI: {dni}")
                print(f"Nombre de usuario: {nombre}")
                print(f"Correo electrónico: {correo}")
                print(f"Saldo inicial: $0")
                guardar = input("¿Desea guardar este registro? (Sí/No): ").strip().lower()
                if guardar == "si":
                    self.usuarios[nombre] = {
                        "dni": dni,
                        "correo": correo,
                        "clave": clave,
                        "saldo": 0,
                        "movimientos": []
                    }
                    self.guardar_usuarios()
                    print("¡Registro guardado exitosamente!")
                else:
                    print("Registro descartado.")

                return

            except ValueError as e:
                print(f"Error: {e}")

    def iniciar_sesion(self):
        print("\nInicio de Sesión")
        while True:
            nombre_usuario = input("Ingrese su nombre de usuario: ").strip()
            if not nombre_usuario:
                print("Debe ingresar un nombre de usuario.")
                continue

            if nombre_usuario not in self.usuarios:
                print("El usuario no existe.")
                opcion = input("¿Desea registrarse automáticamente? (Sí/No): ").strip().lower()
                if opcion == "si":
                    self.registrar_usuario()
                elif opcion == "no":
                    continue
                else:
                    print("Opción no válida. Por favor, responda 'Sí' o 'No'.")
                    continue
            else:
                intentos_clave = 3
                while intentos_clave > 0:
                    clave = input("Ingrese su clave: ").strip()
                    if not clave:
                        print("Debe ingresar una clave.")
                        continue

                    if self.usuarios[nombre_usuario]["clave"] == clave:
                        print("Inicio de sesión exitoso.")
                        return nombre_usuario
                    else:
                        intentos_clave -= 1
                        print(f"Clave incorrecta. Intentos restantes: {intentos_clave}")
                        if intentos_clave == 0:
                            print("Cuenta bloqueada por 24 horas. Comuníquese con su banco.")
                        break

    def retirar(self, nombre_usuario, monto):
        saldo_actual = self.usuarios[nombre_usuario]["saldo"]
        if monto <= 0:
            print("El monto a retirar debe ser mayor que cero.")
        elif monto > saldo_actual:
            print("Fondos insuficientes para realizar la transacción.")
        else:
            self.usuarios[nombre_usuario]["saldo"] -= monto
            self.usuarios[nombre_usuario]["movimientos"].append((datetime.now(), f"Retiro de {monto}"))
            self.guardar_usuarios()
            print(f"Retiro exitoso. Saldo actual: ${self.usuarios[nombre_usuario]['saldo']}")

    def consultar_saldo(self, nombre_usuario):
        saldo_actual = self.usuarios[nombre_usuario]["saldo"]
        print(f"Su saldo actual es: ${saldo_actual}")

    def consignar(self, nombre_usuario, monto):
        if monto <= 0:
            print("El monto a consignar debe ser mayor que cero.")
        else:
            self.usuarios[nombre_usuario]["saldo"] += monto
            self.usuarios[nombre_usuario]["movimientos"].append((datetime.now(), f"Consignación de {monto}"))
            self.guardar_usuarios()
            print(f"Consignación exitosa. Saldo actual: ${self.usuarios[nombre_usuario]['saldo']}")

    def consultar_movimientos(self, nombre_usuario):
        movimientos = self.usuarios[nombre_usuario]["movimientos"]
        if movimientos:
            print("Movimientos:")
            for fecha, descripcion in movimientos:
                print(f"{fecha}: {descripcion}")
        else:
            print("No hay movimientos disponibles.")

if __name__ == "__main__":
    cajero = CajeroAutomatico()
    cajero.cargar_usuarios()

    while True:
        print("\n¡Bienvenido al Cajero Automático!")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip().lower()

        if opcion == "1" or opcion == "r":
            cajero.registrar_usuario()
        elif opcion == "2" or opcion == "i":
            nombre_usuario = cajero.iniciar_sesion()
            if nombre_usuario:
                while True:
                    print("\nOperaciones disponibles:")
                    print("1. Retirar")
                    print("2. Consignar")
                    print("3. Consultar Saldo")
                    print("4. Consultar Movimientos")
                    print("5. Salir")
                    opcion_operacion = input("Seleccione una opción: ").strip()
                    if opcion_operacion == "1":
                        monto = float(input("Ingrese el monto a retirar: "))
                        cajero.retirar(nombre_usuario, monto)
                    elif opcion_operacion == "2":
                        monto = float(input("Ingrese el monto a consignar: "))
                        cajero.consignar(nombre_usuario, monto)
                    elif opcion_operacion == "3":
                        cajero.consultar_saldo(nombre_usuario)
                    elif opcion_operacion == "4":
                        cajero.consultar_movimientos(nombre_usuario)
                    elif opcion_operacion == "5":
                        print("¡Hasta luego!")
                        break
                    else:
                        print("Opción no válida. Por favor, seleccione una opción válida.")
        elif opcion == "3" or opcion == "s":
            print("Gracias por usar el Cajero Automático. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")
