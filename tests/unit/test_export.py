from conjoint_mcp.models.responses import GenerateDesignResponse, GeneratedChoiceTask
from conjoint_mcp.utils.export import (
    create_design_summary,
    export_design_to_csv,
    export_design_to_json,
    export_design_to_qualtrics_format,
)


def test_export_design_to_csv():
    tasks = [
        GeneratedChoiceTask(
            task_index=1,
            options=[{"Color": "Red", "Size": "S"}, {"Color": "Blue", "Size": "L"}]
        ),
        GeneratedChoiceTask(
            task_index=2,
            options=[{"Color": "Blue", "Size": "S"}, {"Color": "Red", "Size": "L"}]
        ),
    ]
    
    response = GenerateDesignResponse(tasks=tasks, efficiency=0.8)
    csv_content = export_design_to_csv(response, include_metadata=True)
    
    assert "CBC Design Export" in csv_content
    assert "Efficiency Score: 0.8" in csv_content
    assert "Task_Index,Option_Index,Color,Size" in csv_content
    assert "1,1,Red,S" in csv_content


def test_export_design_to_json():
    tasks = [
        GeneratedChoiceTask(
            task_index=1,
            options=[{"Color": "Red", "Size": "S"}]
        ),
    ]
    
    response = GenerateDesignResponse(tasks=tasks, efficiency=0.8)
    json_content = export_design_to_json(response)
    
    assert "metadata" in json_content
    assert "efficiency" in json_content
    assert "tasks" in json_content
    assert "Red" in json_content


def test_export_design_to_qualtrics_format():
    tasks = [
        GeneratedChoiceTask(
            task_index=1,
            options=[{"Color": "Red", "Size": "S"}]
        ),
    ]
    
    response = GenerateDesignResponse(tasks=tasks, efficiency=0.8)
    qualtrics_content = export_design_to_qualtrics_format(response)
    
    assert "Task,Option,Attribute,Level" in qualtrics_content
    assert "1,1,Color,Red" in qualtrics_content
    assert "1,1,Size,S" in qualtrics_content


def test_create_design_summary():
    tasks = [
        GeneratedChoiceTask(
            task_index=1,
            options=[{"Color": "Red", "Size": "S"}, {"Color": "Blue", "Size": "L"}]
        ),
        GeneratedChoiceTask(
            task_index=2,
            options=[{"Color": "Blue", "Size": "S"}]
        ),
    ]
    
    response = GenerateDesignResponse(tasks=tasks, efficiency=0.8)
    summary = create_design_summary(response)
    
    assert summary["total_tasks"] == 2
    assert summary["total_options"] == 3
    assert summary["average_options_per_task"] == 1.5
    assert "Color" in summary["attributes"]
    assert "Size" in summary["attributes"]
    assert summary["efficiency_score"] == 0.8
