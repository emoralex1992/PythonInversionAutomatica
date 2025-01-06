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
        if not os.path.exists(file_path):  # Si el archivo no existe, descargar datos
            print(f"Archivo {file_path} no encontrado. Descargando datos...")
            data = yf.download(ticker_symbol, start="2000-01-01")  # Descargar desde Yahoo Finance
            if data.empty:
                raise ValueError("La descarga de datos está vacía. Revisa el ticker o la conexión.")
            data.to_csv(file_path)  # Guardar en CSV
        else:
            print(f"Archivo {file_path} encontrado. Leyendo datos...")
            data = pd.read_csv(file_path, index_col=0)  # Leer el archivo CSV

        # Convertir índice a datetime con formato explícito
        data.index = pd.to_datetime(data.index, format='%Y-%m-%d', errors='coerce')

        # Filtrar filas con índices inválidos
        data = data[~data.index.isnull()]

        # Asegurarse de que la columna 'Close' sea numérica
        if 'Close' in data.columns:
            data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

        # Filtrar valores nulos en 'Close'
        data = data.dropna(subset=["Close"])

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("El índice del DataFrame no es de tipo DatetimeIndex.")

        return data
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return None  # En caso de error, devuelve None


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


# Estrategia 1: Compra el día 1 de cada mes
def estrategia_dia_1(data_monthly, inversion_mensual):
    """
    Estrategia que realiza una compra fija el día 1 de cada mes.
    :param data_monthly: Serie de precios mensuales (últimos valores del mes).
    :param inversion_mensual: Cantidad fija a invertir cada mes.
    :return: Total de acciones compradas, fechas de compra y precios de compra.
    """
    # Generar una señal de compra para cada fecha en data_monthly
    buy_signal = pd.Series(True, index=data_monthly.index)  # Comprar siempre
    return calcular_estrategia(data_monthly, inversion_mensual, buy_signal)



def encontrar_minimos_mensuales(data):
    """
    Encuentra los índices de los valores mínimos de 'Close' por cada mes.
    :param data: DataFrame con los datos históricos, índice de tipo datetime y columna 'Close'.
    :return: Lista de índices correspondientes a los valores mínimos mensuales.
    """
    # Verificar que el índice sea de tipo DatetimeIndex
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("El índice del DataFrame no es de tipo DatetimeIndex.")

    if 'Close' not in data.columns:
        raise ValueError("La columna 'Close' no existe en el DataFrame.")

    indices_minimos = []
    # Agrupar los datos por año y mes
    for (year, month), group in data.groupby([data.index.year, data.index.month]):
        # Obtener el índice del valor mínimo del grupo
        idx_min = group['Close'].idxmin()
        indices_minimos.append(idx_min)

    return indices_minimos


# Estrategia 2: Compra el valor mínimo de cada
def estrategia_minimos(data, inversion_mensual):
    """
    Estrategia que compra en el valor mínimo mensual.
    :param data: DataFrame con los datos históricos.
    :param inversion_mensual: Cantidad fija a invertir cada mes.
    :return: Total de acciones compradas, fechas de compra y precios de compra.
    """
    # Encontrar índices de mínimos mensuales
    min_indices = encontrar_minimos_mensuales(data)
    min_values = data.loc[min_indices, 'Close']  # Valores mínimos mensuales

    # Crear señal de compra alineada con los mínimos
    buy_signal = pd.Series(False, index=min_values.index)
    buy_signal[min_values.index] = True

    # Usar los valores mínimos para calcular la estrategia
    return calcular_estrategia(min_values, inversion_mensual, buy_signal)



# Función para calcular una estrategia de inversión
def calcular_estrategia(data, inversion_mensual, buy_signal):
    """
    Calcula la cantidad de acciones compradas según una estrategia.
    :param data: Serie de precios utilizada para la estrategia.
    :param inversion_mensual: Cantidad fija a invertir cada mes.
    :param buy_signal: Señal para determinar si se realiza la compra.
    :return: Total de acciones compradas, fechas de compra y precios de compra.
    """
    acciones_totales = 0  # Cantidad total de acciones compradas
    acumulado = 0  # Dinero acumulado esperando una compra
    fechas = []  # Fechas en las que se realizaron compras
    precios = []  # Precios a los que se realizaron las compras

    for fecha, precio in data.items():
        acumulado += inversion_mensual  # Acumular la cantidad mensual
        # Comprar si la señal indica compra
        if buy_signal.loc[fecha] if fecha in buy_signal.index else False:
            if not pd.isna(precio):  # Evitar valores nulos
                acciones_totales += acumulado / precio  # Comprar con el dinero acumulado
                fechas.append(fecha)
                precios.append(precio)
                acumulado = 0  # Resetear el acumulado después de la compra

    # Invertir el acumulado restante en el último precio disponible
    if acumulado > 0:
        acciones_totales += acumulado / data.iloc[-1]

    return acciones_totales, fechas, precios


# Comparar estrategias
def comparar_estrategias(data, inversion_mensual=300):
    """
    Compara múltiples estrategias de inversión y genera gráficos de los resultados.
    :param data: DataFrame con los datos históricos.
    :param inversion_mensual: Cantidad fija a invertir mensualmente.
    """
    print("Simulando estrategias de inversión...")

    # Calcular valores mensuales necesarios
    data_monthly = data['Close'].resample('MS').last()  # Últimos valores mensuales

    # Diccionario con estrategias disponibles
    estrategias_info = {
        "1. Día 1 de cada mes": lambda: estrategia_dia_1(data_monthly, inversion_mensual),
        "2. Valor mínimo mensual": lambda: estrategia_minimos(data, inversion_mensual),
    }

    resultados = []  # Resultados de las estrategias
    estrategias = []  # Detalles de estrategias para gráficos

    # Iterar por las estrategias y calcular resultados
    for nombre, funcion in estrategias_info.items():
        acciones_totales, fechas, precios = funcion()  # Ejecutar la estrategia
        total_invertido = len(data_monthly) * inversion_mensual  # Total invertido
        valor_final = acciones_totales * data_monthly.iloc[-1]  # Valor final de la inversión
        ganancia_porcentaje = ((valor_final - total_invertido) / total_invertido) * 100  # Porcentaje de ganancia
        ganancia_monto = valor_final - total_invertido  # Monto absoluto de ganancia

        # Guardar resultados
        resultados.append((nombre, total_invertido, valor_final, ganancia_porcentaje, ganancia_monto))
        estrategias.append((nombre, fechas, precios, f"estrategia_{nombre.lower().replace(' ', '_').replace('.', '')}.png"))

    # Exportar resultados a un archivo CSV
    df_resultados = pd.DataFrame(resultados, columns=["Estrategia", "Invertido", "Valor Final", "Ganancia %", "Ganancia $"])
    df_resultados.to_csv(os.path.join(output_dir, "resultados_estrategias.csv"), index=False)

    # Imprimir resultados en la consola
    for estrategia, invertido, final, ganancia, monto in resultados:
        print(f"\n--- Estrategia: {estrategia} ---")
        print(f"Total invertido: ${invertido:.2f}")
        print(f"Valor final: ${final:.2f}")
        print(f"Ganancia/pérdida: {ganancia:.2f}%")
        print(f"Monto de ganancia/pérdida: ${monto:.2f}")

    # Graficar cada estrategia
    for nombre, fechas, precios, filename in estrategias:
        plt.figure(figsize=(14, 6))
        plt.plot(data_monthly, label='Precio de Cierre (Mensual)', color='green')  # Precio mensual
        plt.scatter(fechas, precios, color='blue', label=f'Puntos de Compra: {nombre}', s=10)  # Puntos de compra
        plt.title(f"Estrategia: {nombre}")
        plt.xlabel("Fecha")
        plt.ylabel("Precio ($)")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, filename))  # Guardar gráfico
        # plt.show()
        plt.close()


# Función principal
def main():
    """
    Ejecuta el flujo principal: carga de datos y generación de gráficos.
    """
    data = cargar_datos(file_path, ticker_symbol)
    graficar_incrementos(data)
    comparar_estrategias(data)

# Ejecutar script
if __name__ == "__main__":
    main()
