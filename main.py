import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import numpy as np
import math

# == Parametry Obiektu (Zbiornika) ==
V_INIT = 0.5  # Objętość zbiornika [m^3]
T_INIT = 293.15  # Temperatura gazu (20°C) [K]
R_INIT = 287  # Indywidualna stała gazowa dla powietrza [J/(kg*K)]
ka_INIT = 0.0004  # Wzmocnienie elementu wykonawczego [(kg/s) / %]
kv_INIT = 0.0000012  # Współczynnik wypływu (nieszczelności) [kg/(s * Pa^0.5)]

# == Parametry Regulatora i Symulacji ==
P_STAR_INIT_BAR = 7.0  # Wartość zadana ciśnienia [bar] (7 bar)
TP_INIT = 0.1  # Okres próbkowania [s] (Utrzymujemy stały)
T_SIM_INIT = 300  # Czas symulacji [s]

# == Nastawy Regulatora PI ==
KP_INIT = 0.001  # Wzmocnienie regulatora [%/Pa]
TI_INIT = 20.0  # Czas zdwojenia (całkowania) [s]

# == Limity Operacyjne ==
P_MIN_INIT_BAR = 1.0  # 100000.0 Pa
U_MIN_INIT = 0.0
U_MAX_INIT = 100.0

external_stylesheets = ['https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': 'black',
    'text': '#E0E0E0',
    'panel_bg': '#252526',
    'border': '#444444',
    'primary': '#007ACC'
}

app.layout = html.Div([
    html.H1(
        "System sterowania ciśnieniem w kompresorze",
        style={'textAlign': 'center', 'color': colors['text']}
    ),

    html.Div([

        html.Div([

            html.Div([
                html.H3("Parametry symulacji i obiektu", style={'color': colors['text']}),
                html.Label("Wartość zadana (p_sp) [bar]:", style={'color': colors['text']}),
                dcc.Slider(id='slider-p-sp', min=1.0, max=8.0, step=0.1, value=P_STAR_INIT_BAR,
                           marks={i: f"{i} bar" for i in range(1, 9)}),

                html.Label("Objętość zbiornika (V) [m^3]:", style={'color': colors['text']}),
                dcc.Slider(id='input-V', min=0.1, max=1.0, step=0.1, value=V_INIT,
                           marks={0.1: '0.1', 0.25: '0.25', 0.5:'0.5', 0.75: '0.75', 1: '1.0'}),

                html.Label("Czas symulacji (tsim) [s]:", style={'color': colors['text']}),
                dcc.Slider(id='input-tsim', min=100, max=2000, step=10, value=T_SIM_INIT,
                           marks={100: '100', 250: '250', 500: '500', 750: '750', 1000: '1000', 1500: '1500',
                                  2000: '2000'}),
                
                html.Label("Wsp. nieszczelności (kv):", style={'color': colors['text']}),
                dcc.RadioItems(
                    id='input-kv',
                    options=[
                        {'label': 'Mała (0.5e-6)', 'value': 0.0000005},
                        {'label': 'Średnia (1.2e-6)', 'value': 0.0000012},
                        {'label': 'Duża (3.0e-6)', 'value': 0.0000030},
                        {'label': 'Bardzo duża (5.0e-6)', 'value': 0.0000050}
                    ],
                    value=kv_INIT,
                    style={'color': colors['text'], 'marginBottom': '15px'},
                    labelStyle={'display': 'block', 'marginTop': '5px'}
                ),
            ]),

            html.Div([
                html.H3("Nastawy regulatora PI", style={'color': colors['text']}),
                html.Label("Wzmocnienie proporcjonalne (Kp) [%/Pa]:", style={'color': colors['text']}),
                dcc.Slider(id='input-Kp', min=0.0001, max=0.01, step=0.0001, value=KP_INIT,
                           marks={0.0001: '0.0001', 0.001: '0.001', 0.01: '0.01'}),

                html.Label("Czas całkowania (Ti) [s]:", style={'color': colors['text']}),
                dcc.Slider(id='input-Ti', min=1.0, max=50.0, step=1.0, value=TI_INIT,
                           marks={1: '1', 10: '10', 20: '20', 50: '50'}),
            ]),

            html.Div([
                html.H3("Limity operacyjne i saturacja", style={'color': colors['text']}),

                html.Label("Ciśnienie minimalne (p_min) [bar]:", style={'color': colors['text']}),
                dcc.Slider(id='input-p-min',
                           min=0.5,
                           max=2.0,
                           step=0.1,
                           value=P_MIN_INIT_BAR,
                           marks={0.5: '0.5', 1.01325: '1.01325 (Atm)', 2: '2.0'}),

                html.Label("Saturacja dolna (u_min) [%]:", style={'color': colors['text']}),
                dcc.Slider(id='input-u-min',
                           min=0.0,
                           max=20.0,
                           step=1.0,
                           value=U_MIN_INIT,
                           marks={0: '0%', 10: '10%', 20: '20%'}),

                html.Label("Saturacja górna (u_max) [%]:", style={'color': colors['text']}),
                dcc.Slider(id='input-u-max',
                           min=80.0,
                           max=100.0,
                           step=1.0,
                           value=U_MAX_INIT,
                           marks={80: '80%', 90: '90%', 100: '100%'}),
            ])

        ], style={
            'backgroundColor': colors['panel_bg'], 'padding': '20px', 'borderRadius': '5px',
            'display': 'grid',
            'grid-template-columns': 'repeat(auto-fit, minmax(350px, 1fr))',
            'gap': '1rem 2rem'
        }),

        html.Div([
            html.Button(
                'Uruchom symulację',
                id='submit-button-state',
                n_clicks=0,
                style={
                    'fontSize': '16px', 'padding': '10px 20px', 'width': '50%', 'minWidth': '200px',
                    'backgroundColor': colors['primary'], 'color': 'white', 'border': 'none',
                    'cursor': 'pointer', 'borderRadius': '5px'
                }
            )
        ], style={'padding': '20px', 'textAlign': 'center'}),

        html.Div([
            dcc.Graph(id='graph-pressure', style={'height': '50vh'}),
            dcc.Graph(id='graph-control-signal', style={'height': '35vh'}),
            dcc.Graph(id='graph-mass-flow', style={'height': '35vh'})
        ], style={'paddingTop': '10px'})

    ], style={'padding': '20px'})

], style={'backgroundColor': colors['background'], 'padding': '0', 'margin': '0',
          'fontFamily': "'Open Sans', sans-serif",
          'color': colors['text']})


@app.callback(
    [Output('graph-pressure', 'figure'),
     Output('graph-control-signal', 'figure'),
     Output('graph-mass-flow', 'figure')],
    [Input('submit-button-state', 'n_clicks')],
    [State('slider-p-sp', 'value'),
     State('input-V', 'value'),
     State('input-kv', 'value'),
     State('input-tsim', 'value'),
     State('input-Kp', 'value'),
     State('input-Ti', 'value'),
     State('input-p-min', 'value'),
     State('input-u-min', 'value'),
     State('input-u-max', 'value')
     ]
)
def update_simulation(n_clicks, p_sp_bar, V, kv, tsim, Kp, Ti, p_min_bar, u_min, u_max):
    plotly_template = "plotly_dark"

    font_settings = dict(
        family="'Open Sans', sans-serif",
        size=13,
        color=colors['text']
    )

    legend_settings_bottom_right = dict(
        x=0.99,
        y=0.01,
        xanchor='right',
        yanchor='bottom',
        bgcolor='rgba(37, 37, 38, 0.8)',
        bordercolor=colors['border'],
        borderwidth=1
    )

    if n_clicks == 0:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Ustaw parametry i kliknij 'Uruchom Symulację'",
            template=plotly_template,
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['panel_bg'],
            font=font_settings
        )
        return empty_fig, empty_fig, empty_fig

    R = R_INIT
    T = T_INIT
    Tp = TP_INIT
    K_obj = (Tp * R * T) / V
    p_star = p_sp_bar * 100000.0
    ka = ka_INIT

    p_min = p_min_bar * 100000.0

    N = int(tsim / Tp) + 1

    t = np.linspace(0, tsim, N)
    p = np.zeros(N)
    u = np.zeros(N)
    e = np.zeros(N)
    m_in = np.zeros(N)
    m_out = np.zeros(N)

    p[0] = p_min
    u[0] = u_min

    e_n_1 = p_star - p[0]
    e[0] = e_n_1

    for n in range(1, N):
        e_n = p_star - p[n - 1]
        e[n] = e_n
        delta_e = e_n - e_n_1
        P_term = Kp * delta_e
        I_term = Kp * (Tp / Ti) * e_n
        delta_u = P_term + I_term
        u_niesat = u[n - 1] + delta_u

        u[n] = np.clip(u_niesat, u_min, u_max)

        m_in[n] = ka * u[n]
        m_out[n] = kv * np.sqrt(p[n - 1])

        p_new = p[n - 1] + K_obj * (m_in[n] - m_out[n])

        p[n] = max(p_min, p_new)
        e_n_1 = e_n

    p_bar = p / 100000.0
    p_star_bar_list = [p_sp_bar] * N

    fig_pressure = go.Figure()
    fig_pressure.add_trace(
        go.Scatter(x=t, y=p_bar, mode='lines', name='Ciśnienie p(n)',
                   line=dict(color='yellow', width=2.5)))
    fig_pressure.add_trace(go.Scatter(
        x=t, y=p_star_bar_list, mode='lines',
        name=f'Wartość zadana p* ({p_sp_bar} bar)',
        line=dict(dash='dash', color='red', width=2)))

    fig_pressure.update_layout(
        title="Ciśnienie w zbiorniku:",
        xaxis=dict(title="Czas [s]", dtick=60),
        yaxis_title="Ciśnienie [bar]",
        hovermode="x unified", template=plotly_template,
        font=font_settings,
        legend=legend_settings_bottom_right,
        title_font_size=18
    )

    fig_control = go.Figure()
    fig_control.add_trace(go.Scatter(
        x=t, y=u, mode='lines',
        name='Sygnał sterujący u(n)',
        line=dict(color='green', width=2.5)))

    fig_control.update_layout(
        title="Sygnał sterujący kompresora:",
        xaxis=dict(title="Czas [s]", dtick=60),
        yaxis_title="Sterowanie kompresora [%]",
        yaxis_range=[u_min - 5, u_max + 5],
        hovermode="x unified", template=plotly_template,
        font=font_settings,
        legend=legend_settings_bottom_right,
        title_font_size=18
    )

    legend_settings_top_right = legend_settings_bottom_right.copy()
    legend_settings_top_right['y'] = 0.99
    legend_settings_top_right['yanchor'] = 'top'

    fig_flow = go.Figure()
    fig_flow.add_trace(go.Scatter(
        x=t, y=m_in, mode='lines',
        name='Dopływ m_in(n)',
        line=dict(color='cyan', width=2.5)))
    fig_flow.add_trace(go.Scatter(
        x=t, y=m_out, mode='lines',
        name='Odpływ m_out(n)',
        line=dict(color='orange', dash='dot', width=2.5)))

    fig_flow.update_layout(
        title="Przepływy masowe w kompresorze:",
        xaxis=dict(title="Czas [s]", dtick=60),
        yaxis_title="Przepływ masy [kg/s]",
        hovermode="x unified", template=plotly_template,
        font=font_settings,
        legend=legend_settings_top_right,
        title_font_size=18
    )

    return fig_pressure, fig_control, fig_flow


if __name__ == '__main__':
    app.run(debug=True)