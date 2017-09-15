# -*- coding: utf-8 -*-
# library to manage services like alexa rank, moz
# Nicolas Lorenzon - nicolas@lorenzon.ovh - http://www.lorenzon.ovh

import urllib.request
import lib_bd
import bs4
from pyscape import Pyscape
import requests
import time
from pyquery import PyQuery as pq
import re
import os


# Fonction qui va lire un fichier et retourner toutes les lignes
def lireFichier(fichier):
    with open(fichier, encoding='utf-8') as f:
        content = f.readlines()
    return content


# lecture du fichier de configuration s'il existe
# renvoie un couple d'éléments : site et config
def readConfig():
    moz_access_id = ""
    moz_secret_key = ""

    if (os.path.isfile("config.cfg")):
        #print("fichier config trouvé")
        contenu = lireFichier("config.cfg")
        #print(contenu)
        for ligne in contenu:
            # on regarde si on trouve les mots clés
            if ("MOZ_ACCESS_ID=" in ligne):
                moz_access_id = ligne.replace("MOZ_ACCESS_ID=", "").replace("\n", "").replace(" ", "")
            if ("MOZ_SECRET_KEY=" in ligne):
                moz_secret_key = ligne.replace("MOZ_SECRET_KEY=", "").replace("\n", "").replace(" ", "")
    else:
        print("fichier config non trouvé")

    return moz_access_id, moz_secret_key


# lecture config pour les requêtes google
def readConfigGoogle():
    # valeurs par défaut
    moteur = "www.google.fr"
    selecteur = "#resultStats"
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'
    if (os.path.isfile("config.cfg")):
        #print("fichier config trouvé")
        contenu = lireFichier("config.cfg")
        #print(contenu)
        for ligne in contenu:
            # on regarde si on trouve les mots clés
            if ("GOOGLE=" in ligne):
                moteur = ligne.replace("GOOGLE=", "").replace("\n", "").replace(" ", "")
            if ("GOOGLE_SELECTOR=" in ligne):
                selecteur = ligne.replace("GOOGLE_SELECTOR=", "").replace("\n", "").replace(" ", "")
            if ("USER_AGENT=" in ligne):
                userAgent = ligne.replace("USER_AGENT=", "").replace("\n", "").replace(" ", "")
    else:
        print("fichier config non trouvé")

    return moteur, selecteur, userAgent


def getAlexaRank(basedonnees, url, id_site):
    url = "http://data.alexa.com/data?cli=10&dat=s&url=" + str(url)
    html_page = urllib.request.urlopen(url).read()
    retour = ""
    try:
        rank = bs4.BeautifulSoup(html_page, "xml").find("REACH")['RANK']
    except:
        rank = "?"
        retour = "Problem reading Alexa Rank (no rank ?)"
    lib_bd.addIndicateur(basedonnees, id_site, "alexa", str(rank))
    return retour


def getMoz(basedonnees, url, id_site):
    moz_access_id, moz_secret_key = readConfig()
    #print(moz_access_id)
    #print(moz_secret_key)
    keys = {
        "access_id": moz_access_id,
        "secret_key": moz_secret_key
    }
    mozda = "?"
    mozpa = "?"
    mozlinks = "?"
    retour = ""
    if (moz_access_id != "" and moz_secret_key != ""):
        try:
            p = Pyscape(**keys)
            resultat = p.get_url_metrics(url).json()
            mozda = str(round(resultat["pda"], 0))
            mozpa = str(round(resultat["upa"], 0))
            mozlinks = str(resultat["uid"])
        except:
            p = ""
            retour = "Problem reading Moz Rank (have you correctly configured config.cfg ?)"
    # ajout dans la base de données
    lib_bd.addIndicateur(basedonnees, id_site, "mozda", mozda)
    lib_bd.addIndicateur(basedonnees, id_site, "mozpa", mozpa)
    lib_bd.addIndicateur(basedonnees, id_site, "mozlinks", mozlinks)
    return retour


def requete_google(query, moteur, userAgent):
    link = 'http://' + moteur + '/search?ie=ISO-8859-1&hl=fr&source=hp&biw=&bih=&gbv=1&q=' + str(query)
    ua = {'User-Agent': userAgent, 'Cache-control': 'max-age=0', 'Connection': 'keep-alive', 'Accept-Language' : 'fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3', 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    payload = {'q': query}
    response = requests.get(link, headers=ua, params=payload)
    contenu = response.text
    time.sleep(5)
    return contenu


def pages_indexees(basedonnees, url, id_site):
    moteur, selecteur, userAgent = readConfigGoogle()
    #print(moteur, selecteur, userAgent)
    retour = ""
    try:
        contenu = requete_google("site:" + str(url), moteur, userAgent)
    except:
        contenu = "?"
        retour = "Problem with Google request"
    d = pq(contenu)
    texte = d(selecteur)
    texte = texte.html()
    #print(texte)
    if (texte is None):
        lib_bd.addIndicateur(basedonnees, id_site, "ggindexed", str("0"))
    else:
        try:
            texte3 = " ".join(re.findall(r'\d+', texte))
        except:
            texte3 = "?"
        lib_bd.addIndicateur(basedonnees, id_site, "ggindexed", str(texte3))
    return retour
