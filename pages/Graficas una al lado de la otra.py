import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from numerize.numerize import numerize
#---- Variables ----
vLine_color='#edf6f9'
vBar_Color='#0077b6'
vHeight=350

#---- Extraccion de datos ----
@st.cache_data
def get_data_excel():
    df_ventas=pd.read_excel(io='ventaDef.xlsx',sheet_name='venta',engine="openpyxl")
    df_metas=pd.read_excel('ventaDef.xlsx',sheet_name='Metas',engine="openpyxl")
    # Add fields Year,Month and Day
    df_ventas['Año']=df_ventas['Fecha'].dt.year
    df_ventas['Mes']=df_ventas['Fecha'].dt.month
    df_ventas['Dia']=df_ventas['Fecha'].dt.day
    df_ventas['Periodo']=df_ventas['Fecha'].dt.strftime('%Y-%m')
    #Anexar df metas a df ventas por periodo
    df=pd.merge(df_ventas,df_metas,on='Periodo')
    return df

st.set_page_config(page_title="Portafolio",
                   page_icon=":tada:",
                   layout="wide")
df= get_data_excel()

#----Filtros----
columns1,columns2,columns3,columns4,columns5 = st.columns(5)
with columns1 :
     f_departamento=st.multiselect(
     "Departamento",
    options=df["departamento"].unique(),
    #default=df["departamento"].unique()
)

with columns2:
     f_periodo=st.multiselect(
     "Periodo",
    options=df["Periodo"].unique(),
    #default=df["periodo"].unique()
)     

with columns3: 
     f_vendedor=st.multiselect(
     "Vendedor",
    options=df["Vendedor"].unique(),
    #default=df["Vendedor"].unique()
)
         
with columns4: 
     f_tipo_venta=st.multiselect(
     "Clasifica",
    options=df["Tipo de venta"].unique(),
    #default=df["Tipo de venta"].unique()
)       
with columns5:
     f_ciudad=st.multiselect(
     "Ciudad",
     options=df["ciudad"].unique(),
     #default="All",
)

# Verificar si se aplicaron filtros o no
if f_departamento or f_ciudad or f_tipo_venta or f_vendedor or f_periodo:
    # Aplicar filtros
    df_filtros = df.query("(departamento == @f_departamento) | (ciudad == @f_ciudad) | (`Tipo de venta` == @f_tipo_venta) | (Vendedor == @f_vendedor) | (Periodo == @f_periodo)")
    #Variables filtro años
else:
    # Conservar todos los datos sin filtrar
    df_filtros = df.copy()
    #Variables filtro años

vAño_Anterior = df.Año.max()-1 if df.Año.max()-1 != df.Año.max()-1 else df.Año.max()
vAño_Actual=df.Año.max() if df.Año.max() != df.Año.max() else df.Año.max()-1

vAño_Actual = df_filtros["Año"].max() if df_filtros["Año"].max() != 1 else 1

#---Metricas----
Venta_Act=int(round(df_filtros.query("Año==@vAño_Actual").groupby("Año").agg({"Venta":"sum"}).iloc[0,0]))
Venta_Ant=int(round(df_filtros.query("Año==@vAño_Anterior").groupby("Año").agg({"Venta":"sum"}).iloc[0,0]))
Costo_Act=int(round(df_filtros.query("Año==@vAño_Actual").groupby("Año").agg({"CostoP":"sum"}).iloc[0,0]))
Costo_Ant=int(round(df_filtros.query("Año==@vAño_Anterior").groupby("Año").agg({"CostoP":"sum"}).iloc[0,0]))
Margen_Bruto_Act=Venta_Act-Costo_Act
Margen_Bruto_Ant=Venta_Ant-Costo_Ant
N_Productos_Act=int(round(df_filtros.query("Año==@vAño_Actual").groupby("Año").agg({"Producto":"count"}).iloc[0,0]))
N_Productos_Ant=int(round(df_filtros.query("Año==@vAño_Anterior").groupby("Año").agg({"Producto":"count"}).iloc[0,0]))
Producto_avg_Act=Venta_Act / N_Productos_Act
Producto_avg_Ant=round(Venta_Ant / N_Productos_Ant)
Objetivo_ventas_act=3466328100

#----Calculo crecimiento por año----
crecimiento_venta=1-((Venta_Act-Venta_Ant)/Venta_Act) *100
crecimiento_costo=1-((Costo_Act-Costo_Ant)/Costo_Act) *100
crecimiento_margen=((Margen_Bruto_Act/Margen_Bruto_Ant)-1) *100
crecimiento_avg_producto=1-((Producto_avg_Act-Producto_avg_Ant)/Producto_avg_Act) *100
crecimiento_objetivo=((Venta_Act/Objetivo_ventas_act)-1) *100
#---- KPIS ----
column_1,column_2,column_3,column_4,column_5 = st.columns(5)
vMes_Actual_texto=''
column_1.metric(label="Ventas", value=f"{numerize(Venta_Act)}", delta=f"vs prev ={numerize(Venta_Ant)} ({crecimiento_venta*100:.0f}%)")
column_2.metric(label="Costos", value=f"{numerize(Costo_Act)}", delta=f"vs prev ={numerize(Costo_Ant)} ({crecimiento_costo*100:.0f}%)")
column_3.metric(label="Margen Bruto", value=f"{numerize(Margen_Bruto_Act)}", delta=f"{crecimiento_margen:.0f}%")
column_4.metric(label="Avg Producto", value=f"{numerize(Producto_avg_Act)}", delta=f"{crecimiento_avg_producto*100:.0f}%")
column_5.metric(label="Objetivo Venta Año actual", value=f"{numerize(Objetivo_ventas_act)}", delta=f"{crecimiento_objetivo:.2f}%")

# Agrupar los datos y calcular las sumas
df_ventas_por_periodo=(df_filtros.groupby("Periodo").agg({"Venta":"sum"}).reset_index())
df_ventas_por_periodo=df_ventas_por_periodo.fillna(0)
# Calcular el crecimiento porcentual de las ventas
df_ventas_por_periodo["Crecimiento"] = 0
for i in range(1, len(df_ventas_por_periodo)):
    venta_actual = df_ventas_por_periodo.loc[i, "Venta"]
    venta_anterior = df_ventas_por_periodo.loc[i - 1, "Venta"]
    crecimiento = (((venta_actual/venta_anterior))-1 )*100
    df_ventas_por_periodo.loc[i, "Crecimiento"] = crecimiento

sales_by_periodo = df_ventas_por_periodo
sales_by_periodo['Crecimiento']=sales_by_periodo['Crecimiento'].apply('{:,.2f}'.format)
#LINE CHART --- Sales by periodo
# Crear el gráfico combinado de barras y línea
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Bar(
        x=sales_by_periodo["Periodo"],
        y=sales_by_periodo["Venta"],
        name='Venta',
        marker=dict(color=vBar_Color)
    ),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(
        x=sales_by_periodo["Periodo"],
        y=sales_by_periodo["Crecimiento"],
        name='Crecimiento',
        mode='lines+markers',
        line=dict(color=vLine_color),  # Utilizar el último color del gradiente para la línea de desempeño
    ),
    secondary_y=True
)
# Configurar los ejes y los títulos
fig.update_layout(
    title="<b>Evolución de ventas y crecimiento(%)</b>",
    yaxis=dict(title='Venta',showticklabels=False),
    yaxis2=dict(title='Crecimiento', side='right'),
    height=vHeight
)
# Mostrar el gráfico en Streamlit
left_column, right_columns = st.columns(2)
with left_column:
    left_column.plotly_chart(fig, use_container_width=True)

# DESEMPEÑO POR PRODUCTO DF
with right_columns:
    venta_producto = df_filtros[["Producto", "Venta"]]
    venta_total = df_filtros.Venta.sum()
    venta_producto = venta_producto.groupby('Producto').agg({'Venta': 'sum'})
    venta_producto = venta_producto.sort_values(by=['Venta'], ascending=False).reset_index()
    venta_producto['Desempeño'] = venta_producto['Venta'] / venta_total * 100
    venta_producto['Desempeño'] =venta_producto['Desempeño'].apply('{:,.2f}'.format)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=venta_producto["Producto"],
            y=venta_producto["Venta"],
            name='Venta',
            marker=dict(color=vBar_Color)
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=venta_producto["Producto"],
            y=venta_producto["Desempeño"],
            name='Desempeño (%)',
            mode='lines+markers',
            line=dict(color=vLine_color),  # Utilizar el último color del gradiente para la línea de desempeño     
        ),
        secondary_y=True
    )
    # Configurar los ejes y los títulos
    fig.update_layout(
        title="<b>Ventas por producto y desempeño(%)</b>",
        xaxis=dict(title='Producto', tickangle=-45),  # Añadir tickangle para cambiar la orientación de las etiquetas
        yaxis2=dict(title='Desempeño (%)', side='right'),
        height=vHeight
    )
    right_columns.plotly_chart(fig, use_container_width=True)

left_column,right_columns =st.columns(2)
with left_column:
    df=df_filtros.groupby('departamento').agg({'Venta':'sum'}).sort_values(by='Venta',ascending=False).reset_index().iloc[0:10]
    df['Venta']=df['Venta']/1000000
    fig = px.funnel(df,x='Venta',y='departamento')
    fig.update_layout(
        title="<b>Top 10 Ventas por departamento (Millones)</b>",
        height=vHeight
    )
    left_column.plotly_chart(fig,use_container_width=True)

with right_columns:
        #----Dataframe ventas por vendedor----
        df = df_filtros[['Vendedor','Periodo','Venta']]
        df=df.groupby(['Periodo','Vendedor']).agg({'Venta':'sum'}).reset_index()
        df['Venta']=round(df['Venta']/1000000,2)
        fig =go.Figure(go.Heatmap(
            z=df['Venta'],
            y=df['Vendedor'],
            x=df['Periodo'],
            colorscale='Viridis'
        ))
        fig.update_layout(
        title="<b>Mapa de Calor de Ventas(Millones) por Periodo y Vendedor</b>",
        yaxis=dict(title='Vendedor'),
        xaxis=dict(title='Departamento', tickangle=-45),  # Añadir tickangle para cambiar la orientación de las etiquetas
        yaxis2=dict(title='Desempeño (%)', side='right'),
        height=vHeight
    )   
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        right_columns.plotly_chart(fig,use_container_width=True)
