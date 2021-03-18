from ..models import Settings

class SettingController(object):

    def get_settings(self):
        sett = Settings.query.first()
        if not sett:
            sett = Settings(
                cpOrmv = False,
                splitfile = False,
                show = False,
                perview = False
            )
        return sett


    # def bind_form_to_data(self,formdata):
