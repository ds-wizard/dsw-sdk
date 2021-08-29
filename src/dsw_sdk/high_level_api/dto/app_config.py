from dsw_sdk.common.attributes import (
    AttributesMixin,
    BoolAttribute, DictAttribute, ListAttribute,
    ObjectAttribute,
    StringAttribute,
)
from dsw_sdk.common.types import ObjectType, StringType
from dsw_sdk.high_level_api.dto.questionnaire import (
    QUESTIONNAIRE_SHARING,
    QUESTIONNAIRE_VISIBILITIES,
)


CUSTOM_QUESTIONNAIRE_CREATION = 'CustomQuestionnaireCreation'
TEMPLATE_QUESTIONNAIRE_CREATION = 'TemplateQuestionnaireCreation'
TEMPLATE_AND_CUSTOM_QUESTIONNAIRE_CREATION = (
    'TemplateAndCustomQuestionnaireCreation'
)
QUESTIONNAIRE_CREATION = (
    CUSTOM_QUESTIONNAIRE_CREATION,
    TEMPLATE_QUESTIONNAIRE_CREATION,
    TEMPLATE_AND_CUSTOM_QUESTIONNAIRE_CREATION,
)


class PackagePattern(AttributesMixin):
    km_id = StringAttribute(nullable=True)
    max_version = StringAttribute(nullable=True)
    min_version = StringAttribute(nullable=True)
    org_id = StringAttribute(nullable=True)


class AppConfigKnowledgeModelPublic(AttributesMixin):
    enabled = BoolAttribute()
    packages = ListAttribute(ObjectType(PackagePattern))


class AppConfigKnowledgeModel(AttributesMixin):
    public = ObjectAttribute(AppConfigKnowledgeModelPublic)


class AppConfigOrganization(AttributesMixin):
    affiliations = ListAttribute(StringType())
    description = StringAttribute()
    name = StringAttribute()
    organization_id = StringAttribute()


class SimpleFeature(AttributesMixin):
    enabled = BoolAttribute()


class AppConfigAuthInternal(AttributesMixin):
    registration = ObjectAttribute(SimpleFeature)


class AppConfigAuthExternalServiceParameter(AttributesMixin):
    name = StringAttribute()
    value = StringAttribute()


class AppConfigAuthExternalServiceStyle(AttributesMixin):
    background = StringAttribute(nullable=True)
    color = StringAttribute(nullable=True)
    icon = StringAttribute(nullable=True)


class AppConfigAuthExternalService(AttributesMixin):
    client_id = StringAttribute()
    client_secret = StringAttribute()
    id = StringAttribute()
    name = StringAttribute()
    parameteres = ListAttribute(
        ObjectType(AppConfigAuthExternalServiceParameter)
    )
    style = ObjectAttribute(AppConfigAuthExternalServiceStyle, nullable=True)
    url = StringAttribute()


class AppConfigAuthExternal(AttributesMixin):
    services = ListAttribute(ObjectType(AppConfigAuthExternalService))


class AppConfigAuth(AttributesMixin):
    default_role = StringAttribute()
    internal = ObjectAttribute(AppConfigAuthInternal)
    external = ObjectAttribute(AppConfigAuthExternal)


class AppConfigPrivacyAndSupport(AttributesMixin):
    privacy_url = StringAttribute(nullable=True)
    support_email = StringAttribute(nullable=True)
    support_repository_name = StringAttribute(nullable=True)
    support_repository_url = StringAttribute(nullable=True)
    terms_of_service_url = StringAttribute(nullable=True)


class AppConfigDashboardWidgets(AttributesMixin):
    admin = ListAttribute(StringType())
    data_steward = ListAttribute(StringType())
    researcher = ListAttribute(StringType())


class AppConfigDashboard(AttributesMixin):
    welcome_info = StringAttribute(nullable=True)
    welcome_warning = StringAttribute(nullable=True)
    widgets = ObjectAttribute(AppConfigDashboardWidgets, nullable=True)


class AppConfigLookAndFeelCustomMenuLink(AttributesMixin):
    icon = StringAttribute()
    new_window = BoolAttribute()
    title = StringAttribute()
    url = StringAttribute()


class AppConfigLookAndFeel(AttributesMixin):
    app_title = StringAttribute(nullable=True)
    app_title_short = StringAttribute(nullable=True)
    custom_menu_links = ListAttribute(
        ObjectType(AppConfigLookAndFeelCustomMenuLink)
    )
    login_info = StringAttribute(nullable=True)


class AppConfigRegistry(AttributesMixin):
    enabled = BoolAttribute()
    token = StringAttribute()


class AppConfigQuestionnaireVisibility(AttributesMixin):
    default_value = StringAttribute(choices=QUESTIONNAIRE_VISIBILITIES)
    enabled = BoolAttribute()


class AppConfigQuestionnaireSharing(AttributesMixin):
    anonymous_enabled = BoolAttribute()
    default_value = StringAttribute(choices=QUESTIONNAIRE_SHARING)
    enabled = BoolAttribute()


class AppConfigQuestionnaireFeedback(AttributesMixin):
    enabled = BoolAttribute()
    owner = StringAttribute()
    repo = StringAttribute()
    token = StringAttribute()


class AppConfigQuestionnaire(AttributesMixin):
    feedback = ObjectAttribute(AppConfigQuestionnaireFeedback)
    questionnaire_creation = StringAttribute(choices=QUESTIONNAIRE_CREATION)
    questionnaire_sharing = ObjectAttribute(AppConfigQuestionnaireSharing)
    questionnaire_visibility = ObjectAttribute(
        AppConfigQuestionnaireVisibility
    )
    summary_report = ObjectAttribute(SimpleFeature)


class AppConfigTemplate(AttributesMixin):
    recommended_template_id = StringAttribute(nullable=True)


class AppConfigSubmissionServiceSupportedFormat(AttributesMixin):
    format_uuid = StringAttribute()
    template_id = StringAttribute()


class AppConfigSubmissionServiceRequestMultipart(AttributesMixin):
    enabled = BoolAttribute()
    file_name = StringAttribute()


class AppConfigSubmissionServiceRequest(AttributesMixin):
    headers = DictAttribute(StringType(), StringType())
    method = StringAttribute()
    multipart = ObjectAttribute(AppConfigSubmissionServiceRequestMultipart)
    url = StringAttribute()


class AppConfigSubmissionService(AttributesMixin):
    description = StringAttribute()
    id = StringAttribute()
    name = StringAttribute()
    props = ListAttribute(StringType())
    request = ObjectAttribute(AppConfigSubmissionServiceRequest)
    supported_formats = ListAttribute(
        ObjectType(AppConfigSubmissionServiceSupportedFormat)
    )


class AppConfigSubmission(AttributesMixin):
    enabled = BoolAttribute()
    services = ListAttribute(ObjectType(AppConfigSubmissionService))


class AppConfigChangeDTO(AttributesMixin):
    authentication = ObjectAttribute(AppConfigAuth)
    dashboard = ObjectAttribute(AppConfigDashboard)
    knowledge_model = ObjectAttribute(AppConfigKnowledgeModel)
    look_and_feel = ObjectAttribute(AppConfigLookAndFeel)
    organization = ObjectAttribute(AppConfigOrganization)
    privacy_and_support = ObjectAttribute(AppConfigPrivacyAndSupport)
    questionnaire = ObjectAttribute(AppConfigQuestionnaire)
    registry = ObjectAttribute(AppConfigRegistry)
    submission = ObjectAttribute(AppConfigSubmission)
    template = ObjectAttribute(AppConfigTemplate)
