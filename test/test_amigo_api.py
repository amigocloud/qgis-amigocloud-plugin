from amigo_api import AmigoAPI
import urllib

def test_project_list():
    amigo_api = AmigoAPI()
    pl = amigo_api.fetch_project_list()
    print(pl)

def test_preview_image():
    amigo_api = AmigoAPI()
    pl = amigo_api.fetch_project_list()
    for p in pl:
        url = p['preview_image'] + '?token=A:A0DlLhxbCUCqNB5ETowpshV56Abw8mmxSl66BE'
        data = urllib.request.urlopen(url).read()
        print(data)

test_preview_image()