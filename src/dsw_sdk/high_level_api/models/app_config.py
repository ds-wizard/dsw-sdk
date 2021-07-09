from dsw_sdk.common.attributes import DateTimeAttribute, ObjectAttribute
from dsw_sdk.high_level_api.dto.app_config import (
    AppConfigAuth,
    AppConfigChangeDTO,
    AppConfigDashboard,
    AppConfigKnowledgeModel,
    AppConfigLookAndFeel,
    AppConfigOrganization,
    AppConfigPrivacyAndSupport,
    AppConfigQuestionnaire,
    AppConfigRegistry,
    AppConfigSubmission,
    AppConfigTemplate,
)
from dsw_sdk.high_level_api.models.model import Model


class AppConfig(Model):
    authentication = ObjectAttribute(AppConfigAuth)
    created_at = DateTimeAttribute()
    dashboard = ObjectAttribute(AppConfigDashboard)
    knowledge_model = ObjectAttribute(AppConfigKnowledgeModel)
    look_and_feel = ObjectAttribute(AppConfigLookAndFeel)
    organization = ObjectAttribute(AppConfigOrganization)
    privacy_and_support = ObjectAttribute(AppConfigPrivacyAndSupport)
    questionnaire = ObjectAttribute(AppConfigQuestionnaire)
    registry = ObjectAttribute(AppConfigRegistry)
    submission = ObjectAttribute(AppConfigSubmission)
    template = ObjectAttribute(AppConfigTemplate)
    updated_at = DateTimeAttribute()

    def _create(self):
        raise NotImplementedError('Cannot create config')

    def _update(self):
        dto = AppConfigChangeDTO(**self.attrs())
        dto.validate()
        data = self._sdk.api.put_configs_app(body=dto.to_json()).json()
        self._update_attrs(**data)

    def _delete(self):
        raise NotImplementedError('Cannot delete config')
