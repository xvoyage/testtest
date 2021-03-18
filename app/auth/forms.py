# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, SelectField,TextAreaField
from wtforms.validators import Required, Length, Email, EqualTo
from flask_wtf.file import FileAllowed, FileField, FileRequired
from ..models import User, Category, Movie, Actor, Tag, Settings, Director, Producer, Series
from flask_uploads import UploadSet, IMAGES
from flask_ckeditor import CKEditorField
from wtforms import ValidationError
import re

class LoginForm(FlaskForm):
    email = StringField('', validators=[Required(), Length(1,64),
                            Email()])
    password = PasswordField('', validators=[Required()])
    remember_me = BooleanField('')
    submit = SubmitField('登录')


class MyEqualTo(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if not field.data and not other.data:
            # d = {
            #     'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
            #     'other_name': self.fieldname
            # }
            message = self.message
            if message is None:
                message = field.gettext('Field must be equal.')

            raise ValidationError(message)

class MovieForm(FlaskForm):
    # cid = SelectMultipleField('', validators=[Required()])
    # cid = SelectMultipleField('', validators=[MyEqualTo('cid_text')])
    # cid_text = StringField('')
    aid = SelectMultipleField('', validators=[MyEqualTo('aid_text')])
    aid_text = StringField('')
    tid = SelectMultipleField('',validators=[MyEqualTo('tid_text')])
    tid_text = StringField('')
    stats = SelectMultipleField('', validators=[Required()])
    title = StringField('',validators=[Required()])
    name = StringField('', validators=[Required()])
    des = CKEditorField('')
    imgurl = StringField('', validators=[Required()])
    movieurl = StringField('')
    bsname = StringField('')
    ares = SelectMultipleField('', validators=[Required()])
    splitfile = BooleanField('')
    submit =SubmitField(u'提交保存')
    date = StringField('')
    ischinese = BooleanField('')
    isperview = BooleanField('')
    director = SelectMultipleField('') #导演
    director_text = StringField('')
    producer = SelectMultipleField('') #片商
    producer_text = StringField('')
    series = SelectMultipleField('') #片商
    series_text = StringField('')
    ismove = StringField('')


    def __init__(self, *args, **kwargs):
        super(MovieForm, self).__init__(*args, **kwargs)
        # self.cid.choices = [(str(x.id), x.name) for x in Category.query.order_by(Category.id.desc()).all()]
        self.aid.choices = [(str(x.id), x.name) for x in Actor.query.order_by(Actor.id.desc()).all()]
        self.tid.choices = [(str(x.id), x.name) for x in Tag.query.all()]
        self.stats.choices = [('0','1'),('1','2'),('2','3'),('3','4'),('4','5')]
        self.ares.choices = [('0','日本'),('1','国产'),('2','欧美')]
        self.director.choices =[(str(x.id), x.name) for x in Director.query.order_by(Director.id.desc()).all()]
        self.producer.choices = [(str(x.id), x.name) for x in Producer.query.order_by(Producer.id.desc()).all()]
        self.series.choices = [(str(x.id), x.name) for x in Series.query.order_by(Series.id.desc()).all()]
        # setstatus = Settings.query.first()
        # self.splitfile.default = setstatus.splitfile
        # print(self.splitfile.default)

    def validate_name(self, field):
        pattern = re.compile(r'^[a-zA-Z]+-[0-9]+(-[a-zA-Z])?$')
        result = re.search(pattern, field.data)
        if not result:
            raise ValidationError('番号格式不正确')






class CategoryForm(FlaskForm):

    ddlParentId = SelectField('',validators=[Required()])

    txtTitle = StringField('', validators=[Required()])
    txtSortId = StringField('', validators=[Required()])
    txtDescription = CKEditorField('')
    btnSubmit = SubmitField(u'提交保存')

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.ddlParentId.choices = [(str(x.id), x.name) for x in Category.query.all()]



class TagForm(FlaskForm):
    txtTitle = StringField('', validators=[Required()])
    txtSortId = StringField('', validators=[Required()])
    btnSubmit = SubmitField(u'提交保存')


class ActorForm(FlaskForm):
    txtTitle = StringField('', validators=[Required()])
    txtSortId = StringField('', validators=[Required()])
    txtDescription = CKEditorField('')
    imgurl = StringField('')
    btnSubmit = SubmitField(u'提交保存')


class DiskForm(FlaskForm):
    # DeviceID = StringField('', validators=[Required()])
    # SerialNumber = StringField('', validators=[Required()])
    # DiskTotal = StringField('', validators=[Required()])
    alisename = StringField('', validators=[Required()])
    part = StringField('', validators=[Required()])
    submit = SubmitField(u'提交') 


class SettingForm(FlaskForm):
    # source_dir = StringField('', validators=[Required()])
    cpOrmv = BooleanField('')
    splitfile = BooleanField('')
    show = BooleanField('')
    preview = BooleanField('')
    submit = SubmitField(u'提交')


class ZimuForm(FlaskForm):

    title = StringField('',validators=[Required()])
    name = StringField('', validators=[Required()])
    imgurl = StringField('', validators=[Required()])
    movieurl = StringField('', validators=[Required()])
    submit =SubmitField(u'提交保存')
