import numpy as np
import pandas as pd
import streamlit as st
import datetime
import plotly.graph_objects as go
from scipy import integrate


st.title("Drop Jump")
name = st.text_input("Athlete Name")
col1, col2 = st.columns([1, 1])
bwkgs = col1.number_input("Body Weight in lbs")
bwkgs = bwkgs / 2.205
zeroVelocityTime = int(col2.number_input("Input Zero Velocity Time (ms)"))
leftdjfp1 = col1.file_uploader("Upload Left Forceplate", type=["txt"], key=88)
rightdjfp1 = col2.file_uploader("Upload Right Forceplate", type=["txt"], key=89)
graph = go.Figure()

if rightdjfp1 is None:
    st.warning("No Right Forceplate Data")
if leftdjfp1 is None:
    st.warning("No Left Forceplate Data")
if bwkgs == 0:
    st.warning("No Bodyweight")
if leftdjfp1 is not None:
    dfldj1 = pd.read_csv(leftdjfp1, header=(0), sep="\t")
    graph.add_trace(
        go.Scatter(x=dfldj1["Time"], y=dfldj1["Fz"], line=dict(color="red"))
    )
if rightdjfp1 is not None:
    dfrdj1 = pd.read_csv(rightdjfp1, header=(0), sep="\t")
    graph.add_trace(
        go.Scatter(x=dfrdj1["Time"], y=dfrdj1["Fz"], line=dict(color="green"))
    )
if rightdjfp1 is not None and leftdjfp1 is not None:
    tab1, tab2, tab3 = st.tabs(["Force-Time Graph", "Impulse Chart", "Metrics"])
    with tab1:
        st.plotly_chart(graph)
    i = 0
    while dfldj1["Fz"][i] < 10:
        i += 1
    j = 0
    while dfrdj1["Fz"][j] < 10:
        j += 1
    lefttouchdown = i
    righttouchdown = j

    while dfldj1["Fz"][i] > 10:
        i += 1
    while dfrdj1["Fz"][j] > 10:
        j += 1
    lefttakeoff = i
    righttakeoff = j

    if bwkgs != 0:
        netImpulseRInterval = dfrdj1["Fz"][righttouchdown:righttakeoff] - (
            bwkgs * 9.81 / 2
        )
        netImpulseTimeR = dfrdj1["Time"][righttouchdown:righttakeoff]
        netImpulseLInterval = dfldj1["Fz"][lefttouchdown:lefttakeoff] - (
            bwkgs * 9.81 / 2
        )
        netImpulseTimeLInterval = dfldj1["Time"][lefttouchdown:lefttakeoff]

        netImpulseR = integrate.simps(netImpulseRInterval, netImpulseTimeR)
        netImpulseL = integrate.simps(netImpulseLInterval, netImpulseTimeLInterval)
        if zeroVelocityTime != 0:
            concentricImpulseRInterval = dfrdj1["Fz"][zeroVelocityTime:righttakeoff]
            concentricImpulseTimeR = dfrdj1["Time"][zeroVelocityTime:righttakeoff]
            concentricImpulseLInterval = dfldj1["Fz"][zeroVelocityTime:lefttakeoff]
            concentricImpulseTimeLInterval = dfldj1["Time"][
                zeroVelocityTime:lefttakeoff
            ]

            concentricImpulseR = integrate.simps(
                concentricImpulseRInterval, concentricImpulseTimeR
            )
            concentricImpulseL = integrate.simps(
                concentricImpulseLInterval, concentricImpulseTimeLInterval
            )

            eccentricImpulseRInterval = dfrdj1["Fz"][righttouchdown:zeroVelocityTime]
            eccentricImpulseTimeR = dfrdj1["Time"][righttouchdown:zeroVelocityTime]
            eccentricImpulseLInterval = dfldj1["Fz"][lefttouchdown:zeroVelocityTime]
            eccentricImpulseTimeLInterval = dfldj1["Time"][
                lefttouchdown:zeroVelocityTime
            ]

            eccentricImpulseR = integrate.simps(
                eccentricImpulseRInterval, eccentricImpulseTimeR
            )
            eccentricImpulseL = integrate.simps(
                eccentricImpulseLInterval, eccentricImpulseTimeLInterval
            )
    impulsestyle = ["Net Impulse", "Absorption Impulse", "Push-off Impulse"]
    yLeft = [netImpulseL, eccentricImpulseL, concentricImpulseL]
    yRight = [netImpulseR, eccentricImpulseR, concentricImpulseR]
    totaly = np.array(yLeft) + np.array(yRight)
    leftPercentage = np.round(yLeft / totaly * 100, decimals=1)
    rightPercentage = np.round(yRight / totaly * 100, decimals=1)

    chart = go.Figure(
        data=[
            go.Bar(name="Left", x=impulsestyle, y=yLeft, text=(leftPercentage)),
            go.Bar(name="Right", x=impulsestyle, y=yRight, text=(rightPercentage)),
        ]
    )

    # Change the bar mode
    chart.update_layout(barmode="group")
    with tab2:
        st.plotly_chart(chart)
    data = np.array([[name, bwkgs, zeroVelocityTime, netImpulseL, netImpulseR]])

    df = pd.DataFrame(
        data,
        columns=[
            "Name",
            "Weight-kg",
            "Zero Velocity Time",
            "Net Impulse-L",
            "Net Impulse-R",
        ],
    )

    with tab3:
        st.dataframe(df)
