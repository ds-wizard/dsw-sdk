# pylint: disable-all

from __future__ import annotations

from typing import Any, Dict, Optional

from dsw_sdk.common.utils import to_camel_case
from dsw_sdk.http_client.interface import HttpClient, HttpResponse


class LowLevelAPI:
    """
    Low-level API mirroring 1:1 the Data Stewardship Wizard API. It contains
    one method for each combination of HTTP method and API endpoint.

    If the endpoint accepts query parameters or body, the method accept
    these as well. Keys in both query params and body are converted to
    `camelCase`, so you can pass them in `snake_case` if you want.

    Note that this class is *generated* by a script, not written by hand.
    """
    def __init__(self, http_client: HttpClient):
        """
        :param http_client: Some instance of the :class:`~interface.HttpClient`
                            interface.
        """
        self._http_client = http_client

    def _camelize_dict_keys(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {to_camel_case(k): self._camelize_dict_keys(v)
                    for k, v in data.items()}
        elif isinstance(data, list):
            return [self._camelize_dict_keys(val) for val in data]
        else:
            return data
    
    def post_questionnaire_migrations(self, qtn_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            targetTagUuids: array
            targetPackageId: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/questionnaires/{qtn_uuid}/migrations', body=body, **kwargs)
    
    def post_package_pull(self, pkg_id: str, **kwargs) -> HttpResponse:
        return self._http_client.post(f'/packages/{pkg_id}/pull', **kwargs)
    
    def post_branch_migrations_current_conflict(self, b_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            originalEventUuid: None
            action: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/branches/{b_uuid}/migrations/current/conflict', body=body, **kwargs)
    
    def post_templates(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            readme: string
            templateId: string
            formats: array
            metamodelVersion: integer
            name: string
            version: string
            license: string
            organizationId: string
            description: string
            allowedPackages: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/templates', body=body, **kwargs)
    
    def get_templates(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            organizationId [optional]: string
            templateId [optional]: string
            q [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/templates', params=query_params, **kwargs)
    
    def delete_templates(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            organizationId [optional]: string
            templateId [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.delete(f'/templates', params=query_params, **kwargs)
    
    def get_questionnaire(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/questionnaires/{qtn_uuid}', **kwargs)
    
    def delete_questionnaire(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/questionnaires/{qtn_uuid}', **kwargs)
    
    def put_questionnaire(self, qtn_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            isTemplate: boolean
            visibility: None
            name: string
            permissions: array
            sharing: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/questionnaires/{qtn_uuid}', body=body, **kwargs)
    
    def delete_document(self, doc_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/documents/{doc_uuid}', **kwargs)
    
    def post_questionnaires_from_template(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            name: string
            questionnaireUuid: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/questionnaires/from-template', body=body, **kwargs)
    
    def get_feedback(self, f_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/feedbacks/{f_uuid}', **kwargs)
    
    def post_templates_bundle(self, **kwargs) -> HttpResponse:
        return self._http_client.post(f'/templates/bundle', **kwargs)
    
    def get_questionnaire_documents_preview(self, qtn_uuid: str, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            Authorization [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/questionnaires/{qtn_uuid}/documents/preview', params=query_params, **kwargs)
    
    def put_questionnaire_content(self, qtn_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            events: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/questionnaires/{qtn_uuid}/content', body=body, **kwargs)
    
    def get_templates_all(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            organizationId [optional]: string
            templateId [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/templates/all', params=query_params, **kwargs)
    
    def get_questionnaire_migrations_current(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/questionnaires/{qtn_uuid}/migrations/current', **kwargs)
    
    def delete_questionnaire_migrations_current(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/questionnaires/{qtn_uuid}/migrations/current', **kwargs)
    
    def put_questionnaire_migrations_current(self, qtn_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            resolvedQuestionUuids: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/questionnaires/{qtn_uuid}/migrations/current', body=body, **kwargs)
    
    def post_template_files(self, template_id: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            content: string
            fileName: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/templates/{template_id}/files', body=body, **kwargs)
    
    def get_template_files(self, template_id: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/templates/{template_id}/files', **kwargs)
    
    def post_registry_confirmation(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            hash: string
            organizationId: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/registry/confirmation', body=body, **kwargs)
    
    def post_users(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            email: string
            lastName: string
            password: string
            firstName: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/users', body=body, **kwargs)
    
    def get_users(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            q [optional]: string
            role [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/users', params=query_params, **kwargs)
    
    def post_branch_migrations_current(self, b_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            targetTagUuids: array
            targetPackageId: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/branches/{b_uuid}/migrations/current', body=body, **kwargs)
    
    def get_branch_migrations_current(self, b_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/branches/{b_uuid}/migrations/current', **kwargs)
    
    def delete_branch_migrations_current(self, b_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/branches/{b_uuid}/migrations/current', **kwargs)
    
    def get_package_bundle(self, pkg_id: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/packages/{pkg_id}/bundle', **kwargs)
    
    def get_questionnaire_report(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/questionnaires/{qtn_uuid}/report', **kwargs)
    
    def get_template_asset(self, template_id: str, asset_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/templates/{template_id}/assets/{asset_uuid}', **kwargs)
    
    def delete_template_asset(self, template_id: str, asset_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/templates/{template_id}/assets/{asset_uuid}', **kwargs)
    
    def post_questionnaire_clone(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.post(f'/questionnaires/{qtn_uuid}/clone', **kwargs)
    
    def delete_questionnaire_version(self, qtn_uuid: str, v_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/questionnaires/{qtn_uuid}/versions/{v_uuid}', **kwargs)
    
    def put_questionnaire_version(self, qtn_uuid: str, v_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            eventUuid: None
            name: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/questionnaires/{qtn_uuid}/versions/{v_uuid}', body=body, **kwargs)
    
    def post_action_keys(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            email: string
            type: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/action-keys', body=body, **kwargs)
    
    def get_users_current(self, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/users/current', **kwargs)
    
    def put_users_current(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            email: string
            lastName: string
            firstName: string
            submissionProps: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/users/current', body=body, **kwargs)
    
    def get_configs_bootstrap(self, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/configs/bootstrap', **kwargs)
    
    def post_questionnaires(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            tagUuids: array
            packageId: string
            visibility: None
            name: string
            sharing: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/questionnaires', body=body, **kwargs)
    
    def get_questionnaires(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            q [optional]: string
            isTemplate [optional]: boolean
            userUuids [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/questionnaires', params=query_params, **kwargs)
    
    def get_auth(self, id: str, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            clientUrl [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/auth/{id}', params=query_params, **kwargs)
    
    def post_document_submissions(self, doc_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            serviceId: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/documents/{doc_uuid}/submissions', body=body, **kwargs)
    
    def get_document_submissions(self, doc_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/documents/{doc_uuid}/submissions', **kwargs)
    
    def post_registry_signup(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            email: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/registry/signup', body=body, **kwargs)
    
    def post_packages(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        return self._http_client.post(f'/packages', **kwargs)
    
    def get_packages(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            organizationId [optional]: string
            kmId [optional]: string
            q [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/packages', params=query_params, **kwargs)
    
    def delete_packages(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            organizationId [optional]: string
            kmId [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.delete(f'/packages', params=query_params, **kwargs)
    
    def post_questionnaire_revert(self, qtn_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            eventUuid: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/questionnaires/{qtn_uuid}/revert', body=body, **kwargs)
    
    def put_user_state(self, u_uuid: str, body: Dict[str, Any], query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        body:
            active: boolean
        
        query_params:
            hash [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/users/{u_uuid}/state', body=body, params=query_params, **kwargs)
    
    def put_user_password(self, u_uuid: str, body: Dict[str, Any], query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        body:
            password: string
        
        query_params:
            hash [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/users/{u_uuid}/password', body=body, params=query_params, **kwargs)
    
    def post_template_assets(self, template_id: str, **kwargs) -> HttpResponse:
        return self._http_client.post(f'/templates/{template_id}/assets', **kwargs)
    
    def get_template_assets(self, template_id: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/templates/{template_id}/assets', **kwargs)
    
    def get_user(self, u_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/users/{u_uuid}', **kwargs)
    
    def delete_user(self, u_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/users/{u_uuid}', **kwargs)
    
    def put_user(self, u_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            email: string
            lastName: string
            active: boolean
            role: string
            firstName: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/users/{u_uuid}', body=body, **kwargs)
    
    def post_questionnaire_revert_preview(self, qtn_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            eventUuid: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/questionnaires/{qtn_uuid}/revert/preview', body=body, **kwargs)
    
    def get_document_download(self, doc_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/documents/{doc_uuid}/download', **kwargs)
    
    def get_templates_suggestions(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            pkgId [optional]: string
            q [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/templates/suggestions', params=query_params, **kwargs)
    
    def post_tokens(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            email: string
            password: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/tokens', body=body, **kwargs)
    
    def post_caches_knowledge_model(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            tagUuids: array
            events: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/caches/knowledge-model', body=body, **kwargs)
    
    def get_document_available_submission_services(self, doc_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/documents/{doc_uuid}/available-submission-services', **kwargs)
    
    def post_typehints(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            questionUuid: None
            q: string
            events: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/typehints', body=body, **kwargs)
    
    def post_admin_operations_executions(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            operationName: string
            parameters: array
            sectionName: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/admin/operations/executions', body=body, **kwargs)
    
    def get_(self, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/', **kwargs)
    
    def get_questionnaire_documents(self, qtn_uuid: str, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            q [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/questionnaires/{qtn_uuid}/documents', params=query_params, **kwargs)
    
    def post_questionnaire_versions(self, qtn_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            eventUuid: None
            name: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/questionnaires/{qtn_uuid}/versions', body=body, **kwargs)
    
    def get_questionnaire_versions(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/questionnaires/{qtn_uuid}/versions', **kwargs)
    
    def post_template_pull(self, template_id: str, **kwargs) -> HttpResponse:
        return self._http_client.post(f'/templates/{template_id}/pull', **kwargs)
    
    def get_auth_callback(self, id: str, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            clientUrl [optional]: string
            error [optional]: string
            code [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/auth/{id}/callback', params=query_params, **kwargs)
    
    def post_packages_bundle(self, **kwargs) -> HttpResponse:
        return self._http_client.post(f'/packages/bundle', **kwargs)
    
    def post_feedbacks(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            packageId: string
            questionUuid: None
            content: string
            title: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/feedbacks', body=body, **kwargs)
    
    def get_feedbacks(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            packageId [optional]: string
            questionUuid [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/feedbacks', params=query_params, **kwargs)
    
    def post_branches(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            kmId: string
            name: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/branches', body=body, **kwargs)
    
    def get_branches(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            q [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/branches', params=query_params, **kwargs)
    
    def get_users_suggestions(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            q [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/users/suggestions', params=query_params, **kwargs)
    
    def get_book_reference(self, br_short_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/book-references/{br_short_uuid}', **kwargs)
    
    def get_feedbacks_synchronization(self, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/feedbacks/synchronization', **kwargs)
    
    def get_template_file(self, template_id: str, file_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/templates/{template_id}/files/{file_uuid}', **kwargs)
    
    def delete_template_file(self, template_id: str, file_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/templates/{template_id}/files/{file_uuid}', **kwargs)
    
    def put_template_file(self, template_id: str, file_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            content: string
            fileName: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/templates/{template_id}/files/{file_uuid}', body=body, **kwargs)
    
    def get_template(self, template_id: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/templates/{template_id}', **kwargs)
    
    def delete_template(self, template_id: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/templates/{template_id}', **kwargs)
    
    def put_template(self, template_id: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            readme: string
            templateId: string
            formats: array
            metamodelVersion: integer
            name: string
            version: string
            license: string
            organizationId: string
            description: string
            allowedPackages: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/templates/{template_id}', body=body, **kwargs)
    
    def delete_caches(self, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/caches', **kwargs)
    
    def get_configs_app(self, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/configs/app', **kwargs)
    
    def put_configs_app(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            privacyAndSupport: None
            authentication: None
            lookAndFeel: None
            dashboard: None
            questionnaire: None
            registry: None
            knowledgeModel: None
            submission: None
            template: None
            organization: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/configs/app', body=body, **kwargs)
    
    def put_users_current_password(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            password: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/users/current/password', body=body, **kwargs)
    
    def get_branch(self, b_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/branches/{b_uuid}', **kwargs)
    
    def delete_branch(self, b_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/branches/{b_uuid}', **kwargs)
    
    def put_branch(self, b_uuid: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            kmId: string
            name: string
            events: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/branches/{b_uuid}', body=body, **kwargs)
    
    def post_documents(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            templateId: string
            name: string
            questionnaireUuid: None
            formatUuid: None
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/documents', body=body, **kwargs)
    
    def get_documents(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            questionnaireUuid [optional]: string
            q [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/documents', params=query_params, **kwargs)
    
    def get_documents_housekeeping(self, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/documents/housekeeping', **kwargs)
    
    def get_template_bundle(self, template_id: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/templates/{template_id}/bundle', **kwargs)
    
    def get_template_asset_content(self, template_id: str, asset_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/templates/{template_id}/assets/{asset_uuid}/content', **kwargs)
    
    def get_packages_suggestions(self, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> HttpResponse:
        """
        query_params:
            q [optional]: string
            page [optional]: integer
            size [optional]: integer
            sort [optional]: string
        
        """
        query_params = self._camelize_dict_keys(query_params)
        return self._http_client.get(f'/packages/suggestions', params=query_params, **kwargs)
    
    def put_branch_version(self, b_uuid: str, version: str, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            readme: string
            license: string
            description: string
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.put(f'/branches/{b_uuid}/versions/{version}', body=body, **kwargs)
    
    def post_questionnaire_squash(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.post(f'/questionnaires/{qtn_uuid}/squash', **kwargs)
    
    def get_package(self, pkg_id: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/packages/{pkg_id}', **kwargs)
    
    def delete_package(self, pkg_id: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/packages/{pkg_id}', **kwargs)
    
    def post_knowledge_models_preview(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        """
        body:
            tagUuids: array
            events: array
        
        """
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/knowledge-models/preview', body=body, **kwargs)
    
    def post_questionnaire_migrations_current_completion(self, qtn_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.post(f'/questionnaires/{qtn_uuid}/migrations/current/completion', **kwargs)
    
    def get_admin_operations(self, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/admin/operations', **kwargs)
