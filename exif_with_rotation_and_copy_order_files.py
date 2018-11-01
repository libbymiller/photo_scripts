#!/usr/bin/env python

import sys
import os
import shutil
import datetime
import struct
import re
import datetime as dati
from subprocess import call
import pexif
from PIL import Image

path_name = sys.argv[1]
date_path_root = "../tmp_photos"
user = "photos"
server = "photos.example.com"

not_found = []

def make_path(date_path_root,y,m,d):
     if(os.path.exists(date_path_root)):
           y_path = date_path_root+"/"+y
           m_path = date_path_root+"/"+y+"/"+m
           d_path = date_path_root+"/"+y+"/"+m+"/"+d

     if(os.path.exists(y_path)==False):
           # mkdir y
           os.mkdir( y_path );

     if(os.path.exists(m_path)==False):
           # mkdir m
           os.mkdir( m_path );

     if(os.path.exists(d_path)==False):
           # mkdir d
           os.mkdir( d_path );

     return d_path      

def get_dt_components(dt):

          dt = str(dt).replace("-",":")

          #2018:02:20 12:14:31
          a = str(dt).split(" ")
          d = a[0]
          t = a[1]

          dd = d.split(":")
          tt = t.split(":")

          y = dd[0]
          m = dd[1]
          d = dd[2]

          h = tt[0]
          mi = tt[1]
          s = tt[2]

          return y,m,d,h,mi,s



last_dt = None

def do_stuff(fp):

        # Open image file and look for exif
        dt = None
        img = None
        try:
            imgg = pexif.JpegFile.fromFile(fp)
            dt = imgg.exif.primary.DateTime
            ## rotate image if need be while we're here
            orientation = imgg.exif.primary.Orientation[0]
            print("orientation "+str(orientation))

            img = Image.open(fp)
            if orientation is 6: img = img.transpose(Image.ROTATE_270)
            elif orientation is 8: img = img.transpose(Image.ROTATE_90)
            elif orientation is 3: img = img.transpose(Image.ROTATE_180)
            elif orientation is 2: img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation is 5: img = img.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation is 7: img = img.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation is 4: img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)

            print("ok and rotated")

        except Exception as e:
            print("exif didn't work - using system date instead")
#            print(e)
            st = os.stat(fp)    
            print(dati.datetime.fromtimestamp(st.st_mtime))
            dt = dati.datetime.fromtimestamp(st.st_mtime)            
            print("set dt to created date "+str(dt))
            not_found.append(fp)


        if(dt != None):
          print("got dt "+str(dt))
          last_dt = dt
          y,m,d,h,mi,s = get_dt_components(dt)
          d_path = make_path(date_path_root,y,m,d)

          # now copy the file to the right place
          fff = fp.split("/")
          file_name = fff[len(fff)-1]
          print "file_name "+file_name
          new_file_name = str(y)+str(m)+str(d)+str(h)+str(mi)+str(s)+"_"+file_name
          print "new_file_name "+new_file_name

          if(img):
             print("got img "+fp)
             print("saving image to "+os.path.join(d_path,new_file_name))
#             img.save(os.path.join(d_path,file_name))
             img.save(os.path.join(d_path,new_file_name))
          else:
             pattern_aae = re.compile("AAE")
             if(pattern_aae.search(fp)):
               pass
             else:
               print("copying over "+fp+" to "+d_path)
#               shutil.copy2(fp, d_path) 
               shutil.copy2(fp, os.path.join(d_path,new_file_name)) 

          # make everything public
          print("making things public in "+fp) 
          os.chmod(os.path.join(d_path,file_name), 0777)    
          print("done")

        else:
         print("no datetime")

# create dir if needed

if(os.path.exists(date_path_root)):
  print("dir exists "+date_path_root)
else:
  print("dir doesn't exist, making it "+date_path_root)
  os.mkdir(date_path_root)


for root, dirs, files in os.walk(sys.argv[1]):

    now = dati.datetime.now()
    ago = now-dati.timedelta(minutes=90)
#    ago = now-dati.timedelta(days=360)

    path = root.split(os.sep)
    for file in files:
     if not file.startswith("."):

        fp = os.path.join(root, file)
        #print("looking at "+fp)

        try:
          st = os.stat(fp)    
          ctime = dati.datetime.fromtimestamp(st.st_ctime)
          if ctime > ago:
              print('%s modified %s'%(fp, ctime))
              do_stuff(fp)

        except Exception as e:
             #print(e)
             #print fp
             pass

print("Uploading photos to "+server)
result = call(["scp", "-r", date_path_root, user+"@"+server+":"])

print(result)

print("running remote script")

result = call(["ssh", user+"@"+server, "python", "process_photos.py"])

print(result)

# finally remove the contents of tmp_photos
print("removing "+date_path_root)
shutil.rmtree(date_path_root)
