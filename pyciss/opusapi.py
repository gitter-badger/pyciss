from urllib.request import unquote
from urllib.parse import urlparse, urlencode, urlunparse
import requests
from IPython.display import HTML, display

base_url = 'http://pds-rings-tools.seti.org/opus/api'
details_url = base_url + 'metadata/'
image_url = base_url + 'image/'
images_url = base_url + 'images/'

srings_ciss_query = {'target': 'S+RINGS',
                     'instrumentid': 'Cassini+ISS'}


class OPUSImage(object):
    """Manage URLS from the OPUS response."""
    def __init__(self, jsonlist):
        self.jsonlist = jsonlist
        for item in jsonlist:
            parsed = urlparse(item)
            if '//' in parsed.path:
                continue
            if item.upper().endswith(".LBL"):
                self.label_url = item
            elif item.upper().endswith('.IMG'):
                self.image_url = item

    def __repr__(self):
        s = "Label:\n{}\nImage:\n{}".format(self.label_url,
                                            self.image_url)
        return s


class OPUSObsID(object):
    """Manage observation IDs from OPUS responses."""
    def __init__(self, obsid_data):
        self.idname = obsid_data[0]
        self.raw = OPUSImage(obsid_data[1]['RAW_IMAGE'])
        self.calib = OPUSImage(obsid_data[1]['CALIBRATED'])

    def get_img_url(self, size):
        base = self.raw.label_url[:-4].replace('volumes', 'browse')
        return "{}_{}.jpg".format(base, size)

    @property
    def small_img_url(self):
        return self.get_img_url('small')

    @property
    def medium_img_url(self):
        return self.get_img_url('med')

    @property
    def thumb_img_url(self):
        return self.get_img_url('thumb')

    @property
    def full_img_url(self):
        return self.get_img_url('full')

    def __repr__(self):
        s = "Raw:\n{}\nCalibrated:\n{}".format(self.raw, self.calib)
        return s


class OPUS(object):
    """Manage OPUS API requests."""

    def get_filename(self, fname):
        """Receive CISS image via it's filename.

        This example receives an image of Titan:

        >>> opus = io.Opus()
        >>> opus.get_filename('N1695760475_1')
        """
        myquery = {'primaryfilespec': fname}
        self.create_files_request(myquery, fmt='json')
        self.unpack_json_response()
        return self.obsids

    def get_image(self, obsid, size='med', return_url=False):
        """size can be thumb,small,med,full """
        r = requests.get("{image_url}{size}/{obsid}.html"
                         .format(image_url=self.image_url,
                                 size=size,
                                 obsid=obsid))
        if return_url:
            return r.url
        else:
            return HTML(r.text)

    def get_details(self, obsid, fmt='html', get_response=False):
        r = requests.get(self.details_url + obsid + '.' + fmt)
        if get_response:
            return r
        elif fmt == 'html':
            return HTML(r.text)
        elif fmt == 'json':
            return r.json()

    def create_request_with_query(self, kind, query, size='thumb', fmt='json'):
        """api/data.[fmt], api/images/[size].[fmt] api/files.[fmt]

        kind = ['data', 'images', 'files']


        """
        if kind == 'data' or kind == 'files':
            url = "{}/{}.{}".format(base_url, kind, fmt)
        elif kind == 'images':
            url = "{}/images/{}.{}".format(base_url, size, fmt)
        self.r = requests.get(url,
                              params=unquote(urlencode(query)))

    def create_files_request(self, query, fmt='json'):
        self.create_request_with_query('files', query, fmt=fmt)

    def create_images_request(self, query, size='thumb', fmt='html'):
        self.create_request_with_query('images', query, size=size, fmt=fmt)

    # def create_data_request(self, query, fmt='json'):
    #     myquery = query.copy()
    #     myquery.update(query)
    #     self.create_request_with_query('data', myquery, fmt=fmt)

    def unpack_json_response(self):
        response = self.r.json()['data']
        obsids = []
        for obsid_data in response.items():
            obsids.append(OPUSObsID(obsid_data))
        self.obsids = obsids

    def get_radial_res_query(self, res1='', res2=0.5):
        myquery = srings_ciss_query.copy()
        myquery['projectedradialresolution1'] = res1
        myquery['projectedradialresolution2'] = res2
        return myquery

    def get_between_resolutions(self, res1='', res2='0.5'):
        myquery = self.get_radial_res_query(res1, res2)
        self.create_files_request(myquery, fmt='json')
        self.unpack_json_response()

    def show_images(self, size='small'):
        if size == 'small':
            width = 256
        elif size == 'med':
            width = 512
        elif size == 'thumb':
            width = 100
        elif size == 'full':
            width = 1024
        img_urls = [i.get_img_url(size) for i in self.obsids]
        imagesList = ''.join(["<img style='width: {0}px; margin: 0px; float: "
                              "left; border: 1px solid black;' "
                              "src='{1}' />"
                              .format(width, s) for s in img_urls])
        return HTML(imagesList)
