import os
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import joblib
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# =========================
# USUARIOS
# =========================
USUARIOS = {
    "rrhh": {
        "password": "1234",
        "role": "admin",
        "sala": "ALL"
    },
    "admin": {
        "password": "abcd",
        "role": "admin",
        "sala": "ALL"
    },
    "jubilee_user": {
        "password": "JUBILEE",
        "role": "sala",
        "sala": "JUBILEE"
    },
    "cancun_user": {
        "password": "JUBILEECANCUN",
        "role": "sala",
        "sala": "JUBILEECANCUN"
    }
}

# =========================
# CARGAR MODELO
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "Rotacion_V2.pkl")
model_pipeline = joblib.load(MODEL_PATH)

# =========================
# APP
# =========================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Predicción de Rotación"
server = app.server

# =========================
# LAYOUT
# =========================
app.layout = html.Div([

    dcc.Store(id="user-session", storage_type="session"),

    # LOGIN
    html.Div(id="login-div", children=[
        html.H3("Login RRHH"),
        dcc.Input(id="username", type="text", placeholder="Usuario"),
        dcc.Input(id="password", type="password", placeholder="Contraseña"),
        dbc.Button("Entrar", id="login-button", n_clicks=0, color="primary"),
        html.Div(id="login-output", style={"color": "red", "marginTop": 10})
    ], style={"textAlign": "center", "marginTop": "50px"}),

    # APP
    html.Div(id="app-content", style={"display": "none"}, children=[
        dbc.Container([

            html.H2("Predicción de Rotación", className="text-center mt-4 mb-4"),

            dcc.Tabs(id="tabs", value="tab1", children=[
                dcc.Tab(label="Datos personales", value="tab1"),
                dcc.Tab(label="Datos laborales", value="tab2"),
                dcc.Tab(label="Resultado", value="tab3")
            ]),

            # TAB 1
            html.Div(id="tab1-content", children=[
                dbc.Row([dbc.Col("Género"), dbc.Col(dcc.RadioItems(
                    ["Masculino", "Femenino"], value="Masculino", id="genero"))]),
                dbc.Row([dbc.Col("Estado civil"), dbc.Col(dcc.RadioItems(
                    ["Soltero", "Casado", "Union_Libre", "Divorcio", "Separado", "Viudo"],
                    value="Soltero", id="civil"))]),
                dbc.Row([dbc.Col("Número de hijos"), dbc.Col(
                    dcc.Input(id="hijos", type="number", value=0))])
            ]),

            # TAB 2
            html.Div(id="tab2-content", children=[
                dbc.Row([dbc.Col("Ingreso mensual"), dbc.Col(
                    dcc.Input(id="salario", type="number", value=9500))]),
                dbc.Row([dbc.Col("Distancia"), dbc.Col(
                    dcc.Input(id="dis", type="number", value=2))]),
                dbc.Row([dbc.Col("Reingreso"), dbc.Col(
                    dcc.RadioItems(["No", "Sí"], value="No", id="reing"))]),
                dbc.Row([dbc.Col("Generación"), dbc.Col(
                    dcc.RadioItems(
                        ["Millenials", "Generation X", "Boomers", "Silent"],
                        value="Millenials", id="generation"))]),
                dbc.Row([dbc.Col("Puesto"), dbc.Col(
                    dcc.Dropdown(id="puesto",
                        options=[{"label": i, "value": i} for i in [
                            'asistente de servicio','cajero (a)','valet parking','imagen',
                            'mesero','barman','dealer','lavaloza','cocinero'
                        ]],
                        value='asistente de servicio'))]),

                html.Div(id="sala-container", children=[
                    dbc.Row([dbc.Col("Sala"), dbc.Col(
                        dcc.Dropdown(
                            [
                                'JUBILEE','JUBILEECANCUN','VIVENTOAPODACA',
                                'HOLLYWOODVALLEALTO','JUBILEECDMX','GOLDENISLAND',
                                'PARADISE','VIVAMEXICO','VIVENTOZAPOPAN','NEWYORK',
                                'GRANDLEON','TAJMAHAL','HOLLYWOODCONSTITUCION',
                                'VIVENTOCULIACAN','ELDORADO'
                            ],
                            id="sala"
                        ))])
                ]),

                dbc.Button("Calcular", id="submit-val", color="primary")
            ]),

            # TAB 3
            html.Div(id="tab3-content", children=[
                html.Div(id="prediction-output")
            ])

        ], fluid=True)
    ])
])

# =========================
# LOGIN CALLBACK
# =========================
@app.callback(
    Output("login-output", "children"),
    Output("app-content", "style"),
    Output("user-session", "data"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value")
)
def check_login(n, username, password):
    if n and username in USUARIOS:
        user = USUARIOS[username]
        if user["password"] == password:
            return "", {"display": "block"}, {
                "role": user["role"],
                "sala": user["sala"]
            }
    return "Usuario o contraseña incorrecta", {"display": "none"}, None

# =========================
# CONTROL SALA
# =========================
@app.callback(
    Output("sala", "value"),
    Output("sala", "disabled"),
    Output("sala-container", "style"),
    Input("user-session", "data")
)
def control_sala(session):
    if not session:
        return None, True, {"display": "none"}

    if session["role"] == "admin":
        return "JUBILEE", False, {"display": "block"}
    else:
        return session["sala"], True, {"display": "none"}

# =========================
# TABS
# =========================
@app.callback(
    Output("tab1-content", "style"),
    Output("tab2-content", "style"),
    Output("tab3-content", "style"),
    Input("tabs", "value")
)
def display_tab(tab):
    return (
        {"display": "block"} if tab == "tab1" else {"display": "none"},
        {"display": "block"} if tab == "tab2" else {"display": "none"},
        {"display": "block"} if tab == "tab3" else {"display": "none"}
    )

# =========================
# MODELO
# =========================
@app.callback(
    Output("prediction-output", "children"),
    Input("submit-val", "n_clicks"),
    State("civil", "value"),
    State("genero", "value"),
    State("puesto", "value"),
    State("salario", "value"),
    State("sala", "value"),
    State("dis", "value"),
    State("reing", "value"),
    State("generation", "value"),
    State("hijos", "value")
)
def predict(n, civil, genero, puesto, salario, sala, dis, reing, generation, hijos):
    if not n:
        return ""

    Horas = [
        '6:00AM-6:00PM','12:00PM-12:00AM',
        '6:00PM-6:00AM','9:00AM-7:00PM','2:00PM-2:00AM'
    ]

    reing_num = 1 if reing == "Sí" else 0
    resultados = []

    for h in Horas:
        x = pd.DataFrame([{
            "Horario": h,
            "Estado_Civil": civil,
            "Genero": genero,
            "Puesto": puesto,
            "Income": salario,
            "Sala": sala,
            "Distancia": dis,
            "Reingreso": reing_num,
            "Generation": generation,
            "Tiempo_meses": "Mas_año",
            "Child": hijos
        }])

        p = model_pipeline.predict_proba(x)[0][1]
        resultados.append({"Horario": h, "Probabilidad (%)": round(p * 100, 2)})

    df = pd.DataFrame(resultados)

    fig = px.bar(
        df, x="Probabilidad (%)", y="Horario",
        orientation="h", title="Probabilidad de renuncia"
    )

    return dcc.Graph(figure=fig)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)




