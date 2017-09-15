# -*- coding: utf-8 -*-
# library to manage GUI
# Nicolas Lorenzon - nicolas@lorenzon.ovh - http://www.lorenzon.ovh

from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile
import lib_bd
import lib_services
import threading
import time
import webbrowser

class myGui(object):

    def __init__(self):

        self.versionNumber = "v20170630"

        self.fenetre = None

        # tree des sites fentre générale
        self.tree = None
        # tree des actions
        self.treeAction = None

        # fenetre ajout d'un site
        self.addWindow = None
        # fenetre affichage info d'un site
        self.printWindow = None
        # fenetre des actions
        self.actionWindow = None
        # fenetre ajout d'une action
        self.addActionWindow = None

        self.idModification = None
        self.idModificationAction = None

        self.entryName = None
        self.entryUrl = None
        self.entryDescription = None
        self.entryComment = None

        self.label_compteur = None

        # contient l'url du site sélectionné pour les actions
        self.siteAction = None

        # champs pour l'ajout et la mise à jour d'un site
        self.champs = [("name", "Name", "entry"),
                    ("url", "URL (http://www.exemple.com)", "entry"),
                    ("last_update", "Last Update (exemple : 20151231)", "entry"),
                    ("description", "Description / theme", "text"),
                    ("comment", "Comment", "text")]
        # champs pour les actions
        self.champsActions = [("site_id", "Site", "listbox"),
                    ("url", "URL (http://www.exemple.com)", "entry"),
                    ("date", "Action date (exemple : 20151231)", "entry"),
                    ("comment", "Comment", "text"),
                    ("backlink", "Backlinks' url", "entry")]

        # les champs pour les sites
        self.entries = []

        # les champs pour les actions
        self.entriesActions = []

        self.base = "websites.data"

        self.initialisation()
        self.addWidgets()
        self.loadData()
        self.runLoop()

    def initialisation(self):
        # init GUI
        self.fenetre = Tk()
        self.fenetre.title("PBN Manager " + self.versionNumber)
        self.fenetre.geometry("1200x600")

    # ajout des widget sur la fenetre principale des sites
    def addWidgets(self):
        
        # rest ineterface.......................................................
        frame1 = Frame(self.fenetre, borderwidth=2, relief=GROOVE)
        frame1.pack(side=TOP, padx=5, pady=5, expand=False, fill=X)

        bouton = Button(frame1, text="Quit", command=self.fenetre.quit)
        bouton.pack(side="right", padx=5, pady=5)

        button = Button(frame1, text="Add Website", command=self.addWebsiteWindow)
        button.pack(side="left", padx=5, pady=5)

        button = Button(frame1, text="Update Website", command=self.modifyWebsiteWindow)
        button.pack(side="left", padx=5, pady=5)

        button = Button(frame1, text="Get Ranks", command=self.getRankForWebsite)
        button.pack(side="left", padx=5, pady=5)

        button = Button(frame1, text="Actions", command=self.create_window_actions)
        button.pack(side="left", padx=5, pady=5)

        button = Button(frame1, text="Delete selected Website", command=self.deleteWebsite)
        button.pack(side="left", padx=5, pady=5)

        button = Button(frame1, text="Import Websites", command=self.importWebsiteCSV)
        button.pack(side="left", padx=5, pady=5)

        button = Button(frame1, text="Export Websites", command=self.saveWebsiteCSV)
        button.pack(side="left", padx=5, pady=5)

        frame2 = Frame(self.fenetre, borderwidth=2, relief=GROOVE)
        frame2.pack(side=TOP, padx=5, pady=5, expand=True, fill=BOTH)

        scrollbar = Scrollbar(frame2)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree = Treeview(frame2)

        self.tree["columns"] = ("url", "name", "last_update", "description", "alexa", "links", "da", "pa", "indexed")
        self.tree.column("#0", minwidth=0, width=1, stretch=NO)
        self.tree.column("url", width=200)
        self.tree.heading("url", text="URL")
        self.tree.column("last_update", width=80)
        self.tree.heading("last_update", text="Last update")
        self.tree.column("name", width=200)
        self.tree.heading("name", text="Name")
        self.tree.column("description", width=300)
        self.tree.heading("description", text="Description / theme")
        self.tree.column("alexa", width=70)
        self.tree.heading("alexa", text="Alexa")
        self.tree.column("links", width=55)
        self.tree.heading("links", text="Links")
        self.tree.column("da", width=40)
        self.tree.heading("da", text="DA")
        self.tree.column("pa", width=40)
        self.tree.heading("pa", text="PA")
        self.tree.column("indexed", width=40)
        self.tree.heading("indexed", text="Indexed")

        self.tree.bind("<Double-1>", self.create_window_print)

        self.tree.pack(side="right", padx=5, pady=5, expand=True, fill=BOTH)

        scrollbar.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar.set)

        frame3 = Frame(self.fenetre, borderwidth=2, relief=GROOVE)
        frame3.pack(side=BOTTOM, padx=5, pady=5, expand=False, fill=X)

        self.label_compteur = StringVar()
        w = Label(frame3, textvariable=self.label_compteur)
        w.pack(side="right", padx=5, pady=5)
        self.label_compteur.set("0 websites")

        w = Label(frame3, text="Use at your own risk - Get help on SeoSoftwareNow.com")
        w.pack(side="left", padx=5, pady=5)

    # pour obtenir le rank et les indicateurs pour les sites
    def getRankForWebsite(self):
        try:
            self.fenetre.config(cursor="watch")
            item = self.tree.selection()[0]
            url = self.tree.item(item, "values")
            url = url[0]
            uniqueid = self.tree.item(item, "text")
            # thread
            t = threading.Thread(target=self.thread_rank, args=(url, uniqueid))
            #self.thread_rank(url, uniqueid)
            t.start()
        except ValueError:
            print(ValueError)
            self.fenetre.config(cursor="")

    def thread_rank(self, url, uniqueid):
        # faire un thread avec les traitements
        # alexa rank
        retour1 = lib_services.getAlexaRank(self.base, url, uniqueid)
        # indicateurs moz
        retour2 = lib_services.getMoz(self.base, url, uniqueid)
        # google indexed
        retour3 = lib_services.pages_indexees(self.base, url, uniqueid)
        # affichage de l'erreur :
        retour = retour1 + " \n" + retour2 + " \n" + retour3
        if ((retour1 != "") or (retour2 != "") or (retour3 != "")):
            # affichage message
            showwarning("Error", retour)
        # recharge la vue avec les données
        self.loadData()
        # on remet le curseur comme avant
        self.fenetre.config(cursor="")

    # fenetre d'ajout d'un site
    def addWebsiteWindow(self):
        self.create_window(True)

    # fenetre de modification d'un site
    def modifyWebsiteWindow(self):
        # on récupère l'id sélectionné
        item = self.tree.selection()[0]
        uniqueid = self.tree.item(item, "text")
        self.idModification = uniqueid
        self.create_window(False)

    # cas du click sur la list box de choix du site sur la fenetre des actions
    def onselect(self, event):
        # Note here that Tkinter passes an event object to onselect()
        self.siteAction = None
        w = event.widget
        index = int(w.curselection()[0])
        if index == 0:
            self.loadDataActions()
            self.siteAction = None
        else:
            # on veut avoir uniquement ce qui concerne un seul site
            value = w.get(index)
            self.siteAction = value
            id_site = lib_bd.getIdForSite(self.base, value)
            self.loadDataActionsForSite(id_site)

    # pour la fenêtre des actions
    def create_window_actions(self):
        self.actionWindow = Toplevel(self.fenetre)
        self.actionWindow.wm_title("Actions")
        self.actionWindow.geometry("1100x600")

        frame1 = Frame(self.actionWindow, borderwidth=2, relief=GROOVE)
        frame1.pack(side=TOP, padx=5, pady=5, expand=False, fill=X)

        bouton = Button(frame1, text="Close", command=self.actionWindow.destroy)
        bouton.pack(side="right", padx=5, pady=5)

        bouton = Button(frame1, text="Add action", command=self.ajouteAction)
        bouton.pack(side="left", padx=5, pady=5)

        bouton = Button(frame1, text="Update action", command=self.modifieAction)
        bouton.pack(side="left", padx=5, pady=5)

        bouton = Button(frame1, text="Export visible actions", command=self.exportActions)
        bouton.pack(side="left", padx=5, pady=5)

        frame2 = Frame(self.actionWindow, borderwidth=2, relief=GROOVE)
        frame2.pack(side=TOP, padx=5, pady=5, expand=True, fill=BOTH)

        # creation de la liste des sites web
        frameList = Frame(frame2, borderwidth=2, relief=GROOVE)
        frameList.pack(side="left", padx=5, pady=5, expand=True, fill=BOTH)
        scrollbar = Scrollbar(frameList)
        scrollbar.pack(side=RIGHT, fill=Y)
        entry = Listbox(frameList, bg="white")
        entry.pack(fill=BOTH, expand=True)

        urlForId = {}

        # on récupère les sites depuis la BD
        allwebsites = lib_bd.lectureTousListBox(self.base)
        entry.insert(END, "All *")
        number = 1
        for website in allwebsites:
            url = website[1]
            entry.insert(END, url)
            urlForId[url] = number
            number += 1
        scrollbar.config(command=entry.yview)
        entry.config(yscrollcommand=scrollbar.set)
        # on sélectionne "tous" au début
        entry.select_set(0)
        entry.bind('<<ListboxSelect>>', self.onselect)

        # création liste des actions
        scrollbar = Scrollbar(frame2)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.treeAction = Treeview(frame2)

        self.treeAction["columns"] = ("site_id", "url", "date", "comment", "backlink")
        self.treeAction.column("#0", minwidth=0, width=1, stretch=NO)
        self.treeAction.column("site_id", width=200)
        self.treeAction.heading("site_id", text="Website")
        self.treeAction.column("url", width=200)
        self.treeAction.heading("url", text="URL (Spot)")
        self.treeAction.column("date", width=80)
        self.treeAction.heading("date", text="Date")
        self.treeAction.column("comment", width=200)
        self.treeAction.heading("comment", text="Comment")
        self.treeAction.column("backlink", width=100)
        self.treeAction.heading("backlink", text="Backlink")

        #self.treeAction.bind("<Double-1>", self.create_window_print)

        self.treeAction.pack(side="right", padx=5, pady=5, expand=True, fill=BOTH)

        scrollbar.config(command=self.treeAction.yview)
        self.treeAction.config(yscrollcommand=scrollbar.set)

        self.loadDataActions()

    # affiche les informations d'un site (sans pouvoir les modifier)
    def create_window_print(self, event):
        self.printWindow = Toplevel(self.fenetre)
        self.printWindow.wm_title("Info")
        # une grande label avec tout et un bouton "OK"
        # on récupère l'id
        item = self.tree.selection()[0]
        uniqueid = self.tree.item(item, "text")
        tableau = lib_bd.lectureUnSite(self.base, uniqueid)
        afficher = ""
        for champ in self.champs:
            uniqueid = champ[0]
            nom = champ[1]
            afficher += str(nom) + str(" :\n")
            afficher += str(tableau[uniqueid]) + str("\n --- \n\n")

        frame = Frame(self.printWindow, borderwidth=2, relief=GROOVE)
        frame.pack(side=TOP, padx=5, pady=5, expand=False, fill=BOTH)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        entry = Text(frame, height=25)
        entry.pack(fill=X, expand=True)
        entry.insert("1.0", afficher)

        scrollbar.config(command=entry.yview)
        entry.config(yscrollcommand=scrollbar.set)

        # bouton
        frameBas = Frame(self.printWindow, borderwidth=2, relief=GROOVE)
        frameBas.pack(side=BOTTOM, padx=5, pady=5, expand=False, fill=X)
        bouton = Button(frameBas, text="OK", command=self.printWindow.destroy)
        bouton.pack(side=BOTTOM)

    # ouvre la fenetre de modification d'une action
    def modifieAction(self):
        item = self.treeAction.selection()[0]
        uniqueid = self.treeAction.item(item, "text")
        self.idModificationAction = uniqueid
        self.create_add_action_window(False)

    # ouvre la fenetre d'ajout d'une action
    def ajouteAction(self):
        self.create_add_action_window(True)

    # affiche le formulaire pour ajouter une action
    def create_add_action_window(self, new):
        # réinitialisation
        self.entriesActions = []
        urlForId = {}

        self.addActionWindow = Toplevel(self.actionWindow)
        self.addActionWindow.wm_title("New Action")

        if not new:
            self.addActionWindow.wm_title("Update Action")
            tableau = lib_bd.lectureUneAction(self.base, self.idModificationAction)
            print(tableau)

        for champ in self.champsActions:
            uniqueid = champ[0]
            nom = champ[1]
            typechamp = champ[2]

            frame = Frame(self.addActionWindow, borderwidth=2, relief=GROOVE)
            frame.pack(side=TOP, padx=5, pady=5, expand=False, fill=X)

            label = Label(frame, text=nom)
            label.pack(side=TOP, padx=5, pady=5, expand=True, fill=Y)
            if typechamp == "entry":
                entry = Entry(frame, width=30)
                entry.pack(fill=X, expand=True)

            if typechamp == "text":
                scrollbar = Scrollbar(frame)
                scrollbar.pack(side=RIGHT, fill=Y)

                entry = Text(frame, height=10, bg="white")
                entry.pack(fill=X, expand=True)

                scrollbar.config(command=entry.yview)
                entry.config(yscrollcommand=scrollbar.set)

            if typechamp == "listbox":
                scrollbar = Scrollbar(frame)
                scrollbar.pack(side=RIGHT, fill=Y)

                entry = Listbox(frame, height=15, bg="white")
                entry.pack(fill=X)

                # on récupère les sites depuis la BD
                allwebsites = lib_bd.lectureTousListBox(self.base)
                number = 0
                for website in allwebsites:
                    url = website[1]
                    entry.insert(END, url)
                    urlForId[url] = number
                    number += 1
                scrollbar.config(command=entry.yview)
                entry.config(yscrollcommand=scrollbar.set)

            if not new:
                if not(tableau[uniqueid] is None):
                    if typechamp == "entry":
                        entry.insert(0, tableau[uniqueid])
                    if typechamp == "text":
                        entry.insert("1.0", tableau[uniqueid])
                    if typechamp == "listbox":
                        # selectionner le site
                        #print("todo : sélectionner le site")
                        #print(urlForId)
                        url_site = lib_bd.getUrlForId(self.base, tableau[uniqueid])
                        #print(url_site)
                        entry.select_set(urlForId[url_site])
            else:
                if uniqueid == "date":
                    entry.insert(0, time.strftime("%Y%m%d"))

            # ajout du champ dans les entrées possibles
            self.entriesActions.append((uniqueid, entry, typechamp))

        frameBas = Frame(self.addActionWindow, borderwidth=2, relief=GROOVE)
        frameBas.pack(side=BOTTOM, padx=5, pady=5, expand=False, fill=X)

        if new:
            button = Button(frameBas, text="Save", command=self.addAction)
        else:
            button = Button(frameBas, text="Save", command=self.updateAction)
        button.pack(side=RIGHT)

        bouton = Button(frameBas, text="Cancel", command=self.addActionWindow.destroy)
        bouton.pack(side=LEFT)

    # affiche le formulaire d'un site pour modifier les informations
    def create_window(self, new):

        # réinitialisation
        self.entries = []

        self.addWindow = Toplevel(self.fenetre)
        self.addWindow.wm_title("New Website")

        if not new:
            self.addWindow.wm_title("Update Website")
            tableau = lib_bd.lectureUnSite(self.base, self.idModification)

        for champ in self.champs:
            uniqueid = champ[0]
            nom = champ[1]
            typechamp = champ[2]

            frame = Frame(self.addWindow, borderwidth=2, relief=GROOVE)
            frame.pack(side=TOP, padx=5, pady=5, expand=False, fill=X)

            label = Label(frame, text=nom)
            label.pack(side=TOP, padx=5, pady=5, expand=True, fill=Y)
            if typechamp == "entry":
                entry = Entry(frame, width=30)
                entry.pack(fill=X, expand=True)

            if typechamp == "text":
                scrollbar = Scrollbar(frame)
                scrollbar.pack(side=RIGHT, fill=Y)

                entry = Text(frame, height=10, bg="white")
                entry.pack(fill=X, expand=True)

                scrollbar.config(command=entry.yview)
                entry.config(yscrollcommand=scrollbar.set)

            if not new:
                if not(tableau[uniqueid] is None):
                    if typechamp == "entry":
                        entry.insert(0, tableau[uniqueid])
                    if typechamp == "text":
                        entry.insert("1.0", tableau[uniqueid])
            else:
                if uniqueid == "last_update":
                    entry.insert(0, time.strftime("%Y%m%d"))

            # ajout du champ dans les entrées possibles
            self.entries.append((uniqueid, entry, typechamp))

        frameBas = Frame(self.addWindow, borderwidth=2, relief=GROOVE)
        frameBas.pack(side=BOTTOM, padx=5, pady=5, expand=False, fill=X)

        if new:
            button = Button(frameBas, text="Save", command=self.addWebsite)
        else:
            button = Button(frameBas, text="Save", command=self.updateWebsite)
        button.pack(side=RIGHT)

        bouton = Button(frameBas, text="Cancel", command=self.addWindow.destroy)
        bouton.pack(side=LEFT)

    # ajout d'un site -> dans la BD
    def addWebsite(self):
        # ajout d'un site web dans le gestionnaire
        # TODO: voir avoir la liste
        table = {}
        for entry in self.entries:
            if entry[2] == "entry":
                table[entry[0]] = entry[1].get()
            if entry[2] == "text":
                table[entry[0]] = entry[1].get('1.0', END)
        #print(table)
        lib_bd.ajouteSite(self.base, table['name'], table['url'], table['description'], table['comment'], table["last_update"])
        self.loadData()
        self.addWindow.destroy()

    # ajout d'une action -> dans BD
    def addAction(self):
        table = {}
        ajout = False
        for entry in self.entriesActions:
            if entry[2] == "entry":
                table[entry[0]] = entry[1].get()
            if entry[2] == "text":
                table[entry[0]] =entry[1].get('1.0', END)
            if entry[2] == "listbox":
                if len(entry[1].curselection()) > 0:
                    item = entry[1].curselection()[0]
                    url_site = entry[1].get(item)
                    site_id = lib_bd.getIdForSite(self.base, url_site)
                    table[entry[0]] = site_id
                    ajout = True
                else:
                    showwarning("Website empty", "You must select a website")
        if ajout:
            lib_bd.ajouteAction(self.base, table['site_id'], table['url'], table['date'], table['comment'], table["backlink"])
            self.loadDataActions()
            self.addActionWindow.destroy()

    # modification d'une action
    def updateAction(self):
        table = {}
        for entry in self.entriesActions:
            if entry[2] == "entry":
                table[entry[0]] = entry[1].get()
            if entry[2] == "text":
                table[entry[0]] = entry[1].get('1.0', END)
            if entry[2] == "listbox":
                item = entry[1].curselection()[0]
                url_site = entry[1].get(item)
                site_id = lib_bd.getIdForSite(self.base, url_site)
                table[entry[0]] = site_id
        #print(table)
        lib_bd.majAction(self.base, table['site_id'], table['url'], table['date'], table['comment'], table["backlink"], self.idModificationAction)
        self.loadDataActions()
        self.addActionWindow.destroy()

    # mise à jour d'un site dans la BD
    def updateWebsite(self):
        table = {}
        for entry in self.entries:
            if entry[2] == "entry":
                table[entry[0]] = entry[1].get()
            if entry[2] == "text":
                table[entry[0]] = entry[1].get('1.0', END)
        #print(table)
        lib_bd.majSite(self.base, table['name'], table['url'], table['description'], table['comment'], self.idModification, table["last_update"])
        self.loadData()
        self.addWindow.destroy()

    # suppression d'un site de la BD
    def deleteWebsite(self):
        if askquestion("Confirm", "WARNING : are you sur you want to delete this website?") != "no":
            item = self.tree.selection()[0]
            identifiant = self.tree.item(item, "text")
            lib_bd.supprimeSite(self.base, identifiant)
            self.loadData()

    # boucle principale TKinter
    def runLoop(self):
        self.fenetre.mainloop()

    # recharger les donnees pour la liste des sites
    def loadData(self):
        # read all data from DB
        self.tree.delete(*self.tree.get_children())
        allwebsites = lib_bd.lectureTous(self.base)
        number = 0
        for website in allwebsites:
            url = website[2]
            name = website[1]
            description = website[3]
            uniqueId = website[0]
            last_update = website[5]
            # on va lire les paramètres pour ce site
            params = lib_bd.lectureIndicateursForSite(self.base, uniqueId)
            self.tree.insert("", "end", text=str(uniqueId), values=(url,name, last_update, description, params['alexa'], params['mozlinks'], params['mozda'], params['mozpa'], params['ggindexed']))
            number += 1
        self.label_compteur.set(str(number) + " websites")

    # recharger les données pour la liste des actions
    def loadDataActions(self):
        # read all data from DB
        self.treeAction.delete(*self.treeAction.get_children())
        allwebsites = lib_bd.lectureToutesActions(self.base)
        for website in allwebsites:
            unique_id = website[0]
            url = website[1]
            date = website[2]
            comment = website[3]
            backlink = website[4]
            siteurl = website[5]
            self.treeAction.insert("", "end", text=str(unique_id), value=(siteurl, url, date, comment, backlink))

    def loadDataActionsForSite(self, id_site):
        self.treeAction.delete(*self.treeAction.get_children())
        allwebsites = lib_bd.lectureToutesActionsForSite(self.base, id_site)
        for website in allwebsites:
            unique_id = website[0]
            url = website[1]
            date = website[2]
            comment = website[3]
            backlink = website[4]
            siteurl = website[5]
            self.treeAction.insert("", "end", text=str(unique_id), values=(siteurl, url, date, comment, backlink))

    def importWebsiteCSV(self):
        # lecture du fichier csv
        # l fichier doite être de la forme toto;titi;tralala;
        fname = askopenfilename(filetypes=(("CSV", "*.csv"),
                                           ("All files", "*.*")))
        try:
            contenu_fichier_website = lib_services.lireFichier(fname)
        except:
            showerror("File error", "Error reading file " + fname)
            return -1
        # def ajouteSite(basedonnees, nom, url, description, comment, last_update):
        for ligne in contenu_fichier_website:
            elements = ligne.replace("\n", " ").split(";")
            # on vérifie que le bon nombre d'elt est sur la ligne
            if len(elements) != 5:
                # message erreur
                showerror("Error in import", "Error in line : " + ligne)
                break
            else:
                # on peut sauvegarder
                nom_site = elements[0]
                url_site = elements[1]
                description_site = elements[2]
                comment_site = elements[3]
                last_update = elements[4]
                lib_bd.ajouteSite(self.base, nom_site, url_site, description_site, comment_site, last_update)
        self.loadData()

    def saveWebsiteCSV(self):
        # sauvegarde des infos au format CSV
        fname = asksaveasfile(mode='w', defaultextension=".txt")
        if fname is None:
            return
        allwebsites = lib_bd.lectureTous(self.base)
        contenu = ""
        for website in allwebsites:
            url = website[2]
            name = website[1].replace("\n", " | ").replace('"', '\"')
            description = '"' + website[3].replace("\n", " | ").replace('"', '\"') + '"'
            last_update = website[5]
            comment = '"' + website[4].replace('"', "'").replace("\n", " | ").replace('"', '\"') + '"'
            contenu += name + ";" + url + ";" + description + ";" + comment + ";" + last_update + "\n"
        fname.write(contenu)
        fname.close()

    def exportDataActionsForSite(self, id_site=None):

        # sauvegarde des infos au format CSV
        fname = asksaveasfile(mode='w', defaultextension=".txt")
        if fname is None:
            return
        allwebsites = lib_bd.lectureToutesActionsForSite(self.base, id_site)
        contenu = ""
        for website in allwebsites:
            url = website[1]
            date = website[2]
            comment = website[3]
            backlink = website[4]
            siteurl = website[5]
            contenu += url + ";" + date + ";" + comment.replace("\n", " ") + ";" + backlink + ";" + siteurl + "\n"
        fname.write(contenu)
        fname.close()

    def exportActions(self):
        # export des actions
        # on récupère le site cliqué
        id_site = lib_bd.getIdForSite(self.base, self.siteAction)
        if not id_site:
            id_site = None
        self.exportDataActionsForSite(id_site)

