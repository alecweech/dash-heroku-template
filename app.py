import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
## Download and wrangle the ANES data
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')
## Generate the individual tables and figures

### Markdown text
string_of_wisdom = '''### What is the GSS? 
The [gss](https://www.nsf.gov/pubs/2007/nsf0748/nsf0748_3.pdf) is a core set of questions on social attitudes that has been conducted by NORC since 1972. In that time core questions and methodologies have changed. This notebook takes a look at 2019 data from the GSS. It aims to take a representative sample from the US population aged 15 and older. The survey itself is conducted with 90 minute in person interviews and a split-ballot approach, meaning that not all participants will have answered all questions. Core questions include socioeconomic and demographic indicators. Here, we will be using those to take a look at the gender pay gap in the US. 
### Why should I be concerned with a gender pay gap in the US?
According to [pew research](https://www.pewresearch.org/fact-tank/2021/05/25/gender-pay-gap-facts/) the gender pay gap is alive and well in the US. It has shrunk from 36 cents on the dollar in 1986 to 7 cents on the dollar in 2020. Not only that, but it received the plurality of responses in a survey of important issues to be addressed in order to further gender equality in the US. Women continue to be over-represented in lower paying roles and suffer more financially from time taken off for parenting. According to [AAUW](https://www.aauw.org/resources/research/simple-truth/) this issue compunds some of the challenges that marginalized communities in the US face. For example, they project that asian-american women will reach pay equity with non-hispanic white males in 20 years at the current rate. However, for hispanic women, with current trends, that time is over 400 years. This interaction compounds the difficulties that the US has in establishing a just and equitable society. While gender pay discrimination and many other forms of discrimination are illegal, some of them are deeply embedded in our cultural and procedural norms. Monitoring the data can help us get a sense of where our society is now on the gender pay gap, and the actions we can all take to narrow it. '''

### Table
cool_stuff = ['job_prestige', 'income', 'education', 'socioeconomic_index' ]

bar_setup = pd.DataFrame(columns = ['Metric', 'Gender', 'Mean Value'])
for var in cool_stuff:
    male_val = gss_clean.loc[gss_clean['sex'] == 'male'][var].mean()
    mean_male = {'Metric' : var, 'Gender': 'male', 'Mean Value' : male_val}
    female_val = gss_clean.loc[gss_clean['sex'] == 'female'][var].mean()
    mean_female = {'Metric' : var, 'Gender': 'female', 'Mean Value' : female_val}
    bar_setup = bar_setup.append(mean_male, ignore_index = True)
    bar_setup = bar_setup.append(mean_female, ignore_index = True)
prob_2 = ff.create_table(round(bar_setup,2))
setup = gss_clean.groupby(['male_breadwinner', 'sex']).size().reset_index()
setup.columns = ['response', 'sex', 'count']
### Barplot
prob_3 = px.bar(setup, x='response', y='count', color='sex',
             hover_data = ['response', 'count', 'sex'],
            labels={'vote':'Vote choice', 'colpercent':'Percent'},
            text='response', barmode = 'group')
prob_3.update(layout=dict(title=dict(x=0.5)))
prob_3.update_layout(showlegend=True)
prob_4 = px.scatter(gss_clean.head(1000), x='job_prestige', y='income', 
                 color = 'sex', 
                 height=600, width=600,
                 labels={'ftbiden':'Joe Biden thermometer rating', 
                        'fttrump':'Donald Trump thermometer rating'},
                 hover_data=['sex', 'income', 'job_prestige',
                            'education', 'socioeconomic_index'],
                trendline = 'lowess')
prob_4.update(layout=dict(title=dict(x=0.5)))
prob_5 = px.box(gss_clean, x='income', color ='sex',
                   labels={'income':'income distribution', 'sex':''},
                   hover_data = ['income'])
prob_5.update_layout(showlegend = False)
prob_5_2 = px.box(gss_clean, x='job_prestige', color ='sex',
                   labels={'job_prestige':'prestige score', 'sex': ''})
prob_5_2.update_layout(showlegend = False)
group_names = ['Lowest Prestige', 'Low Prestige', 'Low Middle',
              'High Middle', 'High Prestige', 'Highest Prestige']
neat_stuff = gss_clean[['income', 'sex', 'job_prestige']]
neat_stuff['prestige_group'] = pd.cut(gss_clean['job_prestige'], bins = 6,
                                     labels = group_names)
neat_stuff = neat_stuff.dropna()

prob_6 = px.box(neat_stuff, x = 'income',color = 'sex',
             facet_col = 'prestige_group', facet_col_wrap = 3,
            color_discrete_map = {'male':'blue', 'female':'red'},
               )
prob_6.update(layout=dict(title=dict(x=0.5)))
prob_6.update_layout(showlegend=False)
prob_6.for_each_annotation(lambda a: \
                        a.update(text=a.text.replace("prestige_group=", "")))
metrics = ['satjob',
'relationship', 
'male_breadwinner',
'men_bettersuited',
'child_suffer',
'men_overwork']
groupings = ['sex', 'region', 'education']
group_names = ['Lowest Prestige', 'Low Prestige', 'Low Middle',
              'High Middle', 'High Prestige', 'Highest Prestige']
neat_stuff = gss_clean[['income', 'sex', 'job_prestige']]
neat_stuff['prestige_group'] = pd.cut(gss_clean['job_prestige'], bins = 6,
                                     labels = group_names)
neat_stuff = neat_stuff.dropna()

prob_6 = px.histogram(neat_stuff, x = 'income', color = 'sex',
             facet_col = 'prestige_group', facet_col_wrap = 3,
            color_discrete_map = {'male':'blue', 'female':'red'})
prob_6.update(layout=dict(title=dict(x=0.5)))
prob_6.for_each_annotation(lambda a: \
                        a.update(text=a.text.replace("prestige_group=", "")))

app2 = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app2.layout = html.Div(
    [
        html.H1("Exploring the results of the General Social Survey"),
        
        dcc.Markdown(children = string_of_wisdom),
        
        html.H2("Metrics by gender: The numbers"),
        
        dcc.Graph(figure=prob_2),
        
        html.H2("Gender attitudes expressed across the survey"),
        
        html.Div([
            
            html.H3("Metric"),
            
            dcc.Dropdown(id='dd1',
                         options=[{'label': i, 'value': i} for i in metrics],
                         value='men_overwork'),
            
            html.H3("Grouping"),
            
            dcc.Dropdown(id='dd2',
                         options=[{'label': i, 'value': i} for i in groupings],
                         value='sex')
        
        ],style={'width': '25%', 'float': 'left'}),
        
        html.Div([
            
            dcc.Graph(id="graph1")
        
        ], style={'width': '70%', 'float': 'right'}),
        
        html.H2("Prestige and Income relationships by gender"),
        
        dcc.Graph(figure=prob_4),
        
        html.Div([
            
            html.H2("Income Distribution by gender"),
            
            dcc.Graph(figure=prob_5)
            
        ], style = {'width':'48%', 'height':'10%', 'float':'left'}),
        
        html.Div([
            
            html.H2("Job Prestige distribution by gender"),
            
            dcc.Graph(figure=prob_5_2)
            
        ], style = {'width':'48%', 'height':'10%',  'float':'right'}),
        
        html.H2("Income distribution by prestige group"),
        
        dcc.Graph(figure=prob_6)
        
    
    ]
)
@app2.callback(Output("graph1","figure"), 
                  [Input('dd1',"value"),
                   Input('dd2',"value")])
def update_img_src(Metric, Grouping):
    setup = gss_clean.groupby([Metric, Grouping]).size().reset_index()
    setup.columns = ['response', 'grouping', 'count']
    figure = px.bar(setup, x='response', y='count', color='grouping',hover_data = ['response', 'count', 'grouping'],text='response', barmode = 'group')
    return figure


if __name__ == '__main__':
    app2.run_server(debug=True, port=8051, host='0.0.0.0')
