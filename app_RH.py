import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import joblib
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# === Usuarios y contraseñas para login ===
USUARIOS = {
    "rrhh": "1234",
    "admin": "abcd"
}

# === Cargar modelo ===
model_pipeline = joblib.load("Rotacion_V2.pkl")

# === Crear app ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Predicción de Rotación'
server = app.server

# === Layout principal con login ===
app.layout = html.Div([
    # Login
    html.Div(id="login-div", children=[
        html.H3("Login RRHH"),
        dcc.Input(id="username", type="text", placeholder="Usuario", style={'marginRight':'10px'}),
        dcc.Input(id="password", type="password", placeholder="Contraseña", style={'marginRight':'10px'}),
        dbc.Button("Entrar", id="login-button", n_clicks=0, color="primary"),
        html.Div(id="login-output", style={"color":"red", "marginTop":10})
    ], style={"textAlign":"center", "marginTop":"50px"}),

    # Contenido de la app (oculto hasta login correcto)
    html.Div(id="app-content", style={"display":"none"}, children=[
        dbc.Container([
            html.H2("Predicción de Rotación", className="text-center mt-4 mb-4"),
            dcc.Tabs(id="tabs", value='tab1', children=[
                dcc.Tab(label='Datos personales', value='tab1'),
                dcc.Tab(label='Datos laborales', value='tab2'),
                dcc.Tab(label='Resultado', value='tab3')
            ]),

            html.Div([
                # Pestaña 1
                html.Div(id='tab1-content', children=[
                    html.H5("Datos personales", className="mb-3 text-primary fw-bold"),
                    dbc.Row([dbc.Col(html.Label("Género:")), dbc.Col(dcc.RadioItems(['Masculino', 'Femenino'], value='Masculino', id='genero'))], className="mb-2"),
                    dbc.Row([dbc.Col(html.Label("Estado civil:")), dbc.Col(dcc.RadioItems(['Soltero', 'Casado', 'Union_Libre', 'Divorcio','Separado','Viudo'], value='Soltero', id='civil'))], className="mb-2"),
                    dbc.Row([dbc.Col(html.Label("Número de hijos:")), dbc.Col(dcc.Input(id='hijos', type='number', value=0, min=0, max=6, step=1, style={'width':'100%'}))], className="mb-2"),
                ]),

                # Pestaña 2
                html.Div(id='tab2-content', children=[
                    html.H5("Datos laborales", className="mb-3 text-primary fw-bold"),
                    dbc.Row([dbc.Col(html.Label("Ingreso mensual (Income):")), dbc.Col(dcc.Input(id='salario', type='number', value=9500, min=0, max=60000, step=50, style={'width':'100%'}))], className="mb-2"),
                    dbc.Row([dbc.Col(html.Label("Distancia (km):")), dbc.Col(dcc.Input(id='dis', type='number', value=2, min=0, max=30, step=0.1, style={'width':'100%'}))], className="mb-2"),
                    dbc.Row([dbc.Col(html.Label("Reingreso:")), dbc.Col(dcc.RadioItems(['No', 'Sí'], value='No', id='reing'))], className="mb-2"),
                    dbc.Row([dbc.Col(html.Label("Generación:")), dbc.Col(dcc.RadioItems(['Millenials', 'Generation X', 'Boomers', 'Silent'], value='Millenials', id='generation'))], className="mb-2"),
                    dbc.Row([dbc.Col(html.Label("Puesto:")), dbc.Col(dcc.Dropdown([
                        'asistente de servicio','cajero (a)', 'valet parking','imagen','mac',
                        'analista de reclutamiento y seleccion','mesero','inspector de riesgos','barman','dealer',
                        'jefe de a y b','supervisor de boveda','jardinero','lavaloza','cocinero','portero',
                        'jefe de contraloria','table game host','hrbp operativo','tecnico de sistemas sala',
                        'ejecutivo de clientes','supervisor de mesas','lider de servicio','supervisor (a) de cajas','pit boss',
                        'ayudante de cocina','tecnico de mantenimiento','cajero fill bank','host ejecutivo','capitan de meseros',
                        'contralor jr','barista','almacenista','coordinador de imagen','coordinador de turno cocina','asesor sportbar',
                        'coordinador de valet parking','supervisor de porteros','enlace sindical','jefe de boveda y caja',
                        'especialista de capacitacion','supervisor sportbar','chef','jefe de porteros sala','auxiliar de capacitacion',
                        'coordinador de mercadotecnia','sous chef','jefe de sistemas sala','especialista de recl y seleccion',
                        'supervisor de almacen','lider de a y b','especialista de servicio a colaboradores','jefe de maquinas operativo',
                        'chofer','jefe de mantenimiento','asistente de entretenimiento','lider de administracion de cajas',
                        'chofer fashion','jefe de mesas','supervisor de sistemas','anfitrion','coordinador de panaderia',
                        'coordinador de cafeteria','jefe de sala','lider de almacen','supervisor de vvun','panadero','runner'
                    ], value='asistente de servicio', id='puesto'))], className="mb-2"),
                    dbc.Row([dbc.Col(html.Label("Sala:")), dbc.Col(dcc.Dropdown([
                        'JUBILEE','JUBILEECANCUN','VIVENTOAPODACA','HOLLYWOODVALLEALTO','JUBILEECDMX','GOLDENISLAND',
                        'PARADISE','VIVAMEXICO','VIVENTOZAPOPAN','NEWYORK','GRANDLEON','TAJMAHAL','HOLLYWOODCONSTITUCION',
                        'VIVENTOCULIACAN','ELDORADO'
                    ], value='JUBILEE', id='sala'))], className="mb-2"),
                    dbc.Button('Calcular', id='submit-val', color='primary', className='mt-2')
                ]),

                # Pestaña 3: Resultado
                html.Div(id='tab3-content', children=[
                    html.H5("Resultado de la predicción", className="mb-3 text-primary fw-bold"),
                    html.Div(id='prediction-output', className="fs-5 fw-bold text-success")
                ])
            ])
        ], fluid=True)
    ])
])

# === Callback login ===
@app.callback(
    Output("login-output", "children"),
    Output("app-content", "style"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value")
)
def check_login(n, username, password):
    if n > 0:
        if username in USUARIOS and USUARIOS[username] == password:
            return "", {"display":"block"}
        else:
            return "Usuario o contraseña incorrecta", {"display":"none"}
    return "", {"display":"none"}

# === Callback mostrar solo la pestaña activa ===
@app.callback(
    Output('tab1-content', 'style'),
    Output('tab2-content', 'style'),
    Output('tab3-content', 'style'),
    Input('tabs', 'value')
)
def display_tab(tab):
    return (
        {'display': 'block'} if tab == 'tab1' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab2' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab3' else {'display': 'none'},
    )

# === Callback del modelo ===
@app.callback(
    Output('prediction-output', 'children'),
    Input('submit-val', 'n_clicks'),
    State('civil', 'value'),
    State('genero', 'value'),
    State('puesto', 'value'),
    State('salario', 'value'),
    State('sala', 'value'),
    State('dis', 'value'),
    State('reing', 'value'),
    State('generation', 'value'),
    State('hijos', 'value')
)
def update_output(n, civil, genero, puesto, salario, sala, dis, reing, generation, hijos):
    if not n:
        return ""
    tiempo_meses_val = "Mas_año"
    Horas = ['6:00AM-6:00PM', '12:00PM-12:00AM', '6:00PM-6:00AM', '9:00AM-7:00PM', '2:00PM-2:00AM']
    reing_num = 1 if reing == 'Sí' else 0

    resultados = []
    for horario in Horas:
        x = pd.DataFrame({
            "Horario": [horario],
            "Estado_Civil": [civil],
            "Genero": [genero],
            "Puesto": [puesto],
            "Income": [float(salario)],
            "Sala": [sala],
            "Distancia": [float(dis)],
            "Reingreso": [reing_num],
            "Generation": [generation],
            "Tiempo_meses": [tiempo_meses_val],
            "Child": [int(hijos)]
        })
        prediction = model_pipeline.predict_proba(x)[0][1]
        resultados.append({"Horario": horario, "Probabilidad (%)": round(prediction * 100, 2)})

    df = pd.DataFrame(resultados).sort_values("Probabilidad (%)", ascending=False)

    fig = px.bar(
        df,
        x="Probabilidad (%)",
        y="Horario",
        orientation="h",
        text="Probabilidad (%)",
        color="Probabilidad (%)",
        color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
        range_color=[0, 100],
        hover_data=["Horario", "Probabilidad (%)"],
        title="Probabilidad de renuncia por horario"
    )

    fig.update_layout(
        xaxis_title="Probabilidad de renuncia (%)",
        yaxis_title="Horario",
        template="simple_white",
        showlegend=False,
        height=400,
        margin=dict(l=80, r=40, t=60, b=40)
    )

    resumen = [
        html.H6("Resultados detallados:", className="mt-3 text-primary"),
        html.Ul([html.Li(f"{row['Horario']}: {row['Probabilidad (%)']}%") for _, row in df.iterrows()])
    ]

    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(figure=fig),
                *resumen
            ]),
            className="shadow-sm mt-3"
        )
    ])
# === Ejecutar ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # toma el puerto de Render o usa 8050 si es local
    app.run(host='0.0.0.0', port=port)

