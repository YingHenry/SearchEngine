# Extraction de liens d'une page.
# Création d'un graphe. Le graphe contient la liste de toutes les pages parcourues par le moteur. Pour chaque page on fait la liste des liens qu'elle contient.
# Classement des pages avec l'algorithme PageRank. Ce dernier utilise les données du graphe.
# Création de l'index. Il contient les mots trouvés dans les pages. Pour chaque mot-clé on fait la liste des pages dans lesquelles il se trouve.
# Optimisation des performances avec les tables de hachage.

# la bibliothèque BeautifulSoup sert à enlever les balises HTML d'une page
# pour installer aller dans le répertoire de Beautiful Soup shif+click droit ->"ouvrir une fenetre de commande ici"
# taper setup.py install
from bs4 import BeautifulSoup

def checkUrl(url, page):
    # on regarde si c'est une adresse absolue ou relative
    if url.find('http:') == -1: # si on ne trouve pas 'http' 
        path = getDirectoryPath(page) # on recupere le chemin du dossier de la page actuelle
        if url[0] == '/': 
            if len(url) > 1 and url[1] == '/': # si le 2ème caractères est également  / alors c'est le nom de domaine
                url = 'http:' + url
            else: # si seul le 1er caractère est / alors c'est un chemin absolu, il faut rajouter le nom de domaine
                url = 'http://queribus.free.fr/Astronomie/accueil.html' + url
        else: # sinon c'est un chemin relatif: le chemin du dossier de la page actuelle + chemin relatif
            url = path + '/' + url
    # si on trouve http alors c'est le chemin complet pas besoin de modifier
    return url

# 
def getDirectoryPath(url):
    oldPosition = 0
    while 1:
        newPosition = url.find('/', oldPosition)
        if newPosition == -1: # si on ne trouve plus de slash on sort
            break
        else:
            oldPosition = newPosition+1 # sinon on cherche un autre slash après celui-ci
    if url[oldPosition-1] != url[oldPosition-2]: # si le caractère qui précède le dernier slash trouvé n'est pas un slash
        url = url[:oldPosition-1] # on ignore ce qu'il y a après le dernier slash
    return url

def get_page(url):
    try:
        import urllib
        return urllib.urlopen(url).read() # ouverture de la page et lecture du contenu
    except:
        return "--fail--"

def get_next_target(page):
    # on cherche un lien
    start_link = page.find('<a href=')
    if start_link == -1: 
        return None, 0
    # on cherche le 1er guillemet
    start_quote = page.find('"', start_link)
    # on cherche le 2ème guillemet
    end_quote = page.find('"', start_quote + 1)
    # l'url qu'on va renvoyer se trouve entre les 2
    url = page[start_quote + 1:end_quote]
    
    return url, end_quote

def union(p,q):
    # on parcourt les éléments dans q
    for e in q:
        # si l'élément n'est pas dans p
        if e not in p:
            # on le rajoute dans p
            p.append(e)


def get_all_links(content, page):
    links = []
    # tant qu'on trouve des urls on continue de chercher
    while True:
        # on cherche une url dans une portion de page
        url,endpos = get_next_target(content)
        # si on trouve une nouvelle url 
        if url:
            url = checkUrl(url, page)
            links.append(url) # on la rajoute dans la liste
            content = content[endpos:] # la nouvelle portion de page démarre après la fin de l'url
        else:
            break
    return links

def crawl_web(seed):
    tocrawl = [seed]
    crawled = []
    graph = {} # <url>: [liste d'urls contenues dans la page]
    index = {} # version dictionnaire
    #index = make_hashtable(10);
    # tant qu'il y a des urls a explorer
    while tocrawl:
        page = tocrawl.pop() # on prend la dernière url 
        if page not in crawled: # si cette url n'a pas encore été explorée
            content = get_page(page)
            add_page_to_index(index, page, content) # on ajoute les mots clé et les urls associées a l'index

            outlinks = get_all_links(content, page) # on récupère les liens
            graph[page] = outlinks
            union(tocrawl, outlinks) # on ajoute les urls de la page à la liste generale
            crawled.append(page) # on indique que la page à ete explorée
            if len(crawled) >= 30: # on limite le nombre de pages parcourues
                # print '--- URL PARCOURUES ---'
                # for url in crawled:
                #     print url
                # print '\n'
                break
    return index, graph

def add_to_index(index,keyword,url):
    if keyword in index: # si on trouve le mot clé dans l'index
        if url not in index[keyword]: # si l'url n'est pas dans la liste des urls associées au mot cle
            index[keyword].append(url) # on ajoute l'url dans la liste des urls
    else:
        index[keyword] = [url] # sinon on crée une nouvelle entrée

def add_page_to_index(index,url,content):
    #for keyword in content.split():

    soup = BeautifulSoup(content)
    cleantext = soup.text

    for keyword in cleantext.split():
        add_to_index(index,keyword,url) # version dictionnaire
        #hashtable_update(index, keyword, url) # version table de hachage

def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    return None

import time

def measure(code):
    start = time.clock()
    eval(code)
    return time.clock() - start

def loop():
    i = 0
    while i < 10000000:
        i = i+ 1
    return
        
#print measure('loop()')    

# HACHAGE
#########

def make_hashtable(nbuckets):
    table = []
    for unused in range(0, nbuckets):
        table.append([])
    return table

def hash_string(keyword,buckets):
    total = 0
    for letter in keyword:
        total += ord(letter)
    return total % buckets # l'index du bucket

# fonction qui renvoie l'index du bucket ou devrait se trouve le mot cle
# le nombre de buckets correspond a la taille de la table
def hashtable_get_bucket(htable,keyword):
    return htable[hash_string(keyword, len(htable))]    

# retourne la valeur d'un mot cle
def hashtable_lookup(htable,key):
    bucket = hashtable_get_bucket(htable,key) # on recupere le bucket dans lequel se trouve le mot cle
    for entry in bucket: # une fois dans le bucket on regarde si le mot clé a deja ete ajoute, si c'est le cas on regarde sa valeur
        if entry[0] == key: 
            return entry[1]
    return None    

#  ajout ou mise a jour d'un mot cle dans la table
def hashtable_update(htable, key, value):
    bucket = hashtable_get_bucket(htable, key)
    for entry in bucket:
        if entry[0] == key: # si le mot cle est deja dans la table on change sa valeur
            if value not in entry[1]: # si l'url n'est pas dans la liste des urls associees au mot cle
                entry[1].append(value) # on ajoute l'url dans la liste des urls
            return htable
    # si on a rien trouve on ajoute une nouvelle entree
    bucket.append([key, [value]])
    return htable

# ALGORITHME PAGERANK
#####################

def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10

    ranks = {} # dictionnaire qui contient les PR a t-1
    npages = len(graph) # nombre de noeuds dans le graphe
    for page in graph:
        ranks[page] = 1.0 / npages # le PR a t=0 est 1/nombre de pages

    for i in range(0, numloops): # on met a jour x fois le PR des pages
        newranks = {} # dictionnaire qui contient les PR a t

# graph{url1: [],
#       url2: [],
#       url3: [],
#       ...
#       }
# pour chaque url on regarde si elle fait partie de la liste de chacune des autres urls
# autrement dit si une url B pointe vers l'url A on ajoute d * (PR(url B) / nombre d'urls contenus dans l'url B)

# pour 1 page index qui pointe vers 1 seule autre page A, 1 iteration donne:
# PR(index) = (1-0.8)/2 = 0.1
# PR(A) = 0.1 + 0.8 * (1/2 / 1) = 0.5
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank += d * (ranks[node] / len(graph[node]))
            newranks[page] = newrank
        ranks = newranks

    inlinks = {}
    for page in graph:
        i = 0
        for node in graph:
            
            if page in graph[node]:
                i += 1
        inlinks[page] = i        
    return ranks, inlinks

# TESTS
#######

#index, graph = crawl_web('http://rhyne220686.perso.sfr.fr/index.html')
#index, graph = crawl_web('http://queribus.free.fr/Astronomie/accueil.html')
#index, graph = crawl_web('faux site/index.html') # local

ranks, inlinks = compute_ranks(graph)

print '--- GRAPH ---'
print '--- LIENS TROUVES POUR CHAQUE URL ---'
print '\n'
#toutes les pages
# for url in graph:
#     print url
#     i = 0
#     for outlink in graph[url]:
#         print '---' + outlink
#         i = i+1
#         if i > 2: # on met juste les x premiers
#             break
# print '\n'

# juste une page
# for outlink in graph['http://www.jeuxvideo.com/toutes-les-news/type-7720/']:
#     print '---' + outlink

print '--- MOTS-CLES ET LISTES ASSOCIEES ---'
print '\n'

print `len(index)` + ' mots' # mots contenu dans le seau
#for keyword in index: # version dictionnaire
#   print keyword
#   print index[keyword]

# for i in range(0, len(index)): # version hachage
#     print 'Seau ' + `i`
#     print '==========' # bug quand on met des tirets...
#     print len(index[i]) # nombre de mots dans un seau

    # for entry in index[i]:
    #     print entry[0] # mots contenu dans le seau
    #     print entry[1] # url associées

#print hash_string('page',10)
#print hash_string('principale',10)
#print hash_string('La',10)

print '\n'
print '--- PAGERANK DES PAGES ---'
print '\n'

for url in ranks:
    print url
    print 'in: ' + `inlinks[url]`
    print 'out: ' + `len(graph[url])`
    print ranks[url]

