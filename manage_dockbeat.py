##
## See if dockbeat index exists, if so export those older than SAVEDATES day.
## Note: only checks back for 30 days so run at least once a month
##
## author: ar0xa@tldr.nu
from datetime import date
from datetime import timedelta
import os.path, sys, urllib2, requests, subprocess

#how many days do you want to save
SAVEDATES = 14

#where is elasticdump located
ELDUMP = "/usr/local/bin/elasticdump"

#where do we dump to
ELDUMPLOC = "/home/user/scripts/"

#where is the database located
ELDBLOC = "http://127.0.0.1:9200"

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
    indexname = "dockbeat-%s" % ( today - timedelta( days = i + SAVEDATES ) ).strftime( '%Y.%m.%d' )
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
