import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import serial
import threading
import queue
from datetime import datetime
import re

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Monitoreo Inteligente",
    page_icon="",
    layout="wide"
)

# Título principal
st.title("Sistema de Monitoreo Inteligente - EEST N14")
st.markdown("---")

class LectorArduino:
    """Clase para leer datos del ESP32 por puerto serial"""
    
    def __init__(self, puerto=''COM7'', baudrate=115200):
        self.puerto = puerto
        self.baudrate = baudrate
        self.serial_conn = None
        self.datos_actuales = {
            ''temperatura'': 0,
            ''humedad_aire'': 0,
            ''suelo1'': 0,
            ''suelo2'': 0,
            ''suelo3'': 0,
            ''suelo4'': 0,
            ''motor_a'': ''APAGADO'',
            ''motor_b'': ''APAGADO'',
            ''timestamp'': datetime.now()
        }
        self.historial = []
        self.conectado = False
        
    def conectar(self):
        """Conectar al puerto serial"""
        try:
            self.serial_conn = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                timeout=1
            )
            time.sleep(2)  # Esperar a que se establezca la conexión
            self.conectado = True
            st.success(f" Conectado al ESP32 en {self.puerto}")
            return True
        except Exception as e:
            st.error(f" Error conectando a {self.puerto}: {e}")
            return False
    
    def desconectar(self):
        """Desconectar del puerto serial"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.conectado = False
    
    def parsear_datos(self, linea):
        """Parsear los datos recibidos del Arduino"""
        try:
            datos = self.datos_actuales.copy()
            
            # Buscar patrones en los datos
            if "Temperatura:" in linea:
                temp_match = re.search(r"Temperatura:\s*([\d.]+)", linea)
                if temp_match:
                    datos[''temperatura''] = float(temp_match.group(1))
            
            if "Humedad:" in linea:
                hum_match = re.search(r"Humedad:\s*([\d.]+)", linea)
                if hum_match:
                    datos[''humedad_aire''] = float(hum_match.group(1))
            
            if "Suelo 1:" in linea:
                s1_match = re.search(r"Suelo 1:\s*(\d+)", linea)
                if s1_match:
                    datos[''suelo1''] = int(s1_match.group(1))
            
            if "Suelo 2:" in linea:
                s2_match = re.search(r"Suelo 2:\s*(\d+)", linea)
                if s2_match:
                    datos[''suelo2''] = int(s2_match.group(1))
            
            if "Suelo 3:" in linea:
                s3_match = re.search(r"Suelo 3:\s*(\d+)", linea)
                if s3_match:
                    datos[''suelo3''] = int(s3_match.group(1))
            
            if "Suelo 4:" in linea:
                s4_match = re.search(r"Suelo 4:\s*(\d+)", linea)
                if s4_match:
                    datos[''suelo4''] = int(s4_match.group(1))
            
            if "Motor A:" in linea:
                motor_a_match = re.search(r"Motor A:\s*(\w+)", linea)
                if motor_a_match:
                    datos[''motor_a''] = motor_a_match.group(1)
            
            if "Motor B:" in linea:
                motor_b_match = re.search(r"Motor B:\s*(\w+)", linea)
                if motor_b_match:
                    datos[''motor_b''] = motor_b_match.group(1)
            
            datos[''timestamp''] = datetime.now()
            return datos
            
        except Exception as e:
            st.warning(f" Error parseando datos: {e}")
            return None
    
    def leer_datos(self):
        """Leer datos del puerto serial"""
        if not self.conectado or not self.serial_conn:
            return None
        
        try:
            if self.serial_conn.in_waiting > 0:
                linea = self.serial_conn.readline().decode(''utf-8'').strip()
                if linea and "===" in linea:  # Ignorar líneas separadoras
                    return None
                
                datos = self.parsear_datos(linea)
                if datos:
                    self.datos_actuales = datos
                    # Guardar en historial (mantener últimos 100 registros)
                    self.historial.append(datos.copy())
                    if len(self.historial) > 100:
                        self.historial.pop(0)
                
                return datos
        except Exception as e:
            st.error(f" Error leyendo datos: {e}")
            return None
        
        return None

# Inicializar el lector de Arduino
if ''lector'' not in st.session_state:
    st.session_state.lector = LectorArduino(''COM7'', 115200)

# Sidebar para configuración
with st.sidebar:
    st.header(" Configuración")
    
    if st.button(" Conectar al ESP32"):
        if st.session_state.lector.conectar():
            st.rerun()
    
    if st.button(" Desconectar"):
        st.session_state.lector.desconectar()
        st.rerun()
    
    st.markdown("---")
    st.subheader("Umbrales de Control")
    
    umbral_humedad = st.slider(
        "Umbral Humedad Suelo",
        min_value=500,
        max_value=2500,
        value=1500,
        help="Valor mayor = más seco (activar riego)"
    )
    
    umbral_temperatura = st.slider(
        "Umbral Temperatura Alta",
        min_value=25,
        max_value=40,
        value=30,
        help="Temperatura para activar ventilación"
    )
    
    st.markdown("---")
    st.info("**Estado de conexión:** " + 
           (" Conectado" if st.session_state.lector.conectado else " Desconectado"))

# Leer datos actuales
datos_actuales = st.session_state.lector.datos_actuales

# Mostrar métricas principales en la parte superior
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label=" Temperatura",
        value=f"{datos_actuales[''temperatura'']}C",
        delta=None,
        delta_color="normal"
    )

with col2:
    st.metric(
        label=" Humedad Aire",
        value=f"{datos_actuales[''humedad_aire'']}%",
        delta=None
    )

with col3:
    # Calcular humedad promedio del suelo (invertir lógica: mayor valor = más seco)
    humedad_promedio = (datos_actuales[''suelo1''] + datos_actuales[''suelo2''] + 
                       datos_actuales[''suelo3''] + datos_actuales[''suelo4'']) / 4
    estado_suelo = " Húmedo" if humedad_promedio < umbral_humedad else " Seco"
    st.metric(
        label=" Estado Suelo",
        value=estado_suelo,
        delta=None
    )

with col4:
    motores_activos = sum([1 for motor in [datos_actuales[''motor_a''], datos_actuales[''motor_b'']] 
                          if motor == ''ACTIVO''])
    st.metric(
        label=" Motores Activos",
        value=f"{motores_activos}/2",
        delta=None
    )

st.markdown("---")

# Columnas para datos detallados
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(" Sensores de Suelo")
    
    # Crear gráfico de barras para sensores de suelo
    fig_suelo = go.Figure()
    
    sensores_suelo = [''Suelo 1'', ''Suelo 2'', ''Suelo 3'', ''Suelo 4'']
    valores_suelo = [datos_actuales[''suelo1''], datos_actuales[''suelo2''], 
                    datos_actuales[''suelo3''], datos_actuales[''suelo4'']]
    
    colores = []
    for valor in valores_suelo:
        if valor < umbral_humedad:
            colores.append(''green'')  # Húmedo
        else:
            colores.append(''red'')    # Seco
    
    fig_suelo.add_trace(go.Bar(
        x=sensores_suelo,
        y=valores_suelo,
        marker_color=colores,
        text=valores_suelo,
        textposition=''auto'',
    ))
    
    fig_suelo.add_hline(
        y=umbral_humedad, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Umbral: {umbral_humedad}",
        annotation_position="top right"
    )
    
    fig_suelo.update_layout(
        title="Humedad del Suelo (Mayor = Más Seco)",
        yaxis_title="Valor del Sensor",
        showlegend=False,
        height=300
    )
    
    st.plotly_chart(fig_suelo, use_container_width=True)
    
    # Mostrar valores numéricos
    cols_suelo = st.columns(4)
    for i, (sensor, valor) in enumerate(zip(sensores_suelo, valores_suelo)):
        with cols_suelo[i]:
            estado = " Húmedo" if valor < umbral_humedad else " Seco"
            st.metric(
                label=sensor,
                value=valor,
                delta=estado,
                delta_color="normal" if valor < umbral_humedad else "inverse"
            )

with col_right:
    st.subheader(" Estado de Motores")
    
    # Estado de motores
    col_motor1, col_motor2 = st.columns(2)
    
    with col_motor1:
        st.write("**Motor A**")
        if datos_actuales[''motor_a''] == ''ACTIVO'':
            st.success(" ACTIVO")
            st.write("**Sensores:** 1 y 2")
            st.write(f"**S1:** {datos_actuales[''suelo1'']} | **S2:** {datos_actuales[''suelo2'']}")
        else:
            st.error(" APAGADO")
    
    with col_motor2:
        st.write("**Motor B**")
        if datos_actuales[''motor_b''] == ''ACTIVO'':
            st.success(" ACTIVO")
            st.write("**Sensores:** 3 y 4")
            st.write(f"**S3:** {datos_actuales[''suelo3'']} | **S4:** {datos_actuales[''suelo4'']}")
        else:
            st.error(" APAGADO")
    
    # Gráfico de medidor de temperatura separado
    st.subheader(" Temperatura Actual")
    
    fig_medidor = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=datos_actuales[''temperatura''],
        domain={''x'': [0, 1], ''y'': [0, 1]},
        title={''text'': "Temperatura (C)"},
        gauge={
            ''axis'': {''range'': [None, 40]},
            ''bar'': {''color'': "darkblue"},
            ''steps'': [
                {''range'': [0, 25], ''color'': "lightblue"},
                {''range'': [25, 30], ''color'': "yellow"},
                {''range'': [30, 40], ''color'': "red"}
            ],
            ''threshold'': {
                ''line'': {''color'': "red", ''width'': 4},
                ''thickness'': 0.75,
                ''value'': umbral_temperatura
            }
        }
    ))
    
    fig_medidor.update_layout(
        height=300,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    st.plotly_chart(fig_medidor, use_container_width=True)

# Sección inferior para histórico
st.markdown("---")
st.subheader(" Tendencia de Datos")

if len(st.session_state.lector.historial) > 1:
    df = pd.DataFrame(st.session_state.lector.historial)
    
    # Gráfico de tendencias
    fig_tendencias = make_subplots(
        rows=2, cols=1,
        subplot_titles=(''Temperatura y Humedad del Aire'', ''Humedad del Suelo''),
        vertical_spacing=0.1
    )
    
    # Temperatura y humedad aire
    fig_tendencias.add_trace(
        go.Scatter(x=df[''timestamp''], y=df[''temperatura''], name="Temperatura", line=dict(color=''red'')),
        row=1, col=1
    )
    
    fig_tendencias.add_trace(
        go.Scatter(x=df[''timestamp''], y=df[''humedad_aire''], name="Humedad Aire", line=dict(color=''blue'')),
        row=1, col=1
    )
    
    # Sensores de suelo
    fig_tendencias.add_trace(
        go.Scatter(x=df[''timestamp''], y=df[''suelo1''], name="Suelo 1", line=dict(color=''green'')),
        row=2, col=1
    )
    
    fig_tendencias.add_trace(
        go.Scatter(x=df[''timestamp''], y=df[''suelo2''], name="Suelo 2", line=dict(color=''orange'')),
        row=2, col=1
    )
    
    fig_tendencias.add_trace(
        go.Scatter(x=df[''timestamp''], y=df[''suelo3''], name="Suelo 3", line=dict(color=''purple'')),
        row=2, col=1
    )
    
    fig_tendencias.add_trace(
        go.Scatter(x=df[''timestamp''], y=df[''suelo4''], name="Suelo 4", line=dict(color=''brown'')),
        row=2, col=1
    )
    
    fig_tendencias.add_hline(y=umbral_humedad, line_dash="dash", line_color="red", row=2, col=1)
    
    fig_tendencias.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig_tendencias, use_container_width=True)
else:
    st.info(" Esperando datos para mostrar tendencias...")

# Auto-actualización
if st.session_state.lector.conectado:
    # Leer datos actuales
    st.session_state.lector.leer_datos()
    
    # Auto-recargar cada 1 segundos
    time.sleep(1)
    st.rerun()


st.markdown("**Sistema de Monitoreo Inteligente - EEST N14**")
