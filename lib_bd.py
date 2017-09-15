# -*- coding: utf-8 -*-
# library to manage SQLITE3 database
# Nicolas Lorenzon - nicolas@lorenzon.ovh - http://www.lorenzon.ovh

import sqlite3

# connect to sqlite3 database
def connexionBase(basedonnees):
    conn = sqlite3.connect(basedonnees)
    return conn

# format text before insert in database
def prepareExpression(expression):
    return expression.replace("\"", "\"\"").strip()

# get all records from database
def lectureTous(basedonnees):
    conn = connexionBase(basedonnees)
    requete = "SELECT * FROM data ORDER BY last_update DESC;"
    cursor = conn.execute(requete)
    tableau = list()
    for ligne in cursor:
        tableau.append(ligne)
    return tableau

# get all records for listbox
def lectureTousListBox(basedonnees):
    conn = connexionBase(basedonnees)
    requete = "SELECT id,url,name FROM data ORDER BY url;"
    cursor = conn.execute(requete)
    tableau = list()
    for ligne in cursor:
        tableau.append(ligne)
    return tableau

# trouve tous enregistrements pour les actions
def lectureToutesActions(basedonnees):
    conn = connexionBase(basedonnees)
    requete = "SELECT actions.id, actions.url, actions.date, actions.comment, backlink, data.url as url_site FROM actions JOIN data ON actions.site_id = data.id ORDER BY actions.date DESC;"
    cursor = conn.execute(requete)
    tableau = list()
    for ligne in cursor:
        tableau.append(ligne)
    return tableau

# trouve tous enregistrements pour les actions
def lectureToutesActionsForSite(basedonnees, id_site):
    conn = connexionBase(basedonnees)

    if id_site is None:
        requete = "SELECT actions.id, actions.url, actions.date, actions.comment, backlink, data.url as url_site FROM actions JOIN data ON actions.site_id = data.id ORDER BY actions.date DESC;"
    else:
        requete = "SELECT actions.id, actions.url, actions.date, actions.comment, backlink, data.url as url_site FROM actions JOIN data ON actions.site_id = data.id WHERE actions.site_id = \"" + str(id_site) + "\" ORDER BY actions.date DESC;"
    cursor = conn.execute(requete)
    tableau = list()
    for ligne in cursor:
        tableau.append(ligne)
    return tableau

# pour lire une seule action
def lectureUneAction(basedonnees, id_action):
    conn = connexionBase(basedonnees)
    conn.row_factory = dict_factory
    requete = "SELECT * FROM actions WHERE id = \"" + str(id_action) + "\""
    cursor = conn.execute(requete)
    return cursor.fetchone()

# retourne un id de site en fonction de son url
def getIdForSite(basedonnees, url):
    conn = connexionBase(basedonnees)
    requete = "SELECT id FROM data WHERE url = \"" + str(url) + "\""
    cursor = conn.execute(requete)
    for ligne in cursor:
        return ligne[0]
        break
    return ""

# retourne l'url pour un id de site
def getUrlForId(basedonnees, id_site):
    conn = connexionBase(basedonnees)
    requete = "SELECT url FROM data WHERE id = \"" + str(id_site) + "\""
    cursor = conn.execute(requete)
    for ligne in cursor:
        return ligne[0]
        break
    return ""

# va initialiser le tableau pour un site (indicateurs)
def initDicIndicateur():
    tableau = {}
    tableau['alexa'] = "?"
    tableau['mozlinks'] = "?"
    tableau['mozda'] = "?"
    tableau['mozpa'] = "?"
    tableau['ggindexed'] = "?"
    return tableau

# va récupérer les indicateur d'un site
def lectureIndicateursForSite(basedonnees, site):
    conn = connexionBase(basedonnees)
    requete = "SELECT name, value FROM indicateurs WHERE id_site = \"" + str(site) + "\" ;"
    cursor = conn.execute(requete)
    tableau = initDicIndicateur()
    for ligne in cursor:
        tableau[ligne[0]] = ligne[1]
    return tableau

# ajoute indicateur (pas d'historique, on supprimer l'ancienne valeur)
def addIndicateur(basedonnees, id_site, name, value):
    conn = connexionBase(basedonnees)
    # suppression ancienne valeur
    conn.execute("DELETE FROM indicateurs WHERE id_site = \"" + str(id_site) + "\" AND name=\""+ str(name) + "\" ;" )
    # ajout de la nouvelle valeur
    requete = "INSERT INTO indicateurs (id_site, name, value) VALUES (\"" + str(id_site) + "\", \"" + str(name) + "\", \"" + str(value) + "\");"
    conn.execute(requete)
    conn.commit()
    conn.close()

# -> https://docs.python.org/2/library/sqlite3.html#sqlite3.Connection.row_factory
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# un seul enregistrement
def lectureUnSite(basedonnees, uniqueid):
    conn = connexionBase(basedonnees)
    conn.row_factory = dict_factory
    requete = "SELECT * FROM data WHERE id = \""+str(uniqueid) + "\";"
    cursor = conn.execute(requete)
    return cursor.fetchone()

# add website
def ajouteSite(basedonnees, nom, url, description, comment, last_update):
    conn = connexionBase(basedonnees)
    conn.execute( "INSERT INTO data (name, url, description, comment, last_update) VALUES (\"" + prepareExpression(str(nom)) + "\", \"" + prepareExpression(str(url)) + "\", \"" + prepareExpression(str(description)) + "\", \"" + prepareExpression(str(comment)) + "\", \"" + prepareExpression(str(last_update)) + "\")")
    conn.commit()
    conn.close()

def majSite(basedonnees, nom, url, description, comment, uniqueid, last_update):
    conn = connexionBase(basedonnees)
    conn.execute( "UPDATE data SET name = \"" + prepareExpression(str(nom)) + "\", url = \"" + prepareExpression(str(url)) + "\", description = \"" + prepareExpression(str(description)) + "\", comment = \"" + prepareExpression(str(comment)) + "\", last_update = \"" + prepareExpression(str(last_update)) + "\" WHERE id = \"" + prepareExpression(str(uniqueid)) + "\" ;")
    conn.commit()
    conn.close()

def supprimeSite(basedonnees, identifiant) :
    conn = connexionBase(basedonnees)
    conn.execute( "DELETE FROM data WHERE id = \"" + prepareExpression(str(identifiant)) + "\"" )
    conn.commit()
    conn.close()

# ajoute une action
def ajouteAction(basedonnees, site_id, url, date, comment, backlink):
    conn = connexionBase(basedonnees)
    conn.execute( "INSERT INTO actions (site_id, url, date, comment, backlink) VALUES (\"" + prepareExpression(str(site_id)) + "\", \"" + prepareExpression(str(url)) + "\", \"" + prepareExpression(str(date)) + "\", \"" + prepareExpression(str(comment)) + "\", \"" + prepareExpression(str(backlink)) + "\")")
    conn.commit()
    conn.close()

# mise à jour d'une action
def majAction(basedonnees, site_id, url, date, comment, backlink, uniqueid):
    conn = connexionBase(basedonnees)
    conn.execute( "UPDATE actions SET site_id = \"" + prepareExpression(str(site_id)) + "\", url = \"" + prepareExpression(str(url)) + "\", date = \"" + prepareExpression(str(date)) + "\", comment = \"" + prepareExpression(str(comment)) + "\", backlink = \"" + prepareExpression(str(backlink)) + "\" WHERE id = \"" + prepareExpression(str(uniqueid)) + "\" ;")
    conn.commit()
    conn.close()