from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, SelectField,TextAreaField
from wtforms.validators import Required, Length, Email
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import ValidationError
from ..models import ImgTag, Actor

class Img_tagForm(FlaskForm):
    txtTitle = StringField('', validators=[Required()])
    txtSortId = StringField('', validators=[Required()])
    btnSubmit = SubmitField(u'提交保存')


class PhotoForm(FlaskForm):
    name = StringField('', validators=[Required()])
    tids = SelectMultipleField('', validators=[Required()])
    imgurls = StringField('')
    stats = SelectField('', validators=[Required()])
    submit =SubmitField(u'提交保存')
    actorid = SelectField('')

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.tids.choices = [(str(x.id), x.name) for x in ImgTag.query.all()]
        self.stats.choices = [('0','1'),('1','2'),('2','3'),('3','4'),('4','5')]
        self.actorid.choices = [(str(x.id), x.name) for x in Actor.query.all()]

