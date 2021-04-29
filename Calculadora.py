import pandas as pd
#from tkinter import *
#from tkinter.ttk import Combobox
import datetime as dt
import numpy as np
#window=Tk()
# add widgets here

def Value_at_Risk(TimeSeries, alpha):
    TS = TimeSeries.sort_values()
    n = alpha * (len(TimeSeries) + 1) - 1
    assert n > 0, 'Datos insuficientes... (Alfa muy pequeña)'
    n_1 = int(n)
    return TS.iat[n_1] + (TS.iat[n_1 + 1] - TS.iat[n_1]) * (n - n_1)

"""
var = StringVar()
var.set("one")
data=("one", "two", "three", "four")
cb=Combobox(window, values=data)
cb.place(x=60, y=150)

lb=Listbox(window, height=5, selectmode='multiple')
for num in data:
    lb.insert(END,num)
lb.place(x=250, y=150)

v0=IntVar()
v0.set(1)
r1=Radiobutton(window, text="male", variable=v0,value=1)
r2=Radiobutton(window, text="female", variable=v0,value=2)
r1.place(x=100,y=50)
r2.place(x=180, y=50)
                
v1 = IntVar()
v2 = IntVar()
C1 = Checkbutton(window, text = "Cricket", variable = v1)
C2 = Checkbutton(window, text = "Tennis", variable = v2)
C1.place(x=100, y=100)
C2.place(x=180, y=100)

window.title('Calculadora')
window.geometry("400x300+10+10")
window.mainloop()
"""
Fecha = dt.date(2021,4,28)
alpha = .008

IE = pd.read_excel("A:/Motor de Riesgos/Calculadora/" + Fecha.strftime("%Y%m%d") + "_BCOT0.xlsx",sheet_name = "IE")
IE.drop(columns=IE.columns[:13],axis=1,inplace=True)
IE.set_index("LLAVE",inplace=True)
aux = pd.DataFrame(index = IE.index)
IC = pd.DataFrame(index= IE.index)
ICL = pd.DataFrame(index= IE.index)
IC_ICL = pd.DataFrame(index = IE.index)
ICScta = pd.DataFrame(index=IE.index)
ICLScta = pd.DataFrame(index=IE.index)
IC_ICL_Scta = pd.DataFrame(index=IE.index)

Port = pd.read_excel("A:/Motor de Riesgos/Calculadora/Portafolio.xlsx")
Port.fillna('', inplace=True)
Port["LLAVE"] = Port.USI.map(lambda x:x if x=="" else str(int(x))[-12:]) + Port.Clase + Port["Clase Real"] + Port.Serie + Port["C/P"] + Port.Ejercicio.map(lambda x: x if x=="" else str(x))
Port.set_index("LLAVE", inplace=True)
Port["LC"] = Port.Larga - Port.Corta
Port["ELC"] = Port["Entrega Larga"] - Port["Entrega Corta"]
Port["SocioCuenta"] = Port["Socio Liquidador"] + "_" + Port["Cuenta"].map(lambda x: str(x))
Port["Total"] = Port["LC"] + Port["ELC"]
Port["EstCuenta"] = Port['Socio Liquidador'] + "_" + Port['Operador'] + "_" + Port['Tipo de Cuenta'] + "_" + Port['Cuenta'].map(lambda x: str(x)) + "_" + Port['Subcuenta'].map(lambda x: str(x))

#####################################################
####################Nivel Cuenta#####################
#####################################################

Vigentes = Port.loc[Port["LC"] != 0][["SocioCuenta","EstCuenta","LC"]]
for i in Vigentes.SocioCuenta.unique():
    IC[i] = pd.concat([aux, Vigentes.LC[Vigentes.SocioCuenta == i]], axis=1)

Entrega = Port.loc[Port.ELC != 0][["SocioCuenta","EstCuenta","ELC"]]
for i in Entrega.SocioCuenta.unique():
    ICL[i] = pd.concat([aux, Entrega.ELC[Entrega.SocioCuenta == i]], axis=1)

for i in Vigentes.EstCuenta.unique():
    ICScta[i] = pd.concat([aux,Vigentes.LC[Vigentes.EstCuenta == i]], axis = 1)
    
for i in Entrega.EstCuenta.unique():
    ICLScta[i] = pd.concat([aux,Entrega.ELC[Entrega.EstCuenta == i]], axis = 1)


ICporIE = pd.DataFrame(np.matmul(IC.fillna(0).to_numpy().transpose() , IE.drop(columns=IE.columns[:2],axis=1).fillna(0).to_numpy()))
ICporIE.set_index(Vigentes.SocioCuenta.unique(), inplace=True)
ICporIE.columns = IE.columns[2:]

ICLporIE = pd.DataFrame(np.matmul(ICL.fillna(0).to_numpy().transpose() , IE.drop(columns=IE.columns[:2],axis=1).fillna(0).to_numpy()))
ICLporIE.set_index(Entrega.SocioCuenta.unique(), inplace=True)
ICLporIE.columns = IE.columns[2:]

ICSctaporIE = pd.DataFrame(np.matmul(ICScta.fillna(0).to_numpy().transpose(), IE.drop(columns=IE.columns[:2],axis=1).fillna(0).to_numpy()))
ICSctaporIE.set_index(Vigentes.EstCuenta.unique(), inplace=True)
ICSctaporIE.columns = IE.columns[2:]

ICLSctaporIE = pd.DataFrame(np.matmul(ICLScta.fillna(0).to_numpy().transpose(), IE.drop(columns=IE.columns[:2],axis=1).fillna(0).to_numpy()))
ICLSctaporIE.set_index(Entrega.EstCuenta.unique(), inplace=True)
ICLSctaporIE.columns = IE.columns[2:]

###############################################################################
Riesgo = []
for i in Vigentes.SocioCuenta.unique():
    Var = Value_at_Risk(ICporIE.loc[i],alpha)
    Riesgo.append(-ICporIE.loc[i][ICporIE.loc[i]<Var].mean())

Riesgo = pd.DataFrame(Riesgo,columns = ["AIM_Riesgo"])
Riesgo.set_index(Vigentes.SocioCuenta.unique(), inplace=True)

Entreg_aux = []
for i in Entrega.SocioCuenta.unique():
    Var = Value_at_Risk(ICLporIE.loc[i],alpha)
    Entreg_aux.append(-ICLporIE.loc[i][ICLporIE.loc[i]<Var].mean())

Entreg_aux = pd.DataFrame(Entreg_aux,columns = ["AIM_Entrega"])
Entreg_aux.set_index(Entrega.SocioCuenta.unique(), inplace=True)


for i in Port.SocioCuenta.unique():
    IC_ICL[i] = pd.concat([aux, Port.Total[Port.SocioCuenta == i]], axis=1)
Prima = np.asarray([IE.PRIMA.fillna(0)]).transpose() * np.asarray(IC_ICL.fillna(0))
Prima = pd.DataFrame(Prima)
Prima.set_index(IE.index,inplace=True)
Prima.columns = Port.SocioCuenta.unique()

Prima_aux = []
for i in Port.SocioCuenta.unique():
    Prima_aux.append(-Prima[i].sum())
    
Prima_aux = pd.DataFrame(Prima_aux,columns=["AIM_Prima"])
Prima_aux.set_index(Port.SocioCuenta.unique(),inplace=True)

AIMs = pd.DataFrame(index = Port.SocioCuenta.unique())
AIMs["AIM Riesgo"] = pd.concat([aux,Riesgo.AIM_Riesgo],axis=1)
AIMs["AIM Entrega"] = pd.concat([aux,Entreg_aux.AIM_Entrega],axis=1)
AIMs["AIM Prima"] = pd.concat([aux,Prima_aux.AIM_Prima],axis=1)
AIMs = AIMs.fillna(0)
AIMs["AIM Cuenta"] = AIMs["AIM Riesgo"] + AIMs["AIM Entrega"] + AIMs["AIM Prima"]
AIMs["SocioCuenta"] = AIMs.index
###############################################################################

#Escenarios Vigentes
ES_Scenarios = pd.Series()
for ID in Vigentes.SocioCuenta.unique():
    Array = pd.DataFrame()
    Array["P&L"] = ICporIE.loc[ID].sort_values()
    Array['Escenarios'] = Array.index
    Array['SocioCuenta'] = ID
    temp = Array[Array['P&L']<Value_at_Risk(Array['P&L'],alpha)]
    ES_Scenarios = pd.concat([ES_Scenarios,temp],0)

Escenarios_EC = pd.DataFrame()
for EC in Vigentes.EstCuenta.unique():
    temp1 = pd.DataFrame(ES_Scenarios.Escenarios[ES_Scenarios.SocioCuenta == Vigentes.SocioCuenta[Vigentes.EstCuenta == EC].unique()[0]])
    temp1["EC"] = EC
    Escenarios_EC  = Escenarios_EC.append(temp1)
    
temp = []
for i in range(len(Escenarios_EC)):
    temp.append(ICSctaporIE[Escenarios_EC.Escenarios[i]][Escenarios_EC.EC[i]])
Escenarios_EC["P&L"] = temp  

temp_e = []
for EC in Escenarios_EC.EC.unique():
    temp_e.append(-Escenarios_EC["P&L"][Escenarios_EC.EC == EC].mean())
temp_e = pd.DataFrame(temp_e, index=Escenarios_EC.EC.unique(),columns=["AIM_Riesgo_Scta"])
temp_e["EstCuenta"] = temp_e.index

#Escenarios Entrega
ESL_Scenarios = pd.Series()
for ID in Entrega.SocioCuenta.unique():
    Array = pd.DataFrame()
    Array["P&L"] = ICLporIE.loc[ID].sort_values()
    Array['Escenarios'] = Array.index
    Array['SocioCuenta'] = ID
    temp = Array[Array['P&L']<Value_at_Risk(Array['P&L'],alpha)]
    ESL_Scenarios = pd.concat([ESL_Scenarios,temp],0)

Escenarios_ECL = pd.DataFrame()
for EC in Entrega.EstCuenta.unique():
    temp1 = pd.DataFrame(ESL_Scenarios.Escenarios[ESL_Scenarios.SocioCuenta == Entrega.SocioCuenta[Entrega.EstCuenta == EC].unique()[0]])
    temp1["EC"] = EC
    Escenarios_ECL  = Escenarios_ECL.append(temp1)
    
temp = []
for i in range(len(Escenarios_ECL)):
    temp.append(ICLSctaporIE[Escenarios_ECL.Escenarios[i]][Escenarios_ECL.EC[i]])
Escenarios_ECL["P&L"] = temp  

temp_el = []
for EC in Escenarios_ECL.EC.unique():
    temp_el.append(-Escenarios_ECL["P&L"][Escenarios_ECL.EC == EC].mean())
temp_el = pd.DataFrame(temp_el,index=Escenarios_ECL.EC.unique(),columns=["AIM_Entrega_Scta"])
temp_el["EstCuenta"] = temp_el.index



##AIM PRIMA SUBCUENTA##
for i in Port.EstCuenta.unique():
    IC_ICL_Scta[i] = pd.concat([aux, Port.Total[Port.EstCuenta == i]], axis=1)
Prima_Scta = np.asarray([IE.PRIMA.fillna(0)]).transpose() * np.asarray(IC_ICL_Scta.fillna(0))
Prima_Scta = pd.DataFrame(Prima_Scta)
Prima_Scta.set_index(IE.index,inplace=True)
Prima_Scta.columns = Port.EstCuenta.unique()


Prima_aux1 = []
for i in Port.EstCuenta.unique():
    Prima_aux1.append(-Prima_Scta[i].sum())
       

Prima_aux1 = pd.DataFrame(Prima_aux1,columns=["AIM_Prima_Scta"])
Prima_aux1.set_index(Port.EstCuenta.unique(),inplace=True)

#######


AIMs_EC = pd.DataFrame(Port.EstCuenta.unique(),columns=["EstCuenta"], index = Port.EstCuenta.unique())
AIMs_EC = pd.merge(AIMs_EC, temp_e, how="outer", on = "EstCuenta")
AIMs_EC = pd.merge(AIMs_EC,temp_el, how="outer", on = "EstCuenta")
AIMs_EC.set_index("EstCuenta", inplace=True)
AIMs_EC["AIM_Prima_Scta"] = Prima_aux1.AIM_Prima_Scta
AIMs_EC = AIMs_EC.fillna(0)
AIMs_EC["Contribución AIM Subcuenta"] = AIMs_EC['AIM_Riesgo_Scta'] + AIMs_EC['AIM_Entrega_Scta'] + AIMs_EC['AIM_Prima_Scta']
#AIMs_EC["EstCuenta"] = AIMs_EC.index

DetalleAIM = Port.merge(AIMs, how="outer", on = "SocioCuenta")
DetalleAIM = DetalleAIM.merge(AIMs_EC, how="outer", on = "EstCuenta")

DetalleAIM = DetalleAIM[['Socio Liquidador', 'Operador', 'Tipo de Cuenta', 'Cuenta', 'Subcuenta','Contribución AIM Subcuenta','AIM Cuenta']]



