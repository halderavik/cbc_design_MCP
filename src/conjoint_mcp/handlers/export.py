from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from conjoint_mcp.constraints.models import ConstraintSpec
from conjoint_mcp.models.requests import DesignGrid, GenerateDesignRequest
from conjoint_mcp.models.responses import GenerateDesignResponse
from conjoint_mcp.utils.export import (
    create_design_summary,
    export_design_to_csv,
    export_design_to_json,
    export_design_to_qualtrics_format,
)


class ExportRequest(BaseModel):
    """
    Request for exporting a design.
    
    Args:
        design_request (GenerateDesignRequest): Original design generation request.
        format (str): Export format ('csv', 'json', 'qualtrics').
        include_metadata (bool): Whether to include metadata.
        constraints (Optional[ConstraintSpec]): Constraint specification.
    """
    
    design_request: GenerateDesignRequest
    format: str = Field(default="csv", description="Export format")
    include_metadata: bool = Field(default=True, description="Include metadata")
    constraints: Optional[ConstraintSpec] = Field(default=None, description="Constraint specification")


class ExportResponse(BaseModel):
    """
    Response containing exported design data.
    
    Args:
        content (str): Exported content.
        format (str): Export format used.
    summary (Dict[str, Any]): Design summary.
    validation_results (Optional[Dict[str, Any]]): Constraint validation results.
    """
    
    content: str
    format: str
    summary: Dict[str, Any]
    validation_results: Optional[Dict[str, Any]] = None


def handle_export_design(req: ExportRequest) -> ExportResponse:
    """
    Handle design export request.
    
    Args:
        req (ExportRequest): Export request.
        
    Returns:
        ExportResponse: Export response with content and metadata.
    """
    # Generate the design first
    from conjoint_mcp.handlers.generation import handle_generate_design
    
    design_response = handle_generate_design(req.design_request)
    
    # Export based on format
    if req.format.lower() == "csv":
        content = export_design_to_csv(design_response, req.include_metadata)
    elif req.format.lower() == "json":
        content = export_design_to_json(design_response)
    elif req.format.lower() == "qualtrics":
        content = export_design_to_qualtrics_format(design_response)
    else:
        raise ValueError(f"Unsupported export format: {req.format}")
    
    # Create summary
    summary = create_design_summary(design_response)
    
    # Validate against constraints if provided
    validation_results = None
    if req.constraints:
        from conjoint_mcp.constraints.manager import ConstraintManager
        
        constraint_manager = ConstraintManager(req.constraints)
        is_valid, violations = constraint_manager.validate_design(
            [{"task_index": task.task_index, "options": task.options} for task in design_response.tasks]
        )
        
        validation_results = {
            "is_valid": is_valid,
            "violations": violations,
            "constraint_summary": constraint_manager.get_constraint_summary(),
        }
    
    return ExportResponse(
        content=content,
        format=req.format,
        summary=summary,
        validation_results=validation_results,
    )
