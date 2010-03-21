from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, TemplateDoesNotExist
from django.contrib.auth.decorators import login_required
from django import forms

from django.utils import simplejson
from md5 import md5
from wui.api.js_utils import create_documentation
from wui.settings import *

import zipfile, mimetypes
import glob

from pprint import pprint
import os

def index(request):
    doc = create_documentation(WUI_JS_DIR + '/wui.js')
    return render_to_response('api_index.html', locals(), context_instance=RequestContext(request))

def doc_namespace(request, ns):
    doc = create_documentation(WUI_JS_DIR + '/wui.js')
    ns = doc['ns'][ns]
    return render_to_response('api_doc_namespace.html', locals(), context_instance=RequestContext(request))

def doc_class(request, ns, cls):
    try:
        doc = create_documentation(WUI_JS_DIR + '/wui.js')
        ns = doc['ns'][ns]
        clazz = ns['classes'][cls]
        
        include = 'api_%s-%s.html' % (ns['namespace'].lower().strip(), clazz['class'].lower().strip())
        if not os.path.exists(os.path.join(TEMPLATE_DIRS, include)):
            include = None

        return render_to_response('api_doc_class.html', locals(), context_instance=RequestContext(request))
    except Exception:
        raise Http404()

def countries_json(request):
    if 's' in request.POST:
        search = request.POST['s']
    elif 's' in request.GET:
        search = request.GET['s']
    else:
        search = None
        countries = []
    
    if search != None:
        search = search.lower()
        countries = filter(lambda x: search != None and x.lower().find(search) != -1, load_countries())
        
    json = map(item_transformer, countries)
    return HttpResponse(simplejson.dumps(json), content_type='application/json')

def download(request):
    import tempfile
    name = 'wui-1.1'
    zipname = '%s.%s' % (name, 'zip')
    filename = os.path.join(tempfile.gettempdir(), zipname)
    #try:
    createZipFile(filename, name)
    response = HttpResponse(open(filename).read(), mimetype=mimetypes.guess_type(filename))
    response['Content-Disposition'] = 'attachment; filename=%(zipname)s' % locals()
    #except:
    #    response = Http404()
        
    if os.path.exists(filename):
        os.remove(filename)
        
    return response

## Utils

def addDirInFile(myzipfile, directory, root_dir, container=None):
    for root, dirs, files in os.walk(directory):
        if '.git' in root or '.svn' in root:
            continue
        
        dirname = root[len(root_dir):]
        print root
        print root_dir
        print dirname
        for file in files:
            if container:
                dirname = os.path.join(container, dirname)
            myzipfile.write(os.path.join(root,file), dirname + '/' +os.path.basename(file), zipfile.ZIP_DEFLATED)
    
    
def createZipFile(filename, container=None):
    myzipfile = zipfile.ZipFile(filename, "w" )
    addDirInFile(myzipfile, os.path.join(PROJECT_DIR, 'lib'), PROJECT_DIR, container)
    addDirInFile(myzipfile, os.path.join(PROJECT_DIR, 'src', 'js'), PROJECT_DIR, container)
    myzipfile.close()

def item_transformer(value):
    return {
        'id':md5(value).hexdigest(),
        'label':value,
    }
    
def load_countries():
    return (
        'Afghanistan',
        'Albania',
        'Algeria',
        'Andorra',
        'Angola',
        'Antigua & Deps',
        'Argentina',
        'Armenia',
        'Australia',
        'Austria',
        'Azerbaijan',
        'Bahamas',
        'Bahrain',
        'Bangladesh',
        'Barbados',
        'Belarus',
        'Belgium',
        'Belize',
        'Benin',
        'Bhutan',
        'Bolivia',
        'Bosnia Herzegovina',
        'Botswana',
        'Brazil',
        'Brunei',
        'Bulgaria',
        'Burkina',
        'Burundi',
        'Cambodia',
        'Cameroon',
        'Canada',
        'Cape Verde',
        'Central African Rep',
        'Chad',
        'Chile',
        'China',
        'Colombia',
        'Comoros',
        'Congo',
        'Congo {Democratic Rep}',
        'Costa Rica',
        'Croatia',
        'Cuba',
        'Cyprus',
        'Czech Republic',
        'Denmark',
        'Djibouti',
        'Dominica',
        'Dominican Republic',
        'East Timor',
        'Ecuador',
        'Egypt',
        'El Salvador',
        'Equatorial Guinea',
        'Eritrea',
        'Estonia',
        'Ethiopia',
        'Fiji',
        'Finland',
        'France',
        'Gabon',
        'Gambia',
        'Georgia',
        'Germany',
        'Ghana',
        'Greece',
        'Grenada',
        'Guatemala',
        'Guinea',
        'Guinea-Bissau',
        'Guyana',
        'Haiti',
        'Honduras',
        'Hungary',
        'Iceland',
        'India',
        'Indonesia',
        'Iran',
        'Iraq',
        'Ireland {Republic}',
        'Israel',
        'Italy',
        'Ivory Coast',
        'Jamaica',
        'Japan',
        'Jordan',
        'Kazakhstan',
        'Kenya',
        'Kiribati',
        'Korea North',
        'Korea South',
        'Kosovo',
        'Kuwait',
        'Kyrgyzstan',
        'Laos',
        'Latvia',
        'Lebanon',
        'Lesotho',
        'Liberia',
        'Libya',
        'Liechtenstein',
        'Lithuania',
        'Luxembourg',
        'Macedonia',
        'Madagascar',
        'Malawi',
        'Malaysia',
        'Maldives',
        'Mali',
        'Malta',
        'Marshall Islands',
        'Mauritania',
        'Mauritius',
        'Mexico',
        'Micronesia',
        'Moldova',
        'Monaco',
        'Mongolia',
        'Montenegro',
        'Morocco',
        'Mozambique',
        'Myanmar, {Burma}',
        'Namibia',
        'Nauru',
        'Nepal',
        'Netherlands',
        'New Zealand',
        'Nicaragua',
        'Niger',
        'Nigeria',
        'Norway',
        'Oman',
        'Pakistan',
        'Palau',
        'Panama',
        'Papua New Guinea',
        'Paraguay',
        'Peru',
        'Philippines',
        'Poland',
        'Portugal',
        'Qatar',
        'Romania',
        'Russian Federation',
        'Rwanda',
        'St Kitts & Nevis',
        'St Lucia',
        'Saint Vincent & the Grenadines',
        'Samoa',
        'San Marino',
        'Sao Tome & Principe',
        'Saudi Arabia',
        'Senegal',
        'Serbia',
        'Seychelles',
        'Sierra Leone',
        'Singapore',
        'Slovakia',
        'Slovenia',
        'Solomon Islands',
        'Somalia',
        'South Africa',
        'Spain',
        'Sri Lanka',
        'Sudan',
        'Suriname',
        'Swaziland',
        'Sweden',
        'Switzerland',
        'Syria',
        'Taiwan',
        'Tajikistan',
        'Tanzania',
        'Thailand',
        'Togo',
        'Tonga',
        'Trinidad & Tobago',
        'Tunisia',
        'Turkey',
        'Turkmenistan',
        'Tuvalu',
        'Uganda',
        'Ukraine',
        'United Arab Emirates',
        'United Kingdom',
        'United States',
        'Uruguay',
        'Uzbekistan',
        'Vanuatu',
        'Vatican City',
        'Venezuela',
        'Vietnam',
        'Yemen',
        'Zambia',
        'Zimbabwe');