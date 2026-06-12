
import webbrowser
import requests

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', False)

from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu


class MainScreen(Screen):
    pass


class DetailScreen(Screen):
    pass


class ChacoRutaV2(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        self.datos = []
        self.localidades = []
        self.combustible_actual = "Nafta_Super"
        self.estacion_seleccionada = None

        self.sm = ScreenManager()

        self.main = MainScreen(name="main")
        self.detail = DetailScreen(name="detail")

        self.crear_main()
        self.crear_detail()

        self.sm.add_widget(self.main)
        self.sm.add_widget(self.detail)

        Clock.schedule_once(self.cargar_datos, 0.5)

        return self.sm

    def crear_main(self):
        layout = MDBoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        titulo = MDLabel(
            text="CHACORUTA v2",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=50
        )

        self.lbl_estado = MDLabel(
            text="Conectando...",
            halign="center",
            size_hint_y=None,
            height=30
        )

        self.btn_localidad = MDFillRoundFlatButton(
            text="Cargando localidades...",
            pos_hint={"center_x": 0.5},
            theme_text_color="Custom",  # Permite usar un color personalizado
            text_color=(0, 0, 0, 1)
        )
        self.btn_localidad.bind(on_release=self.abrir_menu_localidades)

        fila1 = MDBoxLayout(size_hint_y=None, height=50, spacing=15)

        btn_p2 = MDFillRoundFlatButton(
                text="SUPER",
                on_release=lambda x: self.buscar("Nafta_Super"),
                theme_text_color="Custom",  # Permite usar un color personalizado
                text_color=(0, 0, 0, 1), 
            )
        btn_p2.md_bg_color = (0.53, 0.81, 0.98, 1)
        fila1.add_widget(btn_p2)          

        btn_p1 = MDFillRoundFlatButton(
                text="PREMIUM",
                on_release=lambda x: self.buscar("Nafta_Premium"),
                theme_text_color="Custom",  # Permite usar un color personalizado
                text_color=(0, 0, 0, 1), 
            )
        btn_p1.md_bg_color = (0, 0.4, 1, 1)
        fila1.add_widget(btn_p1)    


        btn_g2 = MDFillRoundFlatButton(
          text="G2", on_release=lambda x: self.buscar("Gasoil_Grado2"),
           theme_text_color="Custom",  # Permite usar un color personalizado
            text_color=(0, 0, 0, 1), 
)

        btn_g2.md_bg_color = (1, 0.55, 0, 1)
        fila1.add_widget(btn_g2)
        btn_g3 = MDFillRoundFlatButton(
                text="G3", on_release=lambda x: self.buscar("Gasoil_Grado3"),
                theme_text_color="Custom",  # Permite usar un color personalizado
                text_color=(0, 0, 0, 1), 
            )
        btn_g3.md_bg_color = "grey"
        fila1.add_widget(btn_g3)
        self.resultados = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=5
        )

        scroll = ScrollView()
        scroll.add_widget(self.resultados)

        layout.add_widget(titulo)
        layout.add_widget(self.lbl_estado)
        layout.add_widget(self.btn_localidad)
        layout.add_widget(fila1)     
        layout.add_widget(scroll)

        self.main.add_widget(layout)

    def crear_detail(self):
        layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        self.lbl_detalle = MDLabel(
            text="",
            halign="center"
        )

        btn_mapa = MDFillRoundFlatButton(
            text="IR A LA ESTACIÓN",
            pos_hint={"center_x": 0.5},
            on_release=self.abrir_mapa
        )

        btn_volver = MDFillRoundFlatButton(
            text="VOLVER",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: setattr(self.sm, "current", "main")
        )

        layout.add_widget(self.lbl_detalle)
        layout.add_widget(btn_mapa)
        layout.add_widget(btn_volver)
        self.detail.add_widget(layout)

    def cargar_datos(self, dt):
        try:
            url = "https://datos.energia.gob.ar/api/3/action/datastore_search"
            params = {
                "resource_id": "80ac25de-a44a-4445-9215-090cf55cfda5",
                "limit": 36000
            }

            r = requests.get(url, params=params, timeout=30)
            registros = r.json()["result"]["records"]
            
            for e in registros:
                prov = str(e.get("provincia", "")).upper().strip()

                if prov != "CHACO":
                    continue
                fecha = str(e.get("fecha_vigencia", ""))[:10]

                if fecha < "2026-05-01":
                    continue
                self.datos.append({
                    "localidad": str(e.get("localidad", "")).title(),
                    "empresa": str(e.get("empresa", "")).strip(),
                    "bandera": str(e.get("empresabandera", "")).strip(),
                    "producto": str(e.get("producto", "")).strip(),
                    "precio": float(e.get("precio", 0) or 0),
                    "lat": e.get("latitud"),
                    "lon": e.get("longitud"),
                    "direccion": str(e.get("direccion", "")).strip(),
                    "fecha": fecha
                })

            self.localidades = sorted(
                list(set(x["localidad"] for x in self.datos if x["localidad"]))
            )

            self.lbl_estado.text = "Localidades"

            self.menu = MDDropdownMenu(
                caller=self.btn_localidad,
                items=[
                    {
                        "text": loc,
                        "on_release": lambda x=loc: self.seleccionar_localidad(x)
                    }
                    for loc in self.localidades[:200]
                ],
                width_mult=4
            )

            if self.localidades:
                self.seleccionar_localidad(self.localidades[0])

        except Exception as e:
            self.lbl_estado.text = f"Error: {e}"

    def abrir_menu_localidades(self, *args):
        if hasattr(self, "menu"):
            self.menu.open()

    def seleccionar_localidad(self, loc):
        self.localidad_actual = loc
        self.btn_localidad.text = loc
        if hasattr(self, "menu"):
            self.menu.dismiss()

    def buscar(self, combustible):
        self.combustible_actual = combustible
        self.resultados.clear_widgets()

        mapa = {
            "Nafta_Super": ["SÚPER"],
            "Nafta_Premium": ["PREMIUM"],
            "Gasoil_Grado2": ["GRADO 2"],
            "Gasoil_Grado3": ["GRADO 3"]
        }

        encontrados = []
# Color según combustible seleccionado
        if combustible == "Nafta_Super":
            color = (0.53, 0.81, 0.98, 1)      # celeste

        elif combustible == "Nafta_Premium":
            color = (0, 0.4, 1, 1)             # azul

        elif combustible == "Gasoil_Grado2":
            color = (1, 0.55, 0, 1)            # naranja

        elif combustible == "Gasoil_Grado3":
            color = (0.5, 0.5, 0.5, 1)         # gris

        else:
            color = (1, 0.1, 0.5, 1)
        for e in self.datos:
            if e["localidad"] != self.localidad_actual:
                continue

            if any(t in e["producto"].upper() for t in mapa[combustible]):
                encontrados.append(e)

        encontrados.sort(key=lambda x: x["precio"])

        for i, est in enumerate(encontrados, start=1):
            btn = MDFillRoundFlatButton(
                text=f"{i}) {est['bandera']}  ${est['precio']:.2f}",
                size_hint_y=None,
                height=45,
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1)
            )
            btn.md_bg_color = color
            btn.bind(on_release=lambda x, d=est: self.ver_detalle(d))
            self.resultados.add_widget(btn)

    def ver_detalle(self, estacion):
        
        self.estacion_seleccionada = estacion

        self.lbl_detalle.text = (
            f"Bandera: {estacion['bandera']}\n\n"
            f"Empresa: {estacion['empresa']}\n\n"
            f"Precio: ${estacion['precio']:.2f}\n\n"
            f"Localidad: {estacion['localidad']}"
        )

        self.sm.current = "detail"

    def abrir_mapa(self, *args):
        if not self.estacion_seleccionada:
            return

        lat = self.estacion_seleccionada["lat"]
        lon = self.estacion_seleccionada["lon"]

        if lat and lon:
            webbrowser.open(
                f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            )


if __name__ == "__main__":
    ChacoRutaV2().run()
