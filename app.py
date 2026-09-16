import streamlit as st
import numpy as np
import sympy as sp
from scipy.optimize import fsolve
import plotly.graph_objects as go

# -------------------------------------------------
# Configuración de la página
# -------------------------------------------------
st.set_page_config(
    page_title="Taller Cálculo 1 – Primer Corte (Interactivo)",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos mejorados
st.markdown("""
<style>
    .main-header {font-size: 2.2rem; font-weight: 700; color: #1f4e79; margin-bottom: 0.2rem;}
    .sub-header {font-size: 1.1rem; color: #555; margin-bottom: 1.5rem;}
    .result-box {
        background-color: #d1e7dd;
        border-left: 6px solid #198754;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #0f5132;
        font-size: 1.15rem;
        font-weight: 600;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        color: #664d03;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Título general
# -------------------------------------------------
st.markdown('<p class="main-header">Taller Entregable – Cálculo 1 (Primer Corte)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Aplicación interactiva</p>', unsafe_allow_html=True)

st.info("Puedes modificar los parámetros y la solución, los pasos y las gráficas se actualizan automáticamente.")

# =================================================
# PESTAÑAS
# =================================================
tab1, tab2, tab3 = st.tabs([
    "📘 Ejercicio 1 – Modelo de infección",
    "📗 Ejercicio 2 – Desigualdad con valor absoluto",
    "📙 Ejercicio 3 – Dominio de h(x)"
])

# =================================================
# EJERCICIO 1
# =================================================
with tab1:
    st.header("Ejercicio 1 (Valor 1.6)")
    st.markdown("""
    Una enfermedad infecciosa comienza a diseminarse en una ciudad pequeña con **100 000** habitantes.  
    Después de \( t \) días, el número de personas infectadas se modela mediante:
    """)
    st.latex(r"f(t)=\dfrac{100000}{5+12495\,e^{-t}}")

    # --- Controles interactivos ---
    st.subheader("Parámetros editables (cámbialos y observa los cambios)")
    col1, col2, col3 = st.columns(3)
    with col1:
        N = st.number_input("Población total (N)", value=100000, min_value=1000, step=1000, key="N1")
    with col2:
        a = st.number_input("Constante a", value=5.0, min_value=0.1, step=0.1, format="%.1f", key="a1")
    with col3:
        b = st.number_input("Constante b", value=12495.0, min_value=1.0, step=1.0, key="b1")
    
    target = st.slider("Número de infectados objetivo", min_value=1000, max_value=int(N*0.95), value=10000, step=500, key="target1")

    # Función
    def f(t):
        return N / (a + b * np.exp(-t))

    # --- Parte analítica ---
    st.subheader("(a) Parte analítica")
    st.markdown("Resolvemos \( f(t) = \) objetivo despejando \( t \):")

    # Mostramos los pasos con los valores actuales (limpios)
    st.latex(rf"\dfrac{{{N}}}{{{a} + {b}\,e^{{-t}}}} = {target}")
    st.latex(rf"{a} + {b}\,e^{{-t}} = \dfrac{{{N}}}{{{target}}}")
    st.latex(rf"{b}\,e^{{-t}} = \dfrac{{{N}}}{{{target}}} - {a}")
    st.latex(rf"e^{{-t}} = \dfrac{{\dfrac{{{N}}}{{{target}}} - {a}}}{{{b}}}")
    st.latex(r"t = -\ln\left( \dfrac{\dfrac{N}{\text{objetivo}} - a}{b} \right)")

    # Cálculo
    try:
        arg = (N / target - a) / b
        if arg <= 0:
            st.markdown('<div class="warning-box">El argumento del logaritmo es ≤ 0. No hay solución real con estos parámetros.</div>', unsafe_allow_html=True)
            t_analitico = None
        else:
            t_analitico = -np.log(arg)
            st.markdown(
                f'<div class="result-box">Solución analítica: &nbsp; t = {t_analitico:.4f} días &nbsp; ≈ &nbsp; <b>{t_analitico:.2f} días</b> (2 decimales)</div>',
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"Error en el cálculo analítico: {e}")
        t_analitico = None

    # --- Parte numérica ---
    st.subheader("(b) Comprobación numérica (fsolve)")

    def ecuacion(t):
        return f(t) - target

    try:
        sol = fsolve(ecuacion, 5.0)
        t_num = float(sol[0])
        st.success(f"**Solución numérica (fsolve):**  t = {t_num:.4f} días")
        if t_analitico is not None:
            st.write(f"Diferencia |analítico − numérico| = `{abs(t_analitico - t_num):.2e}`")
    except Exception as e:
        st.error(f"fsolve falló: {e}")
        t_num = None

    # --- Gráfica ---
    st.subheader("Gráfica interactiva de \( f(t) \)")
    t_vals = np.linspace(0, 20, 600)
    y_vals = f(t_vals)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=t_vals, y=y_vals, mode='lines', name='f(t)',
                              line=dict(color='#0d6efd', width=3)))
    fig1.add_hline(y=target, line_dash="dash", line_color="gray",
                   annotation_text=f"y = {target}", annotation_position="bottom right")

    if t_num is not None:
        fig1.add_trace(go.Scatter(
            x=[t_num], y=[target],
            mode='markers+text',
            marker=dict(size=16, color='red', line=dict(width=2, color='darkred')),
            text=[f"({t_num:.2f}, {target})"],
            textposition="top center",
            name=f"Solución t ≈ {t_num:.2f}"
        ))

    fig1.update_layout(
        title="Modelo de infección – f(t)",
        xaxis_title="Días (t)",
        yaxis_title="Infectados",
        hovermode="x unified",
        template="plotly_white",
        height=520,
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02)
    )
    fig1.update_xaxes(range=[0, 20])
    st.plotly_chart(fig1, use_container_width=True)

    st.caption("Línea horizontal = objetivo de infectados · Punto rojo = solución encontrada")

# =================================================
# EJERCICIO 2
# =================================================
with tab2:
    st.header("Ejercicio 2 (Valor 1.6)")
    st.markdown("Encuentre los valores de \( x \) que satisfacen:")
    st.latex(r"\left|4+\dfrac{5}{x+1}\right| > \dfrac{x}{2}")

    st.subheader("Parámetros editables")
    c1, c2, c3 = st.columns(3)
    with c1:
        p = st.number_input("Constante (4)", value=4.0, step=0.5, key="p2")
    with c2:
        q = st.number_input("Numerador (5)", value=5.0, step=0.5, key="q2")
    with c3:
        r = st.number_input("Coeficiente de x", value=0.5, step=0.1, format="%.2f", key="r2")

    st.latex(rf"\left|{p}+\dfrac{{{q}}}{{x+1}}\right| > {r}\,x")

    st.subheader("(a) Parte analítica + SymPy")
    x = sp.Symbol('x', real=True)
    desigualdad = sp.Abs(p + q/(x+1)) > r*x
    try:
        sol_sympy = sp.solve_univariate_inequality(desigualdad, x, relational=False)
        st.markdown("**Solución simbólica (SymPy):**")
        st.latex(r"\text{Solución} = " + sp.latex(sol_sympy))
    except Exception as e:
        st.warning(f"SymPy no pudo resolver completamente: {e}")

    st.markdown("""
    **Procedimiento analítico:**
    1. Asíntota vertical en \( x = -1 \).
    2. Analizar los casos del valor absoluto.
    3. Resolver las desigualdades en cada intervalo.
    4. Unir los intervalos que cumplen la desigualdad.
    """)

    def g(x_val):
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.abs(p + q/(x_val+1)) - r*x_val

    st.subheader("(b) Gráfica de \( g(x) \)")
    x_vals = np.linspace(-8, 8, 2500)
    mask = np.abs(x_vals + 1) > 0.08
    x_plot = x_vals[mask]
    y_plot = g(x_plot)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=x_plot, y=y_plot, mode='lines', name='g(x)',
                              line=dict(color='#198754', width=2.5)))
    fig2.add_hline(y=0, line_color="black", line_width=1)
    fig2.add_vline(x=-1, line_dash="dash", line_color="red",
                   annotation_text="Asíntota x = -1", annotation_position="top right")

    fig2.add_trace(go.Scatter(
        x=x_plot, y=np.where(y_plot > 0, y_plot, 0),
        fill='tozeroy', fillcolor='rgba(25, 135, 84, 0.25)',
        line=dict(width=0), name='g(x) > 0'
    ))

    fig2.update_layout(
        title="Desigualdad con valor absoluto – g(x)",
        xaxis_title="x",
        yaxis_title="g(x)",
        template="plotly_white",
        height=520,
        yaxis=dict(range=[-15, 15])
    )
    st.plotly_chart(fig2, use_container_width=True)

# =================================================
# EJERCICIO 3
# =================================================
with tab3:
    st.header("Ejercicio 3 (Valor 1.8)")
    st.markdown("Determine el dominio de la función:")
    st.latex(r"h(x)=\dfrac{\ln\bigl(1+|x+2|-2|x|\bigr)}{\sqrt{(x^{2}-16)(1-x^{2})}}")

    st.subheader("(a) Parte analítica – Dominio")

    st.markdown("**Condiciones necesarias para que \( h(x) \) esté definida:**")

    st.markdown("**1. Argumento del logaritmo > 0**")
    st.latex(r"1 + |x+2| - 2|x| > 0")

    st.markdown("**2. Radicando del denominador > 0**")
    st.latex(r"(x^{2}-16)(1-x^{2}) > 0")

    st.markdown("""
    **Análisis del radicando:**

    Los puntos críticos son \( x = \pm 4 \) y \( x = \pm 1 \).  
    Estudiando el signo del producto se obtiene que el radicando es positivo en:
    """)
    st.latex(r"(-4,-1)\cup(1,4)")

    st.markdown("""
    **Análisis del argumento del logaritmo:**

    Se resuelve la desigualdad \( 1 + |x+2| - 2|x| > 0 \) por casos  
    (puntos de cambio: \( x = -2 \) y \( x = 0 \)).

    Después de intersecar ambas condiciones, el dominio de la función es:
    """)

    st.latex(r"\operatorname{Dom}(h) = (-4,-1)\cup(1,4)")

    st.markdown("""
    **Nota:** Los extremos \( \pm 1 \) y \( \pm 4 \) se excluyen porque en ellos el radicando se anula  
    y el denominador sería cero.
    """)

    # --- Función segura ---
    def h_scalar(x):
        arg_log = 1 + np.abs(x + 2) - 2 * np.abs(x)
        radicando = (x**2 - 16) * (1 - x**2)
        if arg_log <= 0 or radicando <= 0:
            return np.nan
        return np.log(arg_log) / np.sqrt(radicando)

    h_vec = np.vectorize(h_scalar)

    # --- Verificación puntual ---
    st.subheader("Verificación puntual")
    pts = st.multiselect(
        "Puntos a evaluar",
        options=[-5, -3.5, -3, -2, -0.5, 0, 0.5, 2, 3, 3.5, 5],
        default=[-3, 0, 3],
        key="pts3"
    )

    for pt in pts:
        val = h_scalar(pt)
        if np.isnan(val):
            st.write(f"**h({pt})** = no definido (fuera del dominio)")
        else:
            st.write(f"**h({pt})** = `{val:.6f}`")

    # --- Gráfica ---
    st.subheader("(b) Gráfica de \( h(x) \) y dominio")
    x_vals = np.linspace(-6, 6, 3000)
    y_vals = h_vec(x_vals)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode='markers',
        marker=dict(size=3, color='#dc3545'),
        name='h(x)'
    ))

    # Bandas del dominio
    for intervalo in [(-4, -1), (1, 4)]:
        fig3.add_vrect(
            x0=intervalo[0], x1=intervalo[1],
            fillcolor="green", opacity=0.18, line_width=0
        )

    fig3.add_hline(y=0, line_color="black", line_width=1)
    fig3.add_vline(x=0, line_color="black", line_width=1)

    fig3.update_layout(
        title="Dominio de h(x)",
        xaxis_title="x",
        yaxis_title="h(x)",
        template="plotly_white",
        height=520,
        yaxis=dict(range=[-5, 5])
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.caption("Las bandas verdes verticales marcan el dominio encontrado analíticamente.")

# -------------------------------------------------
st.markdown("---")
st.caption("Gracias.")
