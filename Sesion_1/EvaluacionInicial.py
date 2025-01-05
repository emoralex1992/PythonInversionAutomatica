import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import os
import shutil

# Configuración del archivo y ticker
ticker_symbol = "SPY"  # Símbolo del ETF que representa el S&P 500
file_path = "SPY_historical_data.csv"  # Ruta para guardar los datos históricos descargados

# Crear carpeta para almacenar los resultados (gráficos y datos generados)
output_dir = "Outputs"
if os.path.exists(output_dir):  # Eliminar la carpeta si ya existe
    shutil.rmtree(output_dir)
os.makedirs(output_dir)  # Crear una nueva carpeta Outputs

# Descargar o cargar datos históricos
def cargar_datos(file_path, ticker_symbol):
    """
    Carga datos históricos desde un archivo local o los descarga de Yahoo Finance si no existen.
    """
    try:
        if os.path.exists(file_path):  # Verifica si el archivo ya existe
            print(f"Archivo {file_path} encontrado. Leyendo datos...")
            data = pd.read_csv(file_path, index_col=0)
            data.index = pd.to_datetime(data.index, format='%Y-%m-%d', errors='coerce', utc=True)  # Convertir índices a datetime
            data['Close'] = pd.to_numeric(data['Close'], errors='coerce')  # Convertir a numérico la columna 'Close'
            data = data.dropna(subset=["Close"])  # Eliminar filas con valores nulos en 'Close'
            return data
        else:
            print(f"Archivo {file_path} no encontrado. Descargando datos...")
            data = yf.download(ticker_symbol, start="2000-01-01")  # Descarga datos desde 2000
            data.to_csv(file_path)  # Guarda los datos descargados en un archivo CSV
            return data
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        raise

# Gráficos de incremento mensual, anual y valor de cierre
def graficar_incrementos(data):
    """
    Calcula y grafica los incrementos mensuales, anuales y el valor de cierre del fondo indexado.
    """
    print("Calculando incrementos mensuales y anuales...")
    data_monthly = data['Close'].resample('ME').last().squeeze()  # Asegurar que sea una Serie
    data_annual = data['Close'].resample('YE').last().squeeze()  # Asegurar que sea una Serie

    # Calcular incrementos y asegurarse de que sean numéricos
    incremento_mensual = data_monthly.pct_change().fillna(0) * 100  # Incremento porcentual mensual
    incremento_anual = data_annual.pct_change().fillna(0) * 100  # Incremento porcentual anual

    # Gráfico del valor de cierre del fondo indexado
    print("Generando gráfico del valor de cierre del fondo indexado...")
    plt.figure(figsize=(12, 6))
    plt.plot(data['Close'], label="Valor de Cierre", color='green', linewidth=2)  # Línea verde para el valor de cierre
    plt.title("Evolución del Valor de Cierre del SPY")
    plt.xlabel("Fecha")
    plt.ylabel("Valor de Cierre ($)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "valor_cierre.png"))  # Guardar el gráfico del valor de cierre
    plt.close()

    # Gráfico mensual
    print("Generando gráfico de incremento mensual...")
    plt.figure(figsize=(12, 6))
    colores_mensual = ['green' if x > 0 else 'red' for x in incremento_mensual]
    plt.bar(incremento_mensual.index, incremento_mensual, color=colores_mensual, width=20)
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.title("Incremento Mensual del Valor del SPY")
    plt.ylabel("Incremento (%)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "incremento_mensual.png"))
    plt.close()

    # Gráfico anual
    print("Generando gráfico de incremento anual...")
    plt.figure(figsize=(12, 6))
    colores_anual = ['green' if x > 0 else 'red' for x in incremento_anual]
    plt.bar(incremento_anual.index, incremento_anual, color=colores_anual, width=200)
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.title("Incremento Anual del Valor del SPY")
    plt.ylabel("Incremento (%)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "incremento_anual.png"))
    plt.close()

# Función principal
def main():
    """
    Ejecuta el flujo principal: carga de datos y generación de gráficos.
    """
    data = cargar_datos(file_path, ticker_symbol)
    graficar_incrementos(data)

# Ejecutar script
if __name__ == "__main__":
    main()
