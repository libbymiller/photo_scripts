# photo_scripts

Some python scripts for regular photo processing and putting on a remote 
server. It might be too esoteric for anyone except me.

The idea is:

 * use whatever software to put your photo on your laptop
 * put ```process_photos.py``` on your server with cert-based access
 * point ```exif_with_rotation_and_copy.py``` at the directory, e.g.

```exif_with_rotation_and_copy.py photos/20180601/```

It pulls out the date from the exif for jpgs and ignores the rest, uploads 
them and creates index files for month and date.

# todo

 * preserve date ordering on index pages



