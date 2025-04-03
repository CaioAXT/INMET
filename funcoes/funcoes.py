import numpy as np
import math
from numba import njit
import pandas as pd

distancia_km = 0.1
Numeroponto = 0


@njit(cache=True, fastmath=True, boundscheck=False)
def haversine(lat1, lon1, lat2, lon2):
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return 6371 * c


def diretriz(PontosVertices, distancia_km: float):
    Numeroponto = 0
    PontosNovos = pd.DataFrame(
        columns=["Estacao", "Longitude", "Latitude", "Classificação do Ponto"]
    )

    for i in range(len(PontosVertices)):
        current_row = PontosVertices.iloc[i]
        nom = current_row["Nome do Vertice"]
        lat = float(current_row["Latitude"])
        long = float(current_row["Longitude"])

        Numeroponto += 1
        PontosNovos.loc[Numeroponto] = [nom, lat, long, "Vertice"]

        if i < len(PontosVertices) - 1:
            next_row = PontosVertices.iloc[i + 1]
            latnext = float(next_row["Latitude"])
            lonnext = float(next_row["Longitude"])

            distancia_total = haversine(lat1=lat, lon1=long, lat2=latnext, lon2=lonnext)

            if distancia_total > distancia_km:
                n_pontos = max(1, int(distancia_total // distancia_km))

                for j in range(1, n_pontos + 1):
                    fator = j / (n_pontos + 1)
                    lat_inter = lat + fator * (latnext - lat)
                    lon_inter = long + fator * (lonnext - long)
                    Numeroponto += 1
                    PontosNovos.loc[Numeroponto] = [
                        f"{nom} - Intermediário {j}",
                        lat_inter,
                        lon_inter,
                        "Diretriz da LT",
                    ]

    return PontosNovos


def parse_to_float(value):
    value_str = str(value)
    if "," in value_str:
        value_str = value_str.replace(",", ".")
    try:
        return float(value_str)
    except:
        return -9999.0


@njit(cache=True, fastmath=True, boundscheck=False)
def inom(
    alturamedia: int,
    diametrototal: float,
    diametroaluminio: float,
    epsilon: float,
    coefabsorsolar: float,
    coefvarrestemp: float,
    feixe: int,
    rdc20cc: float,
    artemp: float,
    radglobal: float,
    velvento: float,
    temperatura: float,
) -> float:
    # Cálculo de dra
    dra = math.exp(-0.000116 * alturamedia)

    # Cálculo de vf com verificação de divisão por zero
    vf = 1.32e-5 + 9.5e-7 * (temperatura + artemp) / 2.0
    if vf == 0.0:
        return -9999.0

    # Cálculo de y
    y = 2.42e-2 + 7.2e-5 * (temperatura + artemp) / 2.0

    # Verificação de denominador para rr

    diam_alum_2 = 2.0 * diametroaluminio
    denominator_rr = 2.0 * (diametrototal - diam_alum_2)
    if denominator_rr == 0.0:
        return -9999.0
    rr = diametroaluminio / denominator_rr

    # Cálculo de re
    re = (diametrototal * velvento * dra) / vf

    # Determinação de nn1 e nn2
    nn1 = 1 if 0.05 < rr < 0.718 else 0
    nn2 = 1 if 100.0 < re < 2650.0 else 0

    # Determinação de m2
    if nn1 == 1 and nn2 == 1:
        m2 = 0.471
    elif nn1 == 0 and nn2 == 0:
        m2 = 0.633
    elif nn1 == 1 and nn2 == 0:
        m2 = 0.8
    else:
        m2 = 0.0  # Caso não coberto (ex: nn1=0, nn2=1)

    # Determinação de b2
    if nn1 == 1 and nn2 == 1:
        b2 = 0.641
    elif nn1 == 0 and nn2 == 0:
        b2 = 0.178
    elif nn1 == 1 and nn2 == 0:
        b2 = 0.048
    else:
        b2 = 0.0  # Caso não coberto

    # Cálculo de nu
    nu = b2 * (re**m2)

    # Cálculo de pc
    delta_temp = temperatura - artemp
    pc = math.pi * y * delta_temp * nu

    # Cálculo de pr
    temp_k = temperatura + 273.0
    artemp_k = artemp + 273.0
    pr = 5.67e-8 * epsilon * math.pi * diametrototal * (temp_k**4 - artemp_k**4)

    # Cálculo de qs
    qs = 0.2778 * radglobal * coefabsorsolar * diametrototal

    # Cálculo de rtc com verificação
    rtc = (rdc20cc / 1000.0) * (1.0 + coefvarrestemp * (temperatura - 20.0))
    if rtc <= 0.0:
        return -9999.0

    # Verificação de numerador para sqrt
    numerator = pc + pr - qs
    if numerator < 0.0:
        return -9999.0

    # Cálculo final com verificação de raiz
    ifinal_sqrt = numerator / rtc
    if ifinal_sqrt < 0.0:
        return -9999.0
    ifinal = feixe * math.sqrt(ifinal_sqrt)

    # Retorno com verificação de valor finito
    return ifinal if math.isfinite(ifinal) else -9999.0


@njit(cache=True, fastmath=True, boundscheck=False)
def iref(
    mes: int,
    hora: int,
    idnom: float,
    innom: float,
    vdnom: float,
    vnnom: float,
    idsobrec: float,
    insobrec: float,
    vdsobrec: float,
    vnsobrec: float,
    padraoinom: bool = True,
):

    igual_a_inverno = 4 <= mes <= 9
    igual_a_dia = 6 <= hora <= 18
    igual_a_nominal = padraoinom

    if igual_a_inverno:
        if igual_a_dia:
            return idnom if igual_a_nominal else idsobrec
        else:
            return innom if igual_a_nominal else insobrec
    else:  # Verão
        if igual_a_dia:
            return vdnom if igual_a_nominal else vdsobrec
        else:
            return vnnom if igual_a_nominal else vnsobrec


@njit(cache=True, fastmath=True, boundscheck=False)
def tcnom(
    alturamediadalt: int,
    diametrototal: float,
    diametroaluminio: float,
    epsilon: float,
    coefabsorsolar: float,
    coefvarrestemp: float,
    feixe: int,
    rdc20cc: float,
    artemp: float,
    radglobal: float,
    velvento: float,
    mes: int,
    hora: int,
    idnom: float,
    innom: float,
    vdnom: float,
    vnnom: float,
    idsobrec: float,
    insobrec: float,
    vdsobrec: float,
    vnsobrec: float,
    padraoinom: bool = True,
    tol: float = 0.5,
    minrange: int = 40,
    maxrange: int = 200,
) -> float:
    ref_value = iref(
        mes,
        hora,
        idnom,
        innom,
        vdnom,
        vnnom,
        idsobrec,
        insobrec,
        vdsobrec,
        vnsobrec,
        padraoinom,
    )

    args_inom = (
        alturamediadalt,
        diametrototal,
        diametroaluminio,
        epsilon,
        coefabsorsolar,
        coefvarrestemp,
        feixe,
        rdc20cc,
        artemp,
        radglobal,
        velvento,
    )

    valorbase = 0.0
    iniciorange = minrange * 10
    fimrange = maxrange * 10
    for t in range(2000, 25000, 1):
        valorbase = t / 100.0
        valornominal = inom(*args_inom, valorbase)
        if valornominal == -9999.0:
            continue

        if abs(ref_value - valornominal) < tol:
            break

    return valorbase
