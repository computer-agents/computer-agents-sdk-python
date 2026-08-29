"""Metronome workflow resource APIs and workflow authoring primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Sequence
from uuid import uuid4

from .._api_client import ApiClient
from .versioning import format_version_label, normalize_version_number


class SupportsToDict(Protocol):
    """Object that can be serialized into a Computer Agents API payload."""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        ...


def _merge_config(
    config: Mapping[str, Any] | None,
    extra_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    if config:
        merged.update(dict(config))
    if extra_config:
        merged.update(dict(extra_config))
    return merged


def _drop_none(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item is not None}


def _definition_to_dict(definition: Mapping[str, Any] | SupportsToDict | None) -> dict[str, Any] | None:
    if definition is None:
        return None
    if hasattr(definition, "to_dict"):
        return definition.to_dict()
    return dict(definition)


@dataclass
class MetronomeNode:
    """A node in a Metronome workflow graph.

    Metronome uses explicit node objects for authoring and serializes them to
    the stable API definition shape at the boundary. This mirrors the authoring
    style of agent SDKs where developers compose typed objects and the SDK takes
    care of payload serialization.
    """

    id: str
    kind: str
    subtype: str | None = None
    label: str | None = None
    description: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    position: dict[str, float] | None = None
    parent_id: str | None = None
    extent: str | None = None
    style: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = _drop_none(
            {
                "id": self.id,
                "kind": self.kind,
                "subtype": self.subtype,
                "label": self.label,
                "description": self.description,
                "config": dict(self.config or {}),
                "position": dict(self.position) if self.position else None,
                "parentId": self.parent_id,
                "extent": self.extent,
                "style": dict(self.style) if self.style else None,
            }
        )
        return payload


class TriggerNode(MetronomeNode):
    """Start a workflow from a schedule, connector event, thread, project, or resource event."""

    def __init__(
        self,
        id: str,
        trigger_type: str = "manual",
        *,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            kind="trigger",
            subtype=trigger_type,
            label=label,
            description=description,
            config=_merge_config(config, extra_config),
            position=position,
        )


class ThreadEventTriggerNode(TriggerNode):
    """Start a workflow when a thread message begins with a command."""

    def __init__(
        self,
        id: str,
        *,
        command: str | None = None,
        prompt_extension: str | None = None,
        attachments: Sequence[Mapping[str, Any]] | str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        attachments_json: str | None = None
        normalized_attachments: list[dict[str, Any]] | None = None
        if isinstance(attachments, str):
            attachments_json = attachments
        elif attachments is not None:
            normalized_attachments = [dict(item) for item in attachments]
        super().__init__(
            id=id,
            trigger_type="thread_event",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "thread_event",
                        "threadCommand": command,
                        "promptExtension": prompt_extension,
                        "attachmentsJson": attachments_json,
                        "attachments": normalized_attachments,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class PeriodicScheduleTriggerNode(TriggerNode):
    """Start a workflow from a one-time or recurring schedule."""

    def __init__(
        self,
        id: str,
        *,
        schedule_type: str | None = "one-time",
        scheduled_time: str | None = None,
        cron_expression: str | None = None,
        schedule_preset_id: str | None = None,
        schedule_timezone: str | None = None,
        prompt_extension: str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            trigger_type="periodic",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "periodic",
                        "scheduleType": schedule_type,
                        "scheduledTime": scheduled_time,
                        "cronExpression": cron_expression,
                        "schedulePresetId": schedule_preset_id,
                        "scheduleTimezone": schedule_timezone,
                        "promptExtension": prompt_extension,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class EmailTriggerNode(TriggerNode):
    """Start a workflow when email arrives at a Metronome mailbox."""

    def __init__(
        self,
        id: str,
        *,
        local_part: str | None = None,
        address: str | None = None,
        from_contains: str | None = None,
        subject_contains: str | None = None,
        body_contains: str | None = None,
        prompt_extension: str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            trigger_type="email",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "email",
                        "emailLocalPart": local_part,
                        "emailAddress": address,
                        "fromContains": from_contains,
                        "subjectContains": subject_contains,
                        "bodyContains": body_contains,
                        "promptExtension": prompt_extension,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class TelegramTriggerNode(TriggerNode):
    """Start a workflow when a Telegram command is sent to the Computer Agents bot."""

    def __init__(
        self,
        id: str,
        *,
        command: str | None = None,
        from_username_contains: str | None = None,
        chat_id: str | None = None,
        message_contains: str | None = None,
        prompt_extension: str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            trigger_type="telegram",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "telegram",
                        "telegramCommand": command,
                        "telegramFromContains": from_username_contains,
                        "telegramChatId": chat_id,
                        "telegramMessageContains": message_contains,
                        "promptExtension": prompt_extension,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class GitHubTriggerNode(TriggerNode):
    """Start a workflow from matching GitHub webhook events."""

    def __init__(
        self,
        id: str,
        *,
        event_type: str | None = None,
        repository_contains: str | None = None,
        branch_contains: str | None = None,
        actor_contains: str | None = None,
        action_contains: str | None = None,
        payload_contains: str | None = None,
        prompt_extension: str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            trigger_type="github",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "github",
                        "githubEventType": event_type,
                        "githubRepositoryContains": repository_contains,
                        "githubBranchContains": branch_contains,
                        "githubActorContains": actor_contains,
                        "githubActionContains": action_contains,
                        "githubPayloadContains": payload_contains,
                        "promptExtension": prompt_extension,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class ProjectTicketTriggerNode(TriggerNode):
    """Start a workflow from matching project ticket status changes or comments."""

    def __init__(
        self,
        id: str,
        *,
        event_type: str | None = None,
        project_id: str | None = None,
        project_name: str | None = None,
        from_status: str | None = None,
        to_status: str | None = None,
        comment_contains: str | None = None,
        prompt_extension: str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            trigger_type="project_ticket",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "project_ticket",
                        "ticketEventType": event_type,
                        "ticketProjectId": project_id,
                        "ticketProjectName": project_name,
                        "ticketFromStatus": from_status,
                        "ticketToStatus": to_status,
                        "ticketCommentContains": comment_contains,
                        "promptExtension": prompt_extension,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class ResourceDeploymentTriggerNode(TriggerNode):
    """Start a workflow from successful function or web app deployments."""

    def __init__(
        self,
        id: str,
        *,
        event_type: str | None = None,
        resource_id: str | None = None,
        resource_name: str | None = None,
        resource_kind: str | None = None,
        prompt_extension: str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            trigger_type="resource",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "resource",
                        "resourceEventType": event_type,
                        "resourceId": resource_id,
                        "resourceName": resource_name,
                        "resourceKind": resource_kind,
                        "promptExtension": prompt_extension,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class DatabaseEntryTriggerNode(TriggerNode):
    """Start a workflow when a document is added to a database collection."""

    def __init__(
        self,
        id: str,
        *,
        database_id: str | None = None,
        database_name: str | None = None,
        collection: str | None = None,
        prompt_extension: str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            trigger_type="database_entry",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "database_entry",
                        "databaseEventType": "document_created",
                        "databaseId": database_id,
                        "databaseName": database_name,
                        "databaseCollection": collection,
                        "promptExtension": prompt_extension,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class AuthEventTriggerNode(TriggerNode):
    """Start a workflow when a user registers through an auth resource."""

    def __init__(
        self,
        id: str,
        *,
        auth_resource_id: str | None = None,
        auth_resource_name: str | None = None,
        email_contains: str | None = None,
        prompt_extension: str | None = None,
        label: str | None = "Trigger",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            trigger_type="auth",
            label=label,
            description=description,
            config=_merge_config(
                config,
                _drop_none(
                    {
                        "triggerType": "auth",
                        "authEventType": "user_registered",
                        "authResourceId": auth_resource_id,
                        "authResourceName": auth_resource_name,
                        "authEmailContains": email_contains,
                        "promptExtension": prompt_extension,
                        **extra_config,
                    }
                ),
            ),
            position=position,
        )


class ConditionNode(MetronomeNode):
    """Branch workflow execution based on one or more ordered conditions."""

    def __init__(
        self,
        id: str,
        *,
        conditions: Sequence[Mapping[str, Any]] | None = None,
        label: str | None = "Condition",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        merged = _merge_config(config, extra_config)
        if conditions is not None:
            merged["conditions"] = [dict(condition) for condition in conditions]
        super().__init__(
            id=id,
            kind="condition",
            subtype="if_else",
            label=label,
            description=description,
            config=merged,
            position=position,
        )


class ThreadNode(MetronomeNode):
    """Start a Computer Agents thread as a workflow action."""

    def __init__(
        self,
        id: str,
        *,
        message: str | None = None,
        agent_id: str | None = None,
        agent_name: str | None = None,
        computer_id: str | None = None,
        computer_name: str | None = None,
        project_id: str | None = None,
        project_name: str | None = None,
        input_context_scope: str | None = "all",
        input_binding: str | None = None,
        input_bindings: Mapping[str, Any] | Sequence[str] | None = None,
        output_mode: str | None = "text",
        output_key: str | None = "thread",
        require_json_output: bool | None = None,
        output_fields: Sequence[str] | str | None = None,
        output_contract: Mapping[str, Any] | str | None = None,
        attachments: Sequence[Mapping[str, Any]] | str | None = None,
        label: str | None = "Thread",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        parent_id: str | None = None,
        extent: str | None = None,
        style: dict[str, Any] | None = None,
        **extra_config: Any,
    ) -> None:
        context_type = "project" if project_id or project_name else "computer"
        attachments_json: str | None = None
        normalized_attachments: list[dict[str, Any]] | None = None
        if isinstance(attachments, str):
            attachments_json = attachments
        elif attachments is not None:
            normalized_attachments = [dict(item) for item in attachments]
        output_fields_json: str | None = None
        normalized_output_fields: list[str] | None = None
        if isinstance(output_fields, str):
            output_fields_json = output_fields
        elif output_fields is not None:
            normalized_output_fields = [str(item) for item in output_fields]
        merged = _merge_config(
            config,
            {
                "message": message,
                "agentId": agent_id,
                "agentName": agent_name,
                "environmentId": computer_id,
                "environmentName": computer_name,
                "projectId": project_id,
                "projectName": project_name,
                "inputContextScope": input_context_scope,
                "inputBinding": input_binding,
                "inputBindings": dict(input_bindings) if isinstance(input_bindings, Mapping) else list(input_bindings) if input_bindings is not None else None,
                "contextType": context_type,
                "resource": context_type,
                "outputMode": output_mode,
                "outputKey": output_key,
                "requireJsonOutput": require_json_output,
                "outputFieldsJson": output_fields_json,
                "outputFields": normalized_output_fields,
                "outputContractJson": output_contract if isinstance(output_contract, str) else None,
                "outputContract": dict(output_contract) if isinstance(output_contract, Mapping) else None,
                "attachmentsJson": attachments_json,
                "attachments": normalized_attachments,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="action",
            subtype="start_thread",
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
            parent_id=parent_id,
            extent=extent,
            style=style,
        )


class ImagineNode(MetronomeNode):
    """Start an Imagine thread from a workflow and store the generated asset result."""

    def __init__(
        self,
        id: str,
        operation: str = "start_imagine",
        *,
        template_id: str | None = None,
        template_name: str | None = None,
        prompt: str | None = None,
        attachments: Sequence[Mapping[str, Any]] | str | None = None,
        project_id: str | None = None,
        project_name: str | None = None,
        media_mode: str | None = "image",
        image_model_id: str | None = None,
        video_model_id: str | None = None,
        agent_id: str | None = None,
        agent_name: str | None = None,
        computer_id: str | None = None,
        computer_name: str | None = None,
        input_context_scope: str | None = "all",
        aspect_ratio: str | None = None,
        label: str | None = "Imagine",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        attachments_json: str | None = None
        normalized_attachments: list[dict[str, Any]] | None = None
        if isinstance(attachments, str):
            attachments_json = attachments
        elif attachments is not None:
            normalized_attachments = [dict(item) for item in attachments]
        merged = _merge_config(
            config,
            {
                "templateId": template_id,
                "templateName": template_name,
                "prompt": prompt,
                "attachmentsJson": attachments_json,
                "attachments": normalized_attachments,
                "projectId": project_id,
                "projectName": project_name,
                "mediaMode": media_mode,
                "imageModelId": image_model_id,
                "videoModelId": video_model_id,
                "agentId": agent_id,
                "agentName": agent_name,
                "environmentId": computer_id,
                "environmentName": computer_name,
                "inputContextScope": input_context_scope,
                "aspectRatio": aspect_ratio,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="imagine",
            subtype=operation,
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
        )


class FunctionNode(MetronomeNode):
    """Invoke a deployed Computer Agents function and store its output."""

    def __init__(
        self,
        id: str,
        *,
        function_id: str | None = None,
        function_name: str | None = None,
        payload: Mapping[str, Any] | str | None = None,
        label: str | None = "Function",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        merged = _merge_config(
            config,
            {
                "functionId": function_id,
                "functionName": function_name,
                "payloadJson": payload if isinstance(payload, str) else None,
                "payload": dict(payload) if isinstance(payload, Mapping) else None,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="function",
            subtype="invoke_function",
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
        )


class FirecrawlNode(MetronomeNode):
    """Search, scrape, parse, or extract structured web/document data with Firecrawl."""

    def __init__(
        self,
        id: str,
        operation: str = "web_search",
        *,
        credential_ref: str | None = "workspace:FIRECRAWL_API_KEY",
        credential_vault_id: str | None = None,
        credential_secret_id: str | None = None,
        input_binding: str | None = None,
        query: str | None = None,
        url: str | None = None,
        file_path: str | None = None,
        prompt: str | None = None,
        schema: Mapping[str, Any] | str | None = None,
        limit: int | None = 5,
        formats: Sequence[str] | str | None = None,
        save_artifacts: bool | None = True,
        output_key: str | None = "firecrawl",
        label: str | None = "Firecrawl",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        parent_id: str | None = None,
        extent: str | None = None,
        style: dict[str, Any] | None = None,
        **extra_config: Any,
    ) -> None:
        normalized_formats: str | None = None
        if isinstance(formats, str):
            normalized_formats = formats
        elif formats is not None:
            normalized_formats = ", ".join(str(item) for item in formats)
        merged = _merge_config(
            config,
            {
                "operation": operation,
                "credentialRef": credential_ref,
                "credentialVaultId": credential_vault_id,
                "credentialSecretId": credential_secret_id,
                "inputBinding": input_binding,
                "query": query,
                "url": url,
                "filePath": file_path,
                "prompt": prompt,
                "schemaJson": schema if isinstance(schema, str) else None,
                "schema": dict(schema) if isinstance(schema, Mapping) else None,
                "limit": limit,
                "formats": normalized_formats,
                "saveArtifacts": save_artifacts,
                "outputKey": output_key,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="firecrawl",
            subtype=operation,
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
            parent_id=parent_id,
            extent=extent,
            style=style,
        )


class TableNode(MetronomeNode):
    """Parse CSV or TSV inputs into records and optional batches."""

    def __init__(
        self,
        id: str,
        operation: str = "parse_csv",
        *,
        input_binding: str | None = "trigger.input.files",
        file_path: str | None = None,
        delimiter: str | None = None,
        has_header: bool | None = True,
        batch_size: int | None = 5,
        output_key: str | None = "table",
        content: str | None = None,
        label: str | None = "Table",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        parent_id: str | None = None,
        extent: str | None = None,
        style: dict[str, Any] | None = None,
        **extra_config: Any,
    ) -> None:
        merged = _merge_config(
            config,
            {
                "operation": operation,
                "inputBinding": input_binding,
                "filePath": file_path,
                "delimiter": delimiter,
                "hasHeader": has_header,
                "batchSize": batch_size,
                "outputKey": output_key,
                "content": content,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="table",
            subtype=operation,
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
            parent_id=parent_id,
            extent=extent,
            style=style,
        )


class DatabaseNode(MetronomeNode):
    """Insert, update, or delete a document in a Computer Agents database resource."""

    def __init__(
        self,
        id: str,
        operation: str = "insert_document",
        *,
        database_id: str | None = None,
        database_name: str | None = None,
        collection: str | None = None,
        document_id: str | None = None,
        document: Mapping[str, Any] | str | None = None,
        input_binding: str | None = None,
        records_binding: str | None = None,
        document_template: Mapping[str, Any] | str | None = None,
        upsert_key: str | None = None,
        label: str | None = "Database",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        parent_id: str | None = None,
        extent: str | None = None,
        style: dict[str, Any] | None = None,
        **extra_config: Any,
    ) -> None:
        merged = _merge_config(
            config,
            {
                "databaseId": database_id,
                "databaseName": database_name,
                "collection": collection,
                "documentId": document_id,
                "documentJson": document if isinstance(document, str) else None,
                "document": dict(document) if isinstance(document, Mapping) else None,
                "inputBinding": input_binding,
                "recordsBinding": records_binding,
                "documentTemplateJson": document_template if isinstance(document_template, str) else None,
                "documentTemplate": dict(document_template) if isinstance(document_template, Mapping) else None,
                "upsertKey": upsert_key,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="database",
            subtype=operation,
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
            parent_id=parent_id,
            extent=extent,
            style=style,
        )


class TicketNode(MetronomeNode):
    """Create, update, or comment on a Computer Agents project ticket."""

    def __init__(
        self,
        id: str,
        operation: str = "update_ticket_status",
        *,
        project_id: str | None = None,
        project_name: str | None = None,
        ticket_id: str | None = None,
        title: str | None = None,
        status: str | None = None,
        comment: str | None = None,
        assignee_id: str | None = None,
        assignee_name: str | None = None,
        agent_id: str | None = None,
        agent_name: str | None = None,
        computer_id: str | None = None,
        computer_name: str | None = None,
        instructions: str | None = None,
        subtask_title: str | None = None,
        subtask_description: str | None = None,
        fields: Mapping[str, Any] | str | None = None,
        label: str | None = "Ticket",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        merged = _merge_config(
            config,
            {
                "projectId": project_id,
                "projectName": project_name,
                "ticketId": ticket_id,
                "ticketTitle": title,
                "ticketStatus": status,
                "comment": comment,
                "assigneeId": assignee_id,
                "assigneeName": assignee_name,
                "agentId": agent_id,
                "agentName": agent_name,
                "environmentId": computer_id,
                "environmentName": computer_name,
                "instructions": instructions,
                "subtaskTitle": subtask_title,
                "subtaskDescription": subtask_description,
                "fieldsJson": fields if isinstance(fields, str) else None,
                "fields": dict(fields) if isinstance(fields, Mapping) else None,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="ticket",
            subtype=operation,
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
        )


class MetronomeRunNode(MetronomeNode):
    """Run another Metronome workflow from inside the current workflow."""

    def __init__(
        self,
        id: str,
        operation: str = "run_workflow",
        *,
        workflow_id: str | None = None,
        workflow_name: str | None = None,
        input: Mapping[str, Any] | str | None = None,
        label: str | None = "Metronome",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        merged = _merge_config(
            config,
            {
                "workflowId": workflow_id,
                "workflowName": workflow_name,
                "inputJson": input if isinstance(input, str) else None,
                "input": dict(input) if isinstance(input, Mapping) else None,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="metronome",
            subtype=operation,
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
        )


class LoopNode(MetronomeNode):
    """Repeat enclosed actions by count or until workflow/resource state changes."""

    def __init__(
        self,
        id: str,
        loop_type: str = "fixed_count",
        *,
        iterations: int | None = None,
        max_iterations: int | None = None,
        input_binding: str | None = None,
        context_contains: str | None = None,
        project_id: str | None = None,
        project_name: str | None = None,
        ticket_status: str | None = None,
        database_id: str | None = None,
        database_name: str | None = None,
        database_collection: str | None = None,
        database_field_path: str | None = None,
        database_operator: str | None = None,
        database_compare_value: str | None = None,
        database_limit: int | None = None,
        break_condition: str | None = None,
        label: str | None = "Loop",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        parent_id: str | None = None,
        extent: str | None = None,
        style: dict[str, Any] | None = None,
        **extra_config: Any,
    ) -> None:
        merged = _merge_config(
            config,
            {
                "loopType": loop_type,
                "iterations": iterations,
                "maxIterations": max_iterations,
                "inputBinding": input_binding,
                "contextContainsText": context_contains,
                "projectId": project_id,
                "projectName": project_name,
                "ticketStatusValue": ticket_status,
                "databaseId": database_id,
                "databaseName": database_name,
                "databaseCollection": database_collection,
                "databaseFieldPath": database_field_path,
                "databaseOperator": database_operator,
                "databaseCompareValue": database_compare_value,
                "databaseLimit": database_limit,
                "rule": break_condition,
                **extra_config,
            },
        )
        super().__init__(
            id=id,
            kind="loop",
            subtype=loop_type,
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
            parent_id=parent_id,
            extent=extent,
            style=style,
        )


class EndNode(MetronomeNode):
    """Finish a workflow."""

    def __init__(
        self,
        id: str,
        *,
        label: str | None = "End",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        parent_id: str | None = None,
        extent: str | None = None,
        style: dict[str, Any] | None = None,
        **extra_config: Any,
    ) -> None:
        super().__init__(
            id=id,
            kind="end",
            subtype="end",
            label=label,
            description=description,
            config=_merge_config(config, extra_config),
            position=position,
            parent_id=parent_id,
            extent=extent,
            style=style,
        )


class NoteNode(MetronomeNode):
    """Add documentation or implementation notes to a workflow graph."""

    def __init__(
        self,
        id: str,
        *,
        text: str | None = None,
        label: str | None = "Note",
        description: str | None = None,
        config: Mapping[str, Any] | None = None,
        position: dict[str, float] | None = None,
        **extra_config: Any,
    ) -> None:
        merged = _merge_config(config, {"message": text, **extra_config})
        super().__init__(
            id=id,
            kind="note",
            subtype="note",
            label=label,
            description=description,
            config=_drop_none(merged),
            position=position,
        )


@dataclass
class MetronomeEdge:
    """A connection between two Metronome nodes."""

    id: str
    source: str
    target: str
    source_handle: str | None = None
    target_handle: str | None = None
    label: str | None = None
    config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "source": self.source,
                "target": self.target,
                "sourceHandle": self.source_handle,
                "targetHandle": self.target_handle,
                "label": self.label,
                "config": dict(self.config or {}) or None,
            }
        )


@dataclass
class MetronomeWorkflow:
    """A complete Metronome workflow definition."""

    name: str
    nodes: Sequence[MetronomeNode | Mapping[str, Any]] = field(default_factory=list)
    edges: Sequence[MetronomeEdge | Mapping[str, Any]] = field(default_factory=list)
    version: int = 1
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = _drop_none(
            {
                "version": self.version,
                "name": self.name,
                "description": self.description,
                "metadata": dict(self.metadata or {}) or None,
                "nodes": [
                    node.to_dict() if hasattr(node, "to_dict") else dict(node)
                    for node in self.nodes
                ],
                "edges": [
                    edge.to_dict() if hasattr(edge, "to_dict") else dict(edge)
                    for edge in self.edges
                ],
            }
        )
        return payload


def _normalize_metronome_version(value: Any, index: int) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    version_id = str(value.get("id") or value.get("versionId") or value.get("version_id") or "").strip()
    if not version_id:
        return None
    definition = value.get("definition") if isinstance(value.get("definition"), Mapping) else None
    definition_dict = dict(definition) if definition is not None else None
    nodes = value.get("nodes")
    edges = value.get("edges")
    if not isinstance(nodes, Sequence) or isinstance(nodes, (str, bytes)):
        nodes = definition_dict.get("nodes") if definition_dict else []
    if not isinstance(edges, Sequence) or isinstance(edges, (str, bytes)):
        edges = definition_dict.get("edges") if definition_dict else []
    node_count = int(value.get("nodeCount") or value.get("node_count") or len(nodes or []))
    edge_count = int(value.get("edgeCount") or value.get("edge_count") or len(edges or []))
    raw_version_number = value.get("version")
    if raw_version_number is None:
        raw_version_number = value.get("versionNumber")
    if raw_version_number is None:
        raw_version_number = value.get("version_number")
    version_number = normalize_version_number(raw_version_number, index)
    version_label = format_version_label(version_number)
    return {
        "id": version_id,
        "version": version_number,
        "versionNumber": version_number,
        "label": version_label,
        "name": version_label,
        "description": value.get("description"),
        "status": str(value.get("status") or "saved"),
        "createdAt": value.get("createdAt") or value.get("created_at"),
        "updatedAt": value.get("updatedAt") or value.get("updated_at"),
        "publishedAt": value.get("publishedAt") or value.get("published_at"),
        "triggerSummary": value.get("triggerSummary") or value.get("trigger_summary"),
        "nodeCount": node_count,
        "edgeCount": edge_count,
        "definition": definition_dict,
        "nodes": list(nodes or []),
        "edges": list(edges or []),
    }


def _versions_from_workflow(workflow: Mapping[str, Any]) -> list[dict[str, Any]]:
    metadata_value = workflow.get("metadata")
    metadata: Mapping[str, Any] = (
        metadata_value if isinstance(metadata_value, Mapping) else {}
    )
    definition_value = workflow.get("definition")
    definition: Mapping[str, Any] = (
        definition_value if isinstance(definition_value, Mapping) else {}
    )
    raw_versions = (
        metadata.get("deployments")
        or metadata.get("metronomeDeployments")
        or definition.get("deployments")
        or definition.get("versions")
        or []
    )
    if not isinstance(raw_versions, Sequence) or isinstance(raw_versions, (str, bytes)):
        raw_versions = []
    versions = [
        normalized
        for index, version in enumerate(raw_versions)
        if (normalized := _normalize_metronome_version(version, index)) is not None
    ]
    return sorted(versions, key=lambda item: int(item.get("version") or 0), reverse=True)


def _create_version_id() -> str:
    return f"mdep_{uuid4().hex[:14]}"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class MetronomesResource:
    """Create, publish, run, and inspect agentic workflow automations."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @staticmethod
    def _unwrap(response: Any, *keys: str) -> Any:
        if not isinstance(response, dict):
            return response
        for key in keys:
            if key in response:
                return response[key]
        return response

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        status: str | None = None,
        include_archived: bool | None = None,
    ) -> list[dict[str, Any]]:
        """List Metronome workflows."""
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        if status is not None:
            query["status"] = status
        if include_archived is not None:
            query["includeArchived"] = include_archived
        response = self._client.get("/metronomes", query=query or None)
        return self._unwrap(response, "metronomes", "workflows", "data")

    def get(self, metronome_id: str) -> dict[str, Any]:
        """Fetch one Metronome workflow."""
        response = self._client.get(f"/metronomes/{metronome_id}")
        return self._unwrap(response, "metronome", "workflow", "data")

    def list_owner_candidates(self, metronome_id: str) -> list[dict[str, Any]]:
        response = self._client.get(f"/metronomes/{metronome_id}/owner-candidates")
        return response.get("data", response.get("candidates", []))

    def transfer_ownership(
        self,
        metronome_id: str,
        owner_user_id: str,
    ) -> dict[str, Any]:
        response = self._client.patch(
            f"/metronomes/{metronome_id}/owner",
            {"ownerUserId": owner_user_id},
        )
        return self._unwrap(response, "metronome", "workflow", "data")

    def list_versions(self, metronome_id: str) -> list[dict[str, Any]]:
        """List saved workflow versions."""
        response = self._client.get(f"/metronomes/{metronome_id}/versions")
        return self._unwrap(response, "versions", "data")

    def get_node_schemas(self) -> dict[str, Any]:
        """Return supported Metronome node kinds, trigger types, and action schemas."""
        response = self._client.get("/metronomes/node-schemas")
        return self._unwrap(response, "schema", "data")

    def validate_definition(
        self,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        *,
        mode: str = "publish",
        nodes: list[dict[str, Any]] | None = None,
        edges: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Validate a workflow definition without saving it."""
        body: dict[str, Any] = {"mode": mode}
        definition_dict = _definition_to_dict(definition)
        if definition_dict is not None:
            body["definition"] = definition_dict
        if nodes is not None:
            body["nodes"] = nodes
        if edges is not None:
            body["edges"] = edges
        response = self._client.post(
            "/metronomes/validate",
            body,
        )
        return self._unwrap(response, "validation", "data")

    def validate(
        self,
        metronome_id: str,
        *,
        mode: str = "publish",
        version_id: str | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        nodes: list[dict[str, Any]] | None = None,
        edges: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Validate a saved workflow, a saved version, or an inline definition."""
        body: dict[str, Any] = {"mode": mode}
        if version_id is not None:
            body["versionId"] = version_id
        if nodes is not None:
            body["nodes"] = nodes
        if edges is not None:
            body["edges"] = edges
        definition_dict = _definition_to_dict(definition)
        if definition_dict is not None:
            body["definition"] = definition_dict
        response = self._client.post(f"/metronomes/{metronome_id}/validate", body)
        return self._unwrap(response, "validation", "data")

    def create_version(
        self,
        metronome_id: str,
        *,
        label: str | None = None,
        name: str | None = None,
        description: str | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
    ) -> dict[str, Any]:
        """Save the next zero-based workflow version without publishing it.

        ``label`` and ``name`` are retained for compatibility but ignored by
        current APIs, which assign canonical ``vN`` labels.
        """
        body: dict[str, Any] = {}
        if label is not None:
            body["label"] = label
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        definition_dict = _definition_to_dict(definition)
        if definition_dict is not None:
            body["definition"] = definition_dict
        response = self._client.post(f"/metronomes/{metronome_id}/versions", body)
        return self._unwrap(response, "version", "data")

    def update_version(
        self,
        metronome_id: str,
        version_id: str,
        *,
        label: str | None = None,
        name: str | None = None,
        description: str | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
    ) -> dict[str, Any]:
        """Update a saved workflow version.

        ``label`` and ``name`` are retained for compatibility but version
        labels are immutable and generated by the API.

        Published versions are immutable. Create a new version or unpublish the
        workflow before editing the version that production triggers use.
        """
        body: dict[str, Any] = {}
        if label is not None:
            body["label"] = label
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        definition_dict = _definition_to_dict(definition)
        if definition_dict is not None:
            body["definition"] = definition_dict
        response = self._client.patch(f"/metronomes/{metronome_id}/versions/{version_id}", body)
        return self._unwrap(response, "version", "data")

    def delete_version(self, metronome_id: str, version_id: str) -> bool:
        """Archive a saved workflow version."""
        response = self._client.delete(f"/metronomes/{metronome_id}/versions/{version_id}")
        return bool(response.get("success") or response.get("deleted"))

    def publish_version(
        self,
        metronome_id: str,
        version_id: str,
        *,
        description: str | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        snapshot: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Publish a workflow version, optionally updating it in the same request."""
        body: dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        definition_dict = _definition_to_dict(definition)
        if definition_dict is not None:
            body["definition"] = definition_dict
        if snapshot is not None:
            serialized_snapshot = dict(snapshot)
            snapshot_definition = _definition_to_dict(serialized_snapshot.get("definition"))
            if snapshot_definition is not None:
                serialized_snapshot["definition"] = snapshot_definition
            body["snapshot"] = serialized_snapshot
        response = self._client.post(
            f"/metronomes/{metronome_id}/versions/{version_id}/publish",
            body,
        )
        return self._unwrap(response, "metronome", "workflow", "data")

    def diff_versions(self, metronome_id: str, version_id: str, *, against_version_id: str) -> dict[str, Any]:
        """Compare one saved workflow version against another version."""
        response = self._client.get(
            f"/metronomes/{metronome_id}/versions/{version_id}/diff",
            query={"againstVersionId": against_version_id},
        )
        return self._unwrap(response, "diff", "data")

    def unpublish(self, metronome_id: str) -> dict[str, Any]:
        """Unpublish a workflow while keeping saved versions."""
        response = self._client.post(f"/metronomes/{metronome_id}/unpublish", {})
        return self._unwrap(response, "metronome", "workflow", "data")

    def list_deployments(
        self,
        metronome_id: str,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """List publish and unpublish deployment history for a workflow."""
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        response = self._client.get(f"/metronomes/{metronome_id}/deployments", query=query or None)
        return self._unwrap(response, "deployments", "data")

    def create(
        self,
        *,
        name: str,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        description: str | None = None,
        status: str = "draft",
        trigger_summary: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Create a Metronome workflow."""
        body: dict[str, Any] = {"name": name, "status": status}
        serialized_definition = _definition_to_dict(definition)
        if serialized_definition is not None:
            body["definition"] = serialized_definition
        if description is not None:
            body["description"] = description
        if trigger_summary is not None:
            body["triggerSummary"] = trigger_summary
        body.update(params)
        response = self._client.post("/metronomes", body)
        return self._unwrap(response, "metronome", "workflow", "data")

    def update(self, metronome_id: str, **params: Any) -> dict[str, Any]:
        """Update a Metronome workflow."""
        if "trigger_summary" in params:
            params["triggerSummary"] = params.pop("trigger_summary")
        if "definition" in params:
            serialized_definition = _definition_to_dict(params.get("definition"))
            if serialized_definition is None:
                params.pop("definition", None)
            else:
                params["definition"] = serialized_definition
        response = self._client.patch(f"/metronomes/{metronome_id}", params)
        return self._unwrap(response, "metronome", "workflow", "data")

    def upsert(
        self,
        *,
        name: str,
        metronome_id: str | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        description: str | None = None,
        status: str = "draft",
        trigger_summary: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Create a workflow or update an existing workflow when an ID is supplied."""
        if metronome_id:
            update_params: dict[str, Any] = {"name": name, "status": status}
            serialized_definition = _definition_to_dict(definition)
            if serialized_definition is not None:
                update_params["definition"] = serialized_definition
            if description is not None:
                update_params["description"] = description
            if trigger_summary is not None:
                update_params["triggerSummary"] = trigger_summary
            update_params.update(params)
            return self.update(metronome_id, **update_params)
        return self.create(
            name=name,
            definition=definition,
            description=description,
            status=status,
            trigger_summary=trigger_summary,
            **params,
        )

    def delete(self, metronome_id: str) -> bool:
        """Delete a Metronome workflow."""
        response = self._client.delete(f"/metronomes/{metronome_id}")
        if isinstance(response, dict):
            return bool(response.get("success") or response.get("deleted") or response.get("ok"))
        return True

    def publish(
        self,
        metronome_id: str,
        *,
        active: bool = True,
        version_id: str | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Publish or unpublish a Metronome workflow."""
        body: dict[str, Any] = {"active": active}
        if version_id is not None:
            body["versionId"] = version_id
        definition_dict = _definition_to_dict(definition)
        if definition_dict is not None:
            body["definition"] = definition_dict
        if description is not None:
            body["description"] = description
        response = self._client.post(f"/metronomes/{metronome_id}/publish", body)
        return self._unwrap(response, "metronome", "workflow", "data")

    def run(
        self,
        metronome_id: str,
        *,
        input: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        version_id: str | None = None,
        trigger_type: str | None = None,
        idempotency_key: str | None = None,
        max_attempts: int | None = None,
        timeout_ms: int | None = None,
        attached_project_id: str | None = None,
        attached_ticket_id: str | None = None,
        queue_when_capacity_unavailable: bool | None = None,
        pinned_agent_versions: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run a published workflow manually."""
        body: dict[str, Any] = {}
        if input is not None:
            body["input"] = input
        if inputs is not None:
            body["inputs"] = inputs
        serialized_definition = _definition_to_dict(definition)
        if serialized_definition is not None:
            body["definition"] = serialized_definition
        if version_id is not None:
            body["versionId"] = version_id
        if trigger_type is not None:
            body["triggerType"] = trigger_type
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        if max_attempts is not None:
            body["maxAttempts"] = max_attempts
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms
        if attached_project_id is not None:
            body["attachedProjectId"] = attached_project_id
        if attached_ticket_id is not None:
            body["attachedTicketId"] = attached_ticket_id
        if queue_when_capacity_unavailable is not None:
            body["queueWhenCapacityUnavailable"] = queue_when_capacity_unavailable
        if pinned_agent_versions is not None:
            body["pinnedAgentVersions"] = dict(pinned_agent_versions)
        response = self._client.post(f"/metronomes/{metronome_id}/runs", body)
        run = self._unwrap(response, "run", "data")
        if isinstance(response, dict) and response.get("queuedInBatch") is True:
            batch_job = response.get("batchJob")
            if isinstance(run, dict):
                run = {
                    **run,
                    "queuedInBatch": True,
                    "batchJobId": batch_job.get("id") if isinstance(batch_job, dict) else None,
                    "batchJob": batch_job,
                }
        return run

    def test_run(
        self,
        metronome_id: str,
        *,
        input: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        version_id: str | None = None,
        trigger_type: str | None = None,
        idempotency_key: str | None = None,
        max_attempts: int | None = None,
        timeout_ms: int | None = None,
        attached_project_id: str | None = None,
        attached_ticket_id: str | None = None,
        queue_when_capacity_unavailable: bool | None = None,
        pinned_agent_versions: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run a workflow draft with optional inline definition overrides."""
        body: dict[str, Any] = {}
        if input is not None:
            body["input"] = input
        if inputs is not None:
            body["inputs"] = inputs
        serialized_definition = _definition_to_dict(definition)
        if serialized_definition is not None:
            body["definition"] = serialized_definition
        if version_id is not None:
            body["versionId"] = version_id
        if trigger_type:
            body["triggerType"] = trigger_type
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        if max_attempts is not None:
            body["maxAttempts"] = max_attempts
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms
        if attached_project_id is not None:
            body["attachedProjectId"] = attached_project_id
        if attached_ticket_id is not None:
            body["attachedTicketId"] = attached_ticket_id
        if queue_when_capacity_unavailable is not None:
            body["queueWhenCapacityUnavailable"] = queue_when_capacity_unavailable
        if pinned_agent_versions is not None:
            body["pinnedAgentVersions"] = dict(pinned_agent_versions)
        response = self._client.post(f"/metronomes/{metronome_id}/test-run", body)
        return self._unwrap(response, "run", "data")

    def preview_test_run(
        self,
        metronome_id: str,
        *,
        selection: Mapping[str, Any],
        fixture: Any = None,
        input: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        version_id: str | None = None,
        trigger_type: str | None = None,
        idempotency_key: str | None = None,
        max_attempts: int | None = None,
        timeout_ms: int | None = None,
        attached_project_id: str | None = None,
        attached_ticket_id: str | None = None,
        queue_when_capacity_unavailable: bool | None = None,
        pinned_agent_versions: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Preview an isolated node or connected workflow-slice test."""
        body = self._isolated_test_run_body(
            selection=selection,
            fixture=fixture,
            input=input,
            inputs=inputs,
            definition=definition,
            version_id=version_id,
            trigger_type=trigger_type,
            idempotency_key=idempotency_key,
            max_attempts=max_attempts,
            timeout_ms=timeout_ms,
            attached_project_id=attached_project_id,
            attached_ticket_id=attached_ticket_id,
            queue_when_capacity_unavailable=queue_when_capacity_unavailable,
            pinned_agent_versions=pinned_agent_versions,
        )
        response = self._client.post(f"/metronomes/{metronome_id}/test-runs/preview", body)
        return self._unwrap(response, "data")

    def run_test(
        self,
        metronome_id: str,
        *,
        selection: Mapping[str, Any],
        fixture: Any = None,
        input: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        version_id: str | None = None,
        trigger_type: str | None = None,
        idempotency_key: str | None = None,
        max_attempts: int | None = None,
        timeout_ms: int | None = None,
        attached_project_id: str | None = None,
        attached_ticket_id: str | None = None,
        queue_when_capacity_unavailable: bool | None = None,
        pinned_agent_versions: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Queue an isolated node or connected workflow-slice test."""
        body = self._isolated_test_run_body(
            selection=selection,
            fixture=fixture,
            input=input,
            inputs=inputs,
            definition=definition,
            version_id=version_id,
            trigger_type=trigger_type,
            idempotency_key=idempotency_key,
            max_attempts=max_attempts,
            timeout_ms=timeout_ms,
            attached_project_id=attached_project_id,
            attached_ticket_id=attached_ticket_id,
            queue_when_capacity_unavailable=queue_when_capacity_unavailable,
            pinned_agent_versions=pinned_agent_versions,
        )
        response = self._client.post(f"/metronomes/{metronome_id}/test-runs", body)
        return self._unwrap(response, "run", "data")

    @staticmethod
    def _isolated_test_run_body(
        *,
        selection: Mapping[str, Any],
        fixture: Any,
        input: dict[str, Any] | None,
        inputs: dict[str, Any] | None,
        definition: Mapping[str, Any] | SupportsToDict | None,
        version_id: str | None,
        trigger_type: str | None,
        idempotency_key: str | None,
        max_attempts: int | None,
        timeout_ms: int | None,
        attached_project_id: str | None,
        attached_ticket_id: str | None,
        queue_when_capacity_unavailable: bool | None,
        pinned_agent_versions: Mapping[str, str] | None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"selection": dict(selection)}
        optional_values: dict[str, Any] = {
            "fixture": fixture,
            "input": input,
            "inputs": inputs,
            "versionId": version_id,
            "triggerType": trigger_type,
            "idempotencyKey": idempotency_key,
            "maxAttempts": max_attempts,
            "timeoutMs": timeout_ms,
            "attachedProjectId": attached_project_id,
            "attachedTicketId": attached_ticket_id,
            "queueWhenCapacityUnavailable": queue_when_capacity_unavailable,
            "pinnedAgentVersions": dict(pinned_agent_versions) if pinned_agent_versions is not None else None,
        }
        for key, value in optional_values.items():
            if value is not None:
                body[key] = value
        serialized_definition = _definition_to_dict(definition)
        if serialized_definition is not None:
            body["definition"] = serialized_definition
        return body

    def list_runs(
        self,
        metronome_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        status: str | None = None,
        search: str | None = None,
        project_id: str | None = None,
        ticket_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List runs for a Metronome workflow."""
        query: dict[str, Any] = {}
        page_offset = max(0, offset or 0)
        requested_limit = max(0, limit) if limit is not None else 50
        query["limit"] = min(100, page_offset + requested_limit)
        if status:
            query["status"] = status
        if search:
            query["q"] = search
        if project_id:
            query["projectId"] = project_id
        if ticket_id:
            query["ticketId"] = ticket_id
        response = self._client.get(f"/metronomes/{metronome_id}/runs", query=query or None)
        runs = self._unwrap(response, "runs", "data")
        if not isinstance(runs, list):
            return runs
        return runs[page_offset:page_offset + requested_limit]

    def get_run(
        self,
        metronome_id: str,
        run_id: str,
        *,
        view: str | None = None,
    ) -> dict[str, Any]:
        """Fetch one workflow run."""
        response = self._client.get(
            f"/metronomes/{metronome_id}/runs/{run_id}",
            query={"view": view},
        )
        return self._unwrap(response, "run", "data")

    def get_run_result(self, metronome_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get(
            f"/metronomes/{metronome_id}/runs/{run_id}/result"
        )

    def update_run(
        self,
        metronome_id: str,
        run_id: str,
        *,
        attached_project_id: str | None = None,
        attached_ticket_id: str | None = None,
    ) -> dict[str, Any]:
        """Attach a workflow run to a project or ticket for filtering and review."""
        body: dict[str, Any] = {}
        if attached_project_id is not None:
            body["attachedProjectId"] = attached_project_id
        if attached_ticket_id is not None:
            body["attachedTicketId"] = attached_ticket_id
        response = self._client.patch(f"/metronomes/{metronome_id}/runs/{run_id}", body)
        return self._unwrap(response, "run", "data")

    def get_run_timeline(
        self,
        metronome_id: str,
        run_id: str,
        *,
        view: str | None = None,
    ) -> dict[str, Any]:
        """Fetch a run with trigger diagnostic, node steps, and audit events."""
        response = self._client.get(
            f"/metronomes/{metronome_id}/runs/{run_id}/timeline",
            query={"view": view},
        )
        return self._unwrap(response, "timeline", "data")

    def cancel_run(self, metronome_id: str, run_id: str) -> dict[str, Any]:
        """Cancel a queued or running workflow run."""
        response = self._client.post(f"/metronomes/{metronome_id}/runs/{run_id}/cancel", {})
        return self._unwrap(response, "run", "data")

    def pause_run(self, metronome_id: str, run_id: str) -> dict[str, Any]:
        """Pause a queued or running workflow run."""
        response = self._client.post(f"/metronomes/{metronome_id}/runs/{run_id}/pause", {})
        return self._unwrap(response, "run", "data")

    def resume_run(
        self,
        metronome_id: str,
        run_id: str,
        *,
        confirm_in_doubt_replay: bool | None = None,
    ) -> dict[str, Any]:
        """Resume a paused workflow run."""
        body = (
            {"confirmInDoubtReplay": confirm_in_doubt_replay}
            if confirm_in_doubt_replay is not None
            else {}
        )
        response = self._client.post(f"/metronomes/{metronome_id}/runs/{run_id}/resume", body)
        return self._unwrap(response, "run", "data")

    def retry_run(self, metronome_id: str, run_id: str) -> dict[str, Any]:
        """Retry a failed or cancelled workflow run using its original input and version."""
        response = self._client.post(f"/metronomes/{metronome_id}/runs/{run_id}/retry", {})
        return self._unwrap(response, "run", "data")

    def delete_run(self, metronome_id: str, run_id: str) -> bool:
        """Delete a workflow run record."""
        response = self._client.delete(f"/metronomes/{metronome_id}/runs/{run_id}")
        if isinstance(response, dict):
            return bool(response.get("deleted") or response.get("success") or response.get("ok"))
        return True

    def list_run_steps(self, metronome_id: str, run_id: str) -> list[dict[str, Any]]:
        """List structured node-level trace steps for a workflow run."""
        response = self._client.get(f"/metronomes/{metronome_id}/runs/{run_id}/steps")
        return self._unwrap(response, "steps", "data")

    def list_audit_events(
        self,
        *,
        limit: int | None = None,
        metronome_id: str | None = None,
        action: str | None = None,
    ) -> list[dict[str, Any]]:
        """List Metronome audit events across workflows for the account."""
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if metronome_id:
            query["metronomeId"] = metronome_id
        if action:
            query["action"] = action
        response = self._client.get("/metronomes/audit-events", query=query or None)
        return self._unwrap(response, "audit_events", "events", "data")

    def test_trigger(
        self,
        metronome_id: str,
        *,
        trigger_type: str = "manual_test",
        payload: dict[str, Any] | None = None,
        source_event_id: str | None = None,
        summary: str | None = None,
        definition: Mapping[str, Any] | SupportsToDict | None = None,
        idempotency_key: str | None = None,
        max_attempts: int | None = None,
        timeout_ms: int | None = None,
        attached_project_id: str | None = None,
        attached_ticket_id: str | None = None,
    ) -> dict[str, Any]:
        """Submit a sample trigger payload, record diagnostics, and start a run."""
        body: dict[str, Any] = {
            "triggerType": trigger_type,
            "payload": payload or {},
        }
        if source_event_id is not None:
            body["sourceEventId"] = source_event_id
        if summary is not None:
            body["summary"] = summary
        serialized_definition = _definition_to_dict(definition)
        if serialized_definition is not None:
            body["definition"] = serialized_definition
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        if max_attempts is not None:
            body["maxAttempts"] = max_attempts
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms
        if attached_project_id is not None:
            body["attachedProjectId"] = attached_project_id
        if attached_ticket_id is not None:
            body["attachedTicketId"] = attached_ticket_id
        response = self._client.post(f"/metronomes/{metronome_id}/triggers/test", body)
        return self._unwrap(response, "trigger_test", "data")

    def invoke_function_trigger(
        self,
        metronome_id: str,
        slug: str,
        *,
        payload: dict[str, Any] | None = None,
        source_event_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "payload": payload or {},
                "sourceEventId": source_event_id,
                "idempotencyKey": idempotency_key,
            }.items()
            if value is not None
        }
        response = self._client.post(
            f"/metronomes/{metronome_id}/triggers/function/{slug}",
            body,
        )
        return self._unwrap(response, "data")

    def list_all_trigger_events(
        self,
        *,
        limit: int | None = None,
        status: str | None = None,
        trigger_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """List trigger diagnostics across all Metronome workflows for the account."""
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if status:
            query["status"] = status
        if trigger_type:
            query["triggerType"] = trigger_type
        response = self._client.get("/metronomes/trigger-events", query=query or None)
        return self._unwrap(response, "trigger_events", "events", "data")

    def list_trigger_events(
        self,
        metronome_id: str,
        *,
        limit: int | None = None,
        status: str | None = None,
        trigger_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """List trigger diagnostics for a Metronome workflow."""
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if status:
            query["status"] = status
        if trigger_type:
            query["triggerType"] = trigger_type
        response = self._client.get(f"/metronomes/{metronome_id}/trigger-events", query=query or None)
        return self._unwrap(response, "trigger_events", "events", "data")

    def list_trigger_summaries(
        self,
        metronome_id: str,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """List grouped trigger diagnostics for a Metronome workflow."""
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        response = self._client.get(f"/metronomes/{metronome_id}/trigger-summary", query=query or None)
        return self._unwrap(response, "trigger_summaries", "summaries", "data")
