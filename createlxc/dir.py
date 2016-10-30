import os.path

   def processDirectory(args, dirname, filenames):
        for filename in filenames:
                filename = filename
		print ' File ',filename
        os.path.walk(r'/var/lib/libvirt/images', processDirectory, None)
