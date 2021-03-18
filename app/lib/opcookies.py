from flask import make_response


class Cookies(object):
    def __init__(self, url):
        self.response = make_response(url)
#     if request.cookies.get('cfile'):
#         response = make_response(url_for('auth.movie_add'))
#         response.delete_cookie('cfile')

# #    json_data = '''{"initview": ["http://lorempixel.com/1920/1080/nature/1"],"initconfig": [{"caption":"transport-1.jpg","size":"329892","url":"#","key":"1"}]}'''
#     json_data = json.dumps({
#         'initview':[
#             "/static/1.jpg",
#             "/static/2.jpg"
#             ],
#         "initconfig":[
#             {"caption":"transport-1.jpg","size":"329892","url":"/delete","key":"1"},
#             {"caption":"transport-2.jpg","size":"329892","url":"/delete","key":"2"}
#             ]
#         })
#     response = make_response(render_template('auth/movieAdd.html', form=form))
#     response.set_cookie(key='cfile',value=quote(json_data))
#     response.set_cookie(key='file',value='sdfsf')
#     if form.validate_on_submit():
#         return str(form.tags.data)
#    form.actors.data = [int(x.id) for x in Actor.query.all()]
#     return response

    