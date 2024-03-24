
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from Simulation import Simulation
import plotly.express as px

# patients = dataframe

app = Dash(__name__)

sidebar = html.Div(className = 'sidebar', children = [
            html.H1( className = 'title', children = "Input"),
            html.P( className = 'description', children = "Below one can find the parameters to tune the simulation. Each parameter is described in short "),
            
            html.H3( children = "Simulation duration (years)"),
            html.P( children = "Simulation years refers to the amount of years the simulation will simulate. More years result in better convergence, yet also more computation time"),
            dcc.Slider( id = 'simulation_years', className = 'slider', min=2, max=9, step = 1, marks={ 2:'2', 3:'3', 4:'4', 5:'5', 9:'9'}, value=5, ),
            
            html.H3(children = "Opening Hours"),
            html.P( children = "Opening hours refers to the time the STRC is open for accepting/processing admissions"),
            html.Div(className = 'opening_hours', children = [
                html.Div(children=[
                    html.Label("Opening Hour"),
                    dcc.Input(id='opening', type='number', min=0, max=12, step=1, value=9),
                ]),
                html.Div(children=[
                    html.Label("Closing Hour"),
                    dcc.Input(id='closing', type='number', min=16, max=23, step=1, value=17),
                ])
            ]),
            dcc.Checklist(id = 'weekend', className = 'checkbox', options = ['Weekend'], inline= True),

            html.H3(children = "Beds"),
            html.P( children = "Beds refer to the number of beds available in the STRC"),
            dcc.Input(id='beds', type='number', min=2, max=200, step=1, value=100),

            html.H3(children = "Be patient"),
            html.P( children = "Patience refer to the time patients are willing to wait before making applying to the hospital"),
            dcc.Input(id='patience', type='number', min=0, max=48, step=1, value=8),
            html.Span(children = "*this parameter only affects patients coming from the general practitioner or emergency department"),

            html.H3(children = "Transfer time"),
            html.P( children = "Transfer time refers to the amount of time it takes for a patient to be processed and transported to the STRC"),
            dcc.Input(id='transfer_time', type='number', min=0, max=48, step=1, value=8),
    

            html.H2(children = "What if scenarios.."),
            html.H3(children = "Increase in aging"),
            html.P(children = "As we know, the number of eldery will continue to increase in the comming years. As a result, the numbers of patients that need care grows as well. This parameter refers to the percentile increase in arriving patients."),
            dcc.Input(id='increase_arr', type='number', min=1, max=2, step=0.1, value=1),
            
            html.H3(children = "Highter Tariff"),
            html.P(children = "A solution to decrease the time of stay at the STRC, one may increase the price of care and residence. This parameter refers to the decrease in lengths of stay in percentiles"),
            dcc.Input(id='decrease_los', type='number', min=0, max=1, step=0.1, value=0),       

            html.Button('Submit', id='submit-val', n_clicks=0)

    ])

visuals = html.Div(className = 'output', children = [
            html.H1( className = 'title', children = "Output"),

            html.Div(className = 'waiting-time', children = [
                html.Div(className = 'WT-container', children = [

                    html.Div(className = 'metrics-container', children = [

                        html.Div(className = 'card --fill', children = [

                            html.H2(children = "Probability patient has to wait", className = "output-title"),
                            html.H3(id = "output-waiting-time-probability", className = "output-value --prob", children='XX'),
                        ]),

                        html.Div(className = 'card --outline', children = [

                            html.H2(children = "Median waiting time", className = "output-title"),
                            html.H3(id = "output-waiting-time-median", className = "output-value --avg", children='XX'),
                        ]),

                        html.Div(className = 'card --outline', children = [

                            html.H2(children = "Waiting time Standard deviation", className = "output-title"),
                            html.H3(id = "output-waiting-time-std", className = "output-value --avg", children='XX'),
                        ])
                    ]),

                    html.Div(className = 'graph-container', children = [

                        html.H1(children = "Distribution waiting time", className = "output-title"),
                        dcc.Graph(id="output-waiting-time-dist", className = 'output-graph --hist'),
                    ])
                ])
            ]),

            html.Div(className = 'hospital-values', children = [
                html.Div(className = 'hospital-container', children = [

                    html.Div(className = 'graph-container', children = [
                        html.H1(children = "People in the hopsital (Avg)", className = "output-title"),
                        dcc.Graph(id="output-hospital-patients-in-system", className = 'output-graph --hist'),
                    ]),

                    html.Div(className = 'metrics-container', children = [

                        html.Div(className = 'card --fill', children = [

                            html.H2(children = "probability patient goes to hopsital", className = "output-title"),
                            html.H3(id = "output-hospital-blocking-probability", className = "output-value --prob", children='XX'),
                        ]),

                        html.Div(className = 'card --outline', children = [

                            html.H2(children = "Patients recovered in Hospital", className = "output-title"),
                            html.H3(id = "output-hospital-recovered", className = "output-value --patients", children='XX'),
                        ]),

                        html.Div(className = 'card --outline', children = [

                            html.H2(children = "Median stay in hopsital", className = "output-title"),
                            html.H3(id = "output-hospital-median-stay", className = "output-value --avg", children='XX'),
                        ])
                    ])
                ])
            ]),

            html.Div(className = 'STRC-container', children = [
                html.Div(className = '--card', children = [
                    html.H1(children = "Distribution of care needed by patient", className = "output-title"),
                    dcc.Graph(id="output-types-of-care", className = 'output-graph --pie'),
                ]),
                html.Div(className = '--card', children = [
                    html.H1(children = "Beds occupied in STRC (Avg)", className = "output-title"),
                    dcc.Graph(id="output-beds-filled", className = 'output-graph'),
                ]),
            ])      

                    

        ])


app.layout = html.Div(className='container', children = [
    html.Div( className = 'content', children = [
        sidebar,
        visuals
        ])
])


@app.callback(  
                # Output
                Output('output-waiting-time-probability', 'children'),
                Output('output-waiting-time-median', 'children'),
                Output('output-waiting-time-std', 'children'),
                Output('output-waiting-time-dist', 'figure'),
                Output('output-hospital-patients-in-system', 'figure'),
                Output('output-hospital-blocking-probability', 'children'),
                Output('output-hospital-recovered', 'children'),
                Output('output-hospital-median-stay', 'children'),
                Output('output-types-of-care', 'figure'),
                Output('output-beds-filled', 'figure'),

                # Button
                Input('submit-val', 'n_clicks'),

                # parameters
                State('simulation_years', 'value'),
                State('opening', 'value'),
                State('closing', 'value'),
                State('weekend', 'value'),
                State('beds', 'value'),
                State('patience', 'value'),
                State('transfer_time', 'value'),
                State('increase_arr', 'value'),
                State('decrease_los', 'value')
              )

def printOutput(_, simulation_year, opening, closing, weekend, beds, patience, transfer_time, increase_arr, decrease_los):

    # Start simulation
    simulation = Simulation(simulation_year, patience, transfer_time, beds, weekend, opening, closing, increase_arr, decrease_los)
    simulation.start()

    P, S = simulation.output()

    S.set_index('datetime', inplace=True)


    # Waiting time
    P['waited'] = P['waiting_time'].gt(0)

    waiting_time_probability = round(P['waited'].mean() * 100, 2) 
    waiting_time_std         = round(P['waiting_time'].std(), 2)
    waiting_time_median      = round(P['waiting_time'].median(), 2)

    w       = P.loc[P['waiting_time'] <= P['waiting_time'].quantile(0.95)]
    f_hist  = px.histogram(w, x="waiting_time")


    # types of care
    pie = P.groupby('care').count()['arrival_time'].reset_index()
    f_pie = px.pie(pie, values = 'arrival_time', names = 'care')
    f_pie.update_traces(textposition = 'inside', textinfo = 'percent')

    # Blocking probability
    blocking_probability = round(P['blocked'].mean() * 100, 2)
    patients_recovered_in_hopsital = P['hospital_recovery'].sum()
    median_time_in_que = round(P['time_in_queue'].median(), 2)

    in_system = S[['hospital_queue', 'STRC']].resample('M').mean().expanding().mean()

    fig_hs = px.line(in_system, x=in_system.index, y='hospital_queue')
    fig_STRC =  px.line(in_system, x=in_system.index, y='STRC')
    # print(in_hospital_queue)


    return (waiting_time_probability, 
            waiting_time_median,
            waiting_time_std,
            f_hist, 
            fig_hs,
            blocking_probability,
            patients_recovered_in_hopsital,
            median_time_in_que,
            f_pie,
            fig_STRC,
            )




if __name__ == '__main__':
    app.run_server(debug=True)
