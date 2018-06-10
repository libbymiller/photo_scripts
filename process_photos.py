import sys
import os
import re
import shutil
import datetime as dt

# idea is that we put new files in /var/www/html/photos/
# starting in tmp_photos
# then generate thumbnails
# then generate a new index file
# then delete tmp_photos contents

new_photos_path = "tmp_photos"
photos_path = "/var/www/html/photos"
remove_server = "http://photos.example.com"

def make_path(date_path_root):

     if(os.path.exists(date_path_root)):
       print("path exists "+date_path_root)
     else:
       print("path doesn't exist - making it "+date_path_root+"...")
       os.makedirs( date_path_root )


def create_index_files(list_of_dirs, photo_root):
  print(list_of_dirs)
  for fp in list_of_dirs:
 #   print(fp)
#    print(os.listdir(fp))
    file = open(os.path.join(fp, "index.html"),'w+') 
    file.write("<html>\n<body>\n<style>img { width:500; image-orientation: from-image;} figure { display: inline-block;}</style>\n")
    for root, dirs, files in os.walk(fp):

      for i in files:
        print("foudn file "+i)
        path = os.path.realpath(os.path.join(root,i))

        pattern_aae = re.compile("AAE")

        if(i!="index.html" and not pattern_aae.search(i)):
          dir_path = path.replace(photo_root,"")
          print("dir_path is "+dir_path)
          ii = dir_path
          dd = os.path.split(dir_path)[0]

          pattern_mov = re.compile("mov")
          pattern_mp4 = re.compile("mp4")

          if(pattern_mov.search(ii.lower()) or pattern_mp4.search(ii.lower())):
            file.write("<figure>\n<video src='"+ii+"' width='500px' controls />\n")
          else:
            file.write("<figure>\n<img src='"+ii+"'/>\n")

#          file.write("<figure>\n<a href='"+ii+"'><img src='"+ii+"'/></a>\n")
          file.write("<figcaption><a href='"+dd+"'>source</a></figcaption>\n</figure>\n")
    file.write("</body></html>")
    file.close()

def create_latest_index_file(list_of_images, photo_root):
  print(list_of_images)
  file = open(os.path.join(photo_root, "latest.html"),'w+') 
  file.write("<html>\n<body>\n<style>img { width:500; } figure { display: inline-block;}</style>\n")
  for fp in list_of_images:
    print(fp)

    img_path = fp.replace(photo_root,"")
    print("img_path is "+img_path)
    dd = os.path.split(img_path)[0]

    pattern_mov = re.compile("mov")
    pattern_mp4 = re.compile("mp4")
    pattern_aae = re.compile("AAE")

    if(pattern_mov.search(img_path.lower()) or pattern_mp4.search(img_path.lower())):
      file.write("<figure>\n<video src='"+img_path+"' width='500px' controls />\n")
      file.write("<figcaption><a href='"+dd+"'>source</a></figcaption>\n</figure>\n")
    else:
      if(pattern_aae.search(img_path)):
         pass
      else:
        file.write("<figure>\n<img src='"+img_path+"'/>\n")
        file.write("<figcaption><a href='"+dd+"'>source</a></figcaption>\n</figure>\n")

  file.write("</body></html>")
  file.close()


def create_latest_atom_file(list_of_images, photo_root):
  print(list_of_images)
  file = open(os.path.join(photo_root, "latest.xml"),'w+') 
  file.write('<?xml version="1.0" encoding="utf-8"?>\n')
  file.write('<feed xmlns="http://www.w3.org/2005/Atom">\n')
  file.write('<title>Libby\'s latest photos</title>\n')
  file.write('<subtitle></subtitle>\n')
  file.write('<link rel="alternate" type="text/html" href="'+server+'/latest.html" />\n')
  file.write('<link rel="self" type="application/atom+xml" href="'+server+'/latest.xml" />\n')
  file.write('<id>'+server+'/latest.xml</id>\n')
  file.write('<updated>'+str(dt.datetime.now())+'</updated>\n')


  for fp in list_of_images:
    print(fp)
    img_path = fp.replace(photo_root,"")
    print("img_path is "+img_path)
    dd = os.path.split(img_path)[0]

    pattern_mov = re.compile("mov")
    pattern_mp4 = re.compile("mp4")
    pattern_aae = re.compile("AAE")

    if(pattern_mov.search(img_path.lower()) or pattern_mp4.search(img_path.lower())):
       s = '<entry>\n    <title>'+img_path+'</title>\n    <id>'+img_path+'</id>\n    <published>'+str(dt.datetime.now())+'</published>\n    <updated>'+str(dt.datetime.now())+'</updated>\n    <author><name>Libby</name></author>\n    <content type="html" xml:base="'+server+'" xml:lang="en">\n       <![CDATA[<video src="'+server+'/'+img_path+'" width="500px" controls/>]]>\n    </content>\n    </entry>\n'
    else:
      if(pattern_aae.search(img_path)):
         pass
      else:
         s = '<entry>\n    <title>'+img_path+'</title>\n    <id>'+img_path+'</id>\n    <published>'+str(dt.datetime.now())+'</published>\n    <updated>'+str(dt.datetime.now())+'</updated>\n    <author><name>Libby</name></author>\n    <content type="html" xml:base="'+server+'" xml:lang="en">\n       <![CDATA[<img src="'+server+'/'+img_path+'" width="500px"/>]]>\n    </content>\n    </entry>\n'
    file.write(s)

  file.write("</feed>\n")
  file.close()



list_of_dirs = []
list_of_images = []

for root, dirs, files in os.walk(new_photos_path):

   path = root.split(os.sep)
   for file in files:
     if not file.startswith("."):
         fp = os.path.join(root, file)
         fp_tmp = fp.replace(new_photos_path,"")
         print(fp_tmp)
#        print(os.path.basename(fp_tmp))
         fp_tmp2 = os.path.split(fp_tmp)[0]

         fp_new = photos_path + fp_tmp

         print("looking at "+fp_new)
         just_dir = os.path.split(fp_new)[0]

         if(os.path.exists(just_dir)):
           print "exists - not making it "+just_dir
         else:
           print "doesn't exist - making it "+just_dir
           make_path(just_dir)

         # now copy the file to the right place

         print("copying over "+fp+" to "+fp_new)

         dirs = fp_tmp2.split("/")
         shutil.copy2(fp, fp_new)

         list_of_images.append(fp_new)

         by_month = photos_path+"/"+dirs[1]+"/"+dirs[2]
         by_date = photos_path+fp_tmp2
         if(by_month not in list_of_dirs):
           list_of_dirs.append(by_month)
         if(by_date not in list_of_dirs):
           list_of_dirs.append(by_date)

   create_index_files(list_of_dirs, photos_path)

# create a latest index file (and also atom file)

   create_latest_index_file(list_of_images, photos_path)
   create_latest_atom_file(list_of_images, photos_path)


# finally remove the contents of tmp_photos
print("removing "+new_photos_path)
shutil.rmtree(new_photos_path)
