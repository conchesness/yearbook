from app import app
from app.classes.data import OTSeniors
from flask import redirect
import os
import pandas as pd

@app.route('/importseniors')
def importseniors():
    # This reads a csv file in to a dataframe
    df_srs = pd.read_csv('srs.csv')
    df_srs.fillna('', inplace=True)
    #  This turns that dataframe in to a python dictionary
    srs = df_srs.to_dict(orient='records')

    for i,sr in enumerate(srs):
        newOTSenior = OTSeniors(
            aeriesid=sr['aeriesid'],
            ousdemail=sr['ousdemail']
        )
        newOTSenior.save()
        print(f"{i}: {sr['ousdemail']}")

    return redirect('/')