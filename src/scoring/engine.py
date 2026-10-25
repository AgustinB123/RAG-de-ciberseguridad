class ScoringEngine:
    def __init__(self):
        self.temas = {
            "gobernanza": False, "inventario": False, "proteccion": False,
            "deteccion": False, "respuesta": False, "respaldos": False,
            "capacitacion": False, "proveedores": False
        }
        self.total_temas = len(self.temas)

    def actualizar_progreso(self, tema, es_util):
        tema = str(tema).lower().strip()
        if "gobern" in tema: tema = "gobernanza"
        if "invent" in tema: tema = "inventario"
        if "protec" in tema: tema = "proteccion"
        if "detec" in tema: tema = "deteccion"
        if "respue" in tema: tema = "respuesta"
        if "backup" in tema or "respald" in tema: tema = "respaldos"
        if "capacit" in tema: tema = "capacitacion"
        if "provee" in tema or "tercero" in tema: tema = "proveedores"
        
        if tema in self.temas and es_util:
            self.temas[tema] = True

    def obtener_porcentaje(self):
        cubiertos = sum(1 for estado in self.temas.values() if estado)
        return int((cubiertos / self.total_temas) * 100)

    def obtener_temas_pendientes(self):
        return [tema for tema, estado in self.temas.items() if not estado]

    def esta_completo(self):
        return all(self.temas.values())