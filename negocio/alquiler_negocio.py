from datetime import date, datetime
from datos.mongo_dao import ClienteDAO
from entidades.modelos import Alquiler, Devolucion, Danio
from datos.sql_dao import AlquilerDAO, DevolucionDAO, DanioDAO
from datos.vehiculo_dao import VehiculoDAO

TASA_IMPUESTO       = 0.13
TASA_INTERES_ATRASO = 0.15
SEGURO_DIARIO       = 3500.0

## Lógica de negocio para alquileres
class AlquilerNegocio:

    def __init__(self):
        self._dao          = AlquilerDAO()
        self._vehiculo_dao = VehiculoDAO()
        self._cliente_dao   = ClienteDAO()

    def calcular_dias(self, fecha_inicio, fecha_fin):
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        return max((fecha_fin - fecha_inicio).days, 1)

    def calcular_costo(self, costo_diario, cantidad_dias):
        costo_base   = round(costo_diario * cantidad_dias, 2)
        impuesto     = round(costo_base * TASA_IMPUESTO, 2)
        costo_seguro = round(SEGURO_DIARIO * cantidad_dias, 2)
        total        = round(costo_base + impuesto + costo_seguro, 2)
        return {
            "costo_diario":  costo_diario,
            "cantidad_dias": cantidad_dias,
            "costo_base":    costo_base,
            "impuesto":      impuesto,
            "seguro_diario": SEGURO_DIARIO,
            "costo_seguro":  costo_seguro,
            "total":         total,
        }

    def registrar_alquiler(self, id_cliente, id_vehiculo, fecha_inicio, fecha_fin, es_funcionario=False):
        hoy = date.today()
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

        cliente = self._cliente_dao.buscar_por_id(id_cliente)
        if not cliente:
            raise ValueError("El cliente no existe.")
        if not cliente.activo:
            raise ValueError("El cliente está inactivo y no puede alquilar.")
        if not cliente.es_mayor_de_edad(18):
            raise ValueError("El cliente debe ser mayor de 18 años para alquilar.")

        if fecha_inicio < hoy:
            raise ValueError("La fecha de inicio no puede ser anterior a hoy.")
        if fecha_fin < fecha_inicio:
            raise ValueError("La fecha de devolución no puede ser anterior al inicio.")
        if self._dao.vehiculo_tiene_alquiler_activo(id_vehiculo):
            raise ValueError("El vehículo ya tiene un alquiler activo.")
        if self._dao.vehiculo_tiene_reserva_en_fechas(id_vehiculo, fecha_inicio, fecha_fin):
            raise ValueError("El vehículo ya tiene reserva para ese rango de fechas.")

        vehiculo = self._vehiculo_dao.buscar_por_placa(id_vehiculo)
        if not vehiculo or not vehiculo.disponible:
            raise ValueError("El vehículo no está disponible.")

        cantidad_dias = self.calcular_dias(fecha_inicio, fecha_fin)
        calculo       = self.calcular_costo(vehiculo.costo_diario, cantidad_dias)

        ## Si el funcionario registra el alquiler el cliente está presente, pasa directo a En préstamo
        estado_inicial = "En préstamo" if es_funcionario else "Pendiente"

        alquiler = Alquiler(
            id_cliente=id_cliente,
            id_vehiculo=id_vehiculo,
            fecha_inicio=fecha_inicio,
            fecha_devolucion_planificada=fecha_fin,
            cantidad_dias=calculo["cantidad_dias"],
            costo_diario=calculo["costo_diario"],
            costo_base=calculo["costo_base"],
            impuesto=calculo["impuesto"],
            seguro_diario=calculo["seguro_diario"],
            costo_seguro=calculo["costo_seguro"],
            total=calculo["total"],
            estado=estado_inicial,
        )
        id_alquiler = self._dao.insertar(alquiler)
        self._vehiculo_dao.actualizar_disponibilidad(id_vehiculo, False)
        return id_alquiler

    def activar_alquiler(self, id_alquiler):
        ## Cambia el estado de Pendiente a En préstamo
        self._dao.actualizar_estado(id_alquiler, "En préstamo")

    def cancelar_alquiler(self, id_alquiler):
        ## Cancela el alquiler y libera el vehículo en MongoDB
        alquiler = self._dao.buscar_por_id(id_alquiler)
        if not alquiler:
            raise ValueError("No se encontró el alquiler indicado.")
        if alquiler.estado != "Pendiente":
            raise ValueError("Solo se pueden cancelar alquileres en estado 'Pendiente'.")
        self._dao.actualizar_estado(id_alquiler, "Cancelado")
        self._vehiculo_dao.actualizar_disponibilidad(alquiler.id_vehiculo, True)

    def obtener_alquileres_por_periodo(self, fecha_inicio, fecha_fin):
        return self._dao.obtener_alquileres_por_periodo(fecha_inicio, fecha_fin)

    def obtener_pendientes_en_prestamo(self):
        return self._dao.obtener_pendientes_en_prestamo()

    def obtener_historial_cliente(self, id_cliente):
        return self._dao.obtener_por_cliente(id_cliente)

    def obtener_todos(self):
        return self._dao.obtener_todos()

    def buscar_por_id(self, id_alquiler):
        return self._dao.buscar_por_id(id_alquiler)


## Lógica de negocio para devoluciones
class DevolucionNegocio:

    def __init__(self):
        self._dao_dev = DevolucionDAO()
        self._dao_dan = DanioDAO()
        self._dao_alq = AlquilerDAO()
        self._dao_veh = VehiculoDAO()

    def calcular_devolucion(self, alquiler, fecha_real):
        if isinstance(fecha_real, str):
            fecha_real = datetime.strptime(fecha_real, "%Y-%m-%d").date()
        planificada = alquiler.fecha_devolucion_planificada
        if isinstance(planificada, str):
            planificada = datetime.strptime(planificada, "%Y-%m-%d").date()

        dias_atraso        = max((fecha_real - planificada).days, 0)
        monto_penalizacion = 0.0

        if dias_atraso > 0:
            costo_dias_extra   = alquiler.costo_diario * dias_atraso
            interes            = costo_dias_extra * TASA_INTERES_ATRASO
            impuesto_extra     = costo_dias_extra * TASA_IMPUESTO
            seguro_extra       = SEGURO_DIARIO * dias_atraso
            monto_penalizacion = round(costo_dias_extra + interes + impuesto_extra + seguro_extra, 2)

        return {
            "dias_atraso":        dias_atraso,
            "monto_penalizacion": monto_penalizacion,
        }

    def registrar_devolucion(self, alquiler, fecha_real, lista_danios):
        if isinstance(fecha_real, str):
            fecha_real = datetime.strptime(fecha_real, "%Y-%m-%d").date()

        calculo      = self.calcular_devolucion(alquiler, fecha_real)
        costo_danios = sum(d["costo"] for d in lista_danios)
        tiene_danio  = len(lista_danios) > 0
        total_dev    = round(calculo["monto_penalizacion"] + costo_danios, 2)

        devolucion = Devolucion(
            id_alquiler=alquiler.id_alquiler,
            fecha_devolucion_real=fecha_real,
            dias_atraso=calculo["dias_atraso"],
            monto_penalizacion=calculo["monto_penalizacion"],
            tiene_danio=tiene_danio,
            total_devolucion=total_dev,
        )
        id_devolucion = self._dao_dev.insertar(devolucion)

        for item in lista_danios:
            danio = Danio(id_devolucion=id_devolucion,
                          descripcion=item["descripcion"],
                          costo_danio=item["costo"])
            self._dao_dan.insertar(danio)

        self._dao_alq.actualizar_estado(alquiler.id_alquiler, "Devuelto")
        self._dao_veh.actualizar_disponibilidad(alquiler.id_vehiculo, True)

        return id_devolucion, total_dev