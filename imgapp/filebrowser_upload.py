from django.shortcuts import render, render_to_response,HttpResponse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.core.files.storage import DefaultStorage, default_storage, FileSystemStorage
from filebrowser.utils import convert_filename
from filebrowser.base import FileListing, FileObject
from filebrowser.settings import (DIRECTORY, EXTENSIONS, SELECT_FORMATS, ADMIN_VERSIONS, ADMIN_THUMBNAIL, MAX_UPLOAD_SIZE, NORMALIZE_FILENAME,
                                  CONVERT_FILENAME, SEARCH_TRAVERSE, EXCLUDE, VERSIONS, VERSIONS_BASEDIR, EXTENSION_LIST, DEFAULT_SORTING_BY, DEFAULT_SORTING_ORDER,
                                  LIST_PER_PAGE, OVERWRITE_EXISTING, DEFAULT_PERMISSIONS, UPLOAD_TEMPDIR)

from filebrowser.sites import FileBrowserSite, handle_file_upload, get_breadcrumbs, get_settings_var, _ , messages, query_helper
from filebrowser import signals
from galactica_imanage.settings import BASE_DIR
try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text
import re
import os
import json
from .UpdateMongoDB import update_Mongo, delete_file_data
from .utils import Utils
import datetime



class UserFileBrowserSite(FileBrowserSite):
    timestamp = ""

    def upload(self, request):
        "Multipe File Upload."
        query = request.GET
        
        # timestamp set when the upload page is loaded 
        self.timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        
        request.current_app = self.name
        return render(request, 'filebrowser/upload.html', {
            'query': query,
            'title': _(u'Select files to upload'),
            'settings_var': get_settings_var(directory=self.directory),
            'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
            'breadcrumbs_title': _(u'Upload'),
            'filebrowser_site': self
        })

    def _upload_file(self, request):
        """
        Upload file to the server.
        If temporary is true, we upload to UPLOAD_TEMPDIR, otherwise
        we upload to site.directory
        """
        if request.method == "POST":
            folder = request.GET.get('folder', '')
            temporary = request.GET.get('temporary', '')
            temp_filename = None

            if len(request.FILES) == 0:
                return HttpResponseBadRequest('Invalid request! No files included.')
            if len(request.FILES) > 1:
                return HttpResponseBadRequest('Invalid request! Multiple files included.')

            filedata = list(request.FILES.values())[0]

            fb_uploadurl_re = re.compile(r'^.*(%s)' % reverse("filebrowser:fb_upload", current_app=self.name))
            folder = fb_uploadurl_re.sub('', folder)

            # temporary upload folder should be outside self.directory
            if folder == UPLOAD_TEMPDIR and temporary == "true":
                path = folder
            else:
                path = os.path.join(self.directory, folder)
            # we convert the filename before uploading in order
            # to check for existing files/folders
            file_name = convert_filename(filedata.name)
            filedata.name = file_name
            file_path = os.path.join(path, file_name)
            file_already_exists = self.storage.exists(file_path)

            # construct temporary filename by adding the upload folder, because
            # otherwise we don't have any clue if the file has temporary been
            # uploaded or not
            if folder == UPLOAD_TEMPDIR and temporary == "true":
                temp_filename = os.path.join(folder, file_name)

            # Check for name collision with a directory
            if file_already_exists and self.storage.isdir(file_path):
                ret_json = {'success': False, 'filename': file_name}
                return HttpResponse(json.dumps(ret_json))

            signals.filebrowser_pre_upload.send(sender=request, path=folder, file=filedata, site=self)
            uploadedfile = handle_file_upload(path, filedata, site=self)

            if file_already_exists and OVERWRITE_EXISTING:
                old_file = smart_text(file_path)
                new_file = smart_text(uploadedfile)
                self.storage.move(new_file, old_file, allow_overwrite=True)
                full_path = FileObject(smart_text(old_file), site=self).path_full
            else:
                file_name = smart_text(uploadedfile)
                filedata.name = os.path.relpath(file_name, path)
                full_path = FileObject(smart_text(file_name), site=self).path_full

            # set permissions
            if DEFAULT_PERMISSIONS is not None:
                os.chmod(full_path, DEFAULT_PERMISSIONS)

            f = FileObject(smart_text(file_name), site=self)
            signals.filebrowser_post_upload.send(sender=request, path=folder, file=f, site=self)

            # let Ajax Upload know whether we saved it or not
            ret_json = {'success': True, 'filename': f.filename, 'temp_filename': temp_filename}
            print("\n \n \n hello world \nfile:"+full_path+" \n \n")

            timestamp = self.timestamp
            userID = request.user.pk
            update_Mongo(folder,'aerial',full_path,timestamp,userID,True)
            return HttpResponse(json.dumps(ret_json), content_type="application/json")

    
    def delete(self, request):
        "Delete existing File/Directory."
        query = request.GET
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))
        fileobject = FileObject(os.path.join(path, query.get('filename', '')), site=self)

        if request.GET:
            try:
                signals.filebrowser_pre_delete.send(sender=request, path=fileobject.path, name=fileobject.filename, site=self)
                fileobject.delete_versions()
                fileobject.delete()

                # delete document from the mongoDB
                if (fileobject.filetype == "Folder") :
                    delete_file_data(False,os.path.join(BASE_DIR,path, query.get('filename', '')),request.user.pk)
                else :
                    delete_file_data(True,os.path.join(BASE_DIR,path, query.get('filename', '')),request.user.pk)


                signals.filebrowser_post_delete.send(sender=request, path=fileobject.path, name=fileobject.filename, site=self)
                messages.add_message(request, messages.SUCCESS, _('Successfully deleted %s') % fileobject.filename)
            except OSError:
                # TODO: define error-message
                pass
        redirect_url = reverse("filebrowser:fb_browse", current_app=self.name) + query_helper(query, "", "filename,filetype")
        return HttpResponseRedirect(redirect_url)


storage = DefaultStorage()
# imgapp FileBrowser site
site = UserFileBrowserSite(name='filebrowser', storage=storage)

# Default actions
from filebrowser.actions import flip_horizontal, flip_vertical, rotate_90_clockwise, rotate_90_counterclockwise, rotate_180
site.add_action(flip_horizontal)
site.add_action(flip_vertical)
site.add_action(rotate_90_clockwise)
site.add_action(rotate_90_counterclockwise)
site.add_action(rotate_180)



# from filebrowser.settings import (DIRECTORY, EXTENSIONS, SELECT_FORMATS, ADMIN_VERSIONS, ADMIN_THUMBNAIL, MAX_UPLOAD_SIZE, NORMALIZE_FILENAME,
#                                   CONVERT_FILENAME, SEARCH_TRAVERSE, EXCLUDE, VERSIONS, VERSIONS_BASEDIR, EXTENSION_LIST, DEFAULT_SORTING_BY, DEFAULT_SORTING_ORDER,
#                                   LIST_PER_PAGE, OVERWRITE_EXISTING, DEFAULT_PERMISSIONS, UPLOAD_TEMPDIR)
