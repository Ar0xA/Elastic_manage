##
## See if index exists, if so export those older than SAVEDATES day.
## Note: only checks back for 90 days
## Index format is required to be  [name]-yyyy.mm.dd
##
## author: artien.bel@conclusion.nl

from datetime import date
from datetime import timedelta
import os.path, sys, urllib2, requests, subprocess

if len(sys.argv) < 3:
    print ( "You need to specify the index name and retention length in days!" )
    print ( "Where index format needs to be [name]-yyyy.mm.dd")
    print ( "" )
    print ( "python export_delete_ELDBindex.py dockbeat 14" )
    sys.exit ( 1 )

#how many days do you want to save
SAVEDATES = sys.argv[ 2 ]
try:
    SAVEDATES = int( SAVEDATES )
except:
    print ( "!! Parameter two needs to be an integer amount of days" )
    sys.exit( 1 )

#where is elasticdump located
ELDUMP = "/usr/local/bin/elasticdump"

#where do we dump to
ELDUMPLOC = "/home/siemonster/scripts/"

#where is the database located
ELDBLOC = "http://127.0.0.1:9200"

#whats the index name?
#format name-yyyy.mm.dd
ELINDEX = sys.argv[ 1 ]

#does the elasticdump program exist?
if not os.path.exists( ELDUMP ):
    print ( "!! Cannot find elasticdump at %s" % (ELDUMP) )
    sys.exit( 1 )

#can i access the elastic database?
requestresult = urllib2.urlopen( ELDBLOC )
if not requestresult.getcode() == 200:
    print ("!! Cannot access database at %s" % ( ELDBLOC ) )
    sys.exit( 1 )

today = date.today()
for i in range( 0, 90 ):
    indexname = ELINDEX + "-%s" % ( today - timedelta( days = i + SAVEDATES ) ).strftime( '%Y.%m.%d' )
    #check if index exists
    requestresult = requests.request( 'HEAD', ELDBLOC + "/" + indexname )
    if requestresult.status_code == 200:
        print ("index %s exists" % (indexname ) )
        #alright, it exists, lets dump it!
        print ( "- dumping index %s to file" % indexname )
        subprocess.check_output( [ ELDUMP, "--input=" + ELDBLOC + "/" + indexname, "--output=" + ELDUMPLOC + "/" + indexname + ".json" ] )
        print ( "- compressing %s" % indexname )
        subprocess.check_output( [ '/bin/gzip','--force', '-9', ELDUMPLOC + "/" + indexname + ".json" ] )
        #if all goes well, we ended up here..time to delete the index from the server and free up some space!
        print ("- dump completed, deleting index %s " % indexname)
        requestresult = requests.request( 'DELETE', ELDBLOC + "/" + indexname )
        if requestresult.status_code == 200:
            print ( "-- deleting index successful, better safe that exported file" )
        else:
            print ( "!! Error deleting index, this should not happen!" )
            sys.exit( 1 )
    else:
       print ("index %s does not exist" % (indexname))
