# /// script
# dependencies = []
#
# [tool.griptape-nodes]
# name = "image_flow"
# schema_version = "0.14.0"
# engine_version_created_with = "0.65.3"
# node_libraries_referenced = [["Griptape Nodes Library", "0.52.3"]]
# node_types_used = [["Griptape Nodes Library", "Agent"], ["Griptape Nodes Library", "EndFlow"], ["Griptape Nodes Library", "MergeTexts"], ["Griptape Nodes Library", "SeedreamImageGeneration"], ["Griptape Nodes Library", "StartFlow"]]
# is_griptape_provided = false
# is_template = false
# creation_date = 2025-12-11T00:49:56.685368Z
# last_modified_date = 2025-12-11T01:52:36.454122Z
# workflow_shape = "{\"inputs\":{\"Start Flow\":{\"exec_out\":{\"name\":\"exec_out\",\"tooltip\":\"Connection to the next node in the execution chain\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Flow Out\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"subject\":{\"name\":\"subject\",\"tooltip\":\"Enter text/string for subject.\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null}}},\"outputs\":{\"End Flow\":{\"exec_in\":{\"name\":\"exec_in\",\"tooltip\":\"Control path when the flow completed successfully\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Succeeded\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"failed\":{\"name\":\"failed\",\"tooltip\":\"Control path when the flow failed\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Failed\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"was_successful\":{\"name\":\"was_successful\",\"tooltip\":\"Indicates whether it completed without errors.\",\"type\":\"bool\",\"input_types\":[\"bool\"],\"output_type\":\"bool\",\"default_value\":false,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{},\"settable\":false,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"result_details\":{\"name\":\"result_details\",\"tooltip\":\"Details about the operation result\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"multiline\":true,\"placeholder_text\":\"Details about the completion or failure will be shown here.\"},\"settable\":false,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"image_url\":{\"name\":\"image_url\",\"tooltip\":\"New parameter\",\"type\":\"ImageUrlArtifact\",\"input_types\":[\"ImageUrlArtifact\"],\"output_type\":\"ImageUrlArtifact\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"pulse_on_run\":true,\"hide\":false,\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":\"\",\"parent_element_name\":null}}}}"
#
# ///

import argparse
import asyncio
import json
import pickle

from griptape_nodes.bootstrap.workflow_executors.local_workflow_executor import LocalWorkflowExecutor
from griptape_nodes.bootstrap.workflow_executors.workflow_executor import WorkflowExecutor
from griptape_nodes.drivers.storage.storage_backend import StorageBackend
from griptape_nodes.node_library.library_registry import IconVariant, NodeDeprecationMetadata, NodeMetadata
from griptape_nodes.retained_mode.events.connection_events import CreateConnectionRequest
from griptape_nodes.retained_mode.events.flow_events import (
    CreateFlowRequest,
    GetTopLevelFlowRequest,
    GetTopLevelFlowResultSuccess,
)
from griptape_nodes.retained_mode.events.library_events import LoadLibrariesRequest
from griptape_nodes.retained_mode.events.node_events import CreateNodeRequest
from griptape_nodes.retained_mode.events.parameter_events import (
    AddParameterToNodeRequest,
    AlterParameterDetailsRequest,
    SetParameterValueRequest,
)
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

GriptapeNodes.handle_request(LoadLibrariesRequest())

context_manager = GriptapeNodes.ContextManager()

if not context_manager.has_current_workflow():
    context_manager.push_workflow(workflow_name="image_flow")

"""
1. We've collated all of the unique parameter values into a dictionary so that we do not have to duplicate them.
   This minimizes the size of the code, especially for large objects like serialized image files.
2. We're using a prefix so that it's clear which Flow these values are associated with.
3. The values are serialized using pickle, which is a binary format. This makes them harder to read, but makes
   them consistently save and load. It allows us to serialize complex objects like custom classes, which otherwise
   would be difficult to serialize.
"""
top_level_unique_values_dict = {
    "04059676-ae2c-4583-8c5c-7ca425c08c82": pickle.loads(
        b"\x80\x04\x95\n\x00\x00\x00\x00\x00\x00\x00\x8c\x06cookie\x94."
    ),
    "bfced1c7-e31a-45ad-afe7-72c5c7d15565": pickle.loads(
        b'\x80\x04\x95\xbd\x04\x00\x00\x00\x00\x00\x00}\x94(\x8c\x04type\x94\x8c\x12GriptapeNodesAgent\x94\x8c\x08rulesets\x94]\x94\x8c\x05rules\x94]\x94\x8c\x02id\x94\x8c 5c05919e0e5c4f089d177a60760c8fc7\x94\x8c\x13conversation_memory\x94}\x94(h\x01\x8c\x12ConversationMemory\x94\x8c\x04runs\x94]\x94}\x94(h\x01\x8c\x03Run\x94h\x07\x8c 1d9cfcc8fa4945dba3454d94549f6d07\x94\x8c\x04meta\x94N\x8c\x05input\x94}\x94(h\x01\x8c\x0cTextArtifact\x94h\x07\x8c 4f2aa25c31014e62ab5510b2904a5b4b\x94\x8c\treference\x94Nh\x11}\x94\x8c\x04name\x94h\x15\x8c\x05value\x94\x8cuCreate an image generation prompt about the following subject. ONLY respond with the image generation prompt:\n\ncookie\x94u\x8c\x06output\x94}\x94(h\x01h\x14h\x07\x8c dc9a7e19f9024ed38a1a10135eeb9066\x94h\x16Nh\x11}\x94\x8c\x0fis_react_prompt\x94\x89sh\x18h\x1dh\x19X\x04\x01\x00\x00"A close-up of a freshly baked chocolate chip cookie, golden brown with melted chocolate chips glistening, sitting on a rustic wooden table with crumbs scattered around, warm sunlight streaming through a nearby window, creating a cozy and inviting atmosphere."\x94uuah\x11}\x94\x8c\x08max_runs\x94Nu\x8c\x1cconversation_memory_strategy\x94\x8c\rper_structure\x94\x8c\x05tasks\x94]\x94}\x94(h\x01\x8c\nPromptTask\x94h\x03]\x94h\x05]\x94h\x07\x8c 046f764087f949a3b7f6954df61f4835\x94\x8c\x05state\x94\x8c\x0eState.FINISHED\x94\x8c\nparent_ids\x94]\x94\x8c\tchild_ids\x94]\x94\x8c\x17max_meta_memory_entries\x94K\x14\x8c\x07context\x94}\x94\x8c\rprompt_driver\x94}\x94(h\x01\x8c\x19GriptapeCloudPromptDriver\x94\x8c\x0btemperature\x94G?\xb9\x99\x99\x99\x99\x99\x9a\x8c\nmax_tokens\x94N\x8c\x06stream\x94\x88\x8c\x0cextra_params\x94}\x94\x8c\x05model\x94\x8c\x06gpt-4o\x94\x8c\x1astructured_output_strategy\x94\x8c\x06native\x94u\x8c\x05tools\x94]\x94\x8c\x0cmax_subtasks\x94K\x14uau.'
    ),
    "da9dce99-aad4-4210-904e-864b4a8e73c5": pickle.loads(
        b"\x80\x04\x95\n\x00\x00\x00\x00\x00\x00\x00\x8c\x06gpt-4o\x94."
    ),
    "92e4cbaf-854a-4059-a1e0-ecb7ab0f3f98": pickle.loads(
        b"\x80\x04\x95y\x00\x00\x00\x00\x00\x00\x00\x8cuCreate an image generation prompt about the following subject. ONLY respond with the image generation prompt:\n\ncookie\x94."
    ),
    "7436f412-acbe-4fbc-a993-4287bc56fc20": pickle.loads(b"\x80\x04\x95\x04\x00\x00\x00\x00\x00\x00\x00\x8c\x00\x94."),
    "ce7b5b38-6317-499d-83eb-1806292a386d": pickle.loads(b"\x80\x04]\x94."),
    "d6bd2d35-1433-4280-98af-989a74591c66": pickle.loads(b"\x80\x04]\x94."),
    "f9dadf46-352f-4afe-8b9d-6c5c03d73eec": pickle.loads(
        b'\x80\x04\x95\x0b\x01\x00\x00\x00\x00\x00\x00X\x04\x01\x00\x00"A close-up of a freshly baked chocolate chip cookie, golden brown with melted chocolate chips glistening, sitting on a rustic wooden table with crumbs scattered around, warm sunlight streaming through a nearby window, creating a cozy and inviting atmosphere."\x94.'
    ),
    "01ae91d6-6701-4bbf-a31c-8f5b6cf3db59": pickle.loads(b"\x80\x04\x89."),
    "bb7ae55e-eefc-4937-9410-288b0093317c": pickle.loads(
        b"\x80\x04\x95N\x00\x00\x00\x00\x00\x00\x00\x8cJ[Processing..]\n[Started processing agent..]\n\n[Finished processing agent.]\n\x94."
    ),
    "94124382-734c-4dfc-a13f-480c96090f44": pickle.loads(
        b"\x80\x04\x95q\x00\x00\x00\x00\x00\x00\x00\x8cmCreate an image generation prompt about the following subject. ONLY respond with the image generation prompt:\x94."
    ),
    "13f790ba-7c87-4600-8481-b7b29bc7fa14": pickle.loads(
        b"\x80\x04\x95\x08\x00\x00\x00\x00\x00\x00\x00\x8c\x04\\n\\n\x94."
    ),
    "95560651-da51-46ca-a7fe-f162660e2290": pickle.loads(
        b"\x80\x04\x95\x10\x00\x00\x00\x00\x00\x00\x00\x8c\x0cseedream-4.5\x94."
    ),
    "9d86cb66-5d80-40a1-a568-277e40c716a7": pickle.loads(b"\x80\x04]\x94."),
    "e7f6e6e8-cee8-4791-9d2f-1a8bf1d0ca3a": pickle.loads(
        b"\x80\x04\x95\x06\x00\x00\x00\x00\x00\x00\x00\x8c\x022K\x94."
    ),
    "fb70b008-7d9c-4e73-ae45-4a903199fe14": pickle.loads(
        b"\x80\x04\x95\x06\x00\x00\x00\x00\x00\x00\x00J\xff\xff\xff\xff."
    ),
    "70ae025e-d3e5-4164-a3f7-0bc47793124c": pickle.loads(b"\x80\x04K\n."),
    "548956b9-e0b1-4186-b506-0db53b5bd71d": pickle.loads(
        b"\x80\x04\x95\n\x00\x00\x00\x00\x00\x00\x00G@\x04\x00\x00\x00\x00\x00\x00."
    ),
}

"# Create the Flow, then do work within it as context."

flow0_name = GriptapeNodes.handle_request(
    CreateFlowRequest(parent_flow_name=None, flow_name="ControlFlow_1", set_as_new_context=False, metadata={})
).flow_name

with GriptapeNodes.ContextManager().flow(flow0_name):
    node0_name = GriptapeNodes.handle_request(
        CreateNodeRequest(
            node_type="StartFlow",
            specific_library_name="Griptape Nodes Library",
            node_name="Start Flow",
            metadata={
                "position": {"x": -25.23067388810523, "y": 680},
                "tempId": "placing-1765414068937-40c9c8",
                "library_node_metadata": NodeMetadata(
                    category="workflows",
                    description="Define the start of a workflow and pass parameters into the flow",
                    display_name="Start Flow",
                    tags=None,
                    icon=None,
                    color=None,
                    group="create",
                    deprecation=None,
                    is_node_group=None,
                ),
                "library": "Griptape Nodes Library",
                "node_type": "StartFlow",
                "showaddparameter": True,
                "size": {"width": 600, "height": 330},
                "category": "workflows",
            },
            resolution="resolved",
            initial_setup=True,
        )
    ).node_name
    with GriptapeNodes.ContextManager().node(node0_name):
        GriptapeNodes.handle_request(
            AddParameterToNodeRequest(
                parameter_name="subject",
                tooltip="Enter text/string for subject.",
                type="str",
                input_types=["str"],
                output_type="str",
                ui_options={"is_custom": True, "is_user_added": True},
                mode_allowed_input=False,
                mode_allowed_property=True,
                mode_allowed_output=True,
                initial_setup=True,
            )
        )
    node1_name = GriptapeNodes.handle_request(
        CreateNodeRequest(
            node_type="Agent",
            specific_library_name="Griptape Nodes Library",
            node_name="Agent",
            metadata={
                "position": {"x": 1587.5923303327736, "y": 680},
                "tempId": "placing-1765414081641-sm6s5g",
                "library_node_metadata": NodeMetadata(
                    category="agents",
                    description="Creates an AI agent with conversation memory and the ability to use tools",
                    display_name="Agent",
                    tags=None,
                    icon=None,
                    color=None,
                    group="create",
                    deprecation=None,
                    is_node_group=None,
                ),
                "library": "Griptape Nodes Library",
                "node_type": "Agent",
                "showaddparameter": False,
                "size": {"width": 600, "height": 864},
                "category": "agents",
            },
            resolution="resolved",
            initial_setup=True,
        )
    ).node_name
    node2_name = GriptapeNodes.handle_request(
        CreateNodeRequest(
            node_type="MergeTexts",
            specific_library_name="Griptape Nodes Library",
            node_name="Merge Texts",
            metadata={
                "position": {"x": 825.8068482564886, "y": 680},
                "tempId": "placing-1765414102456-ackjem",
                "library_node_metadata": NodeMetadata(
                    category="text",
                    description="MergeTexts node",
                    display_name="Merge Texts",
                    tags=None,
                    icon="merge",
                    color=None,
                    group="merge",
                    deprecation=None,
                    is_node_group=None,
                ),
                "library": "Griptape Nodes Library",
                "node_type": "MergeTexts",
                "showaddparameter": False,
                "size": {"width": 600, "height": 500},
                "category": "text",
            },
            resolution="resolved",
            initial_setup=True,
        )
    ).node_name
    node3_name = GriptapeNodes.handle_request(
        CreateNodeRequest(
            node_type="EndFlow",
            specific_library_name="Griptape Nodes Library",
            node_name="End Flow",
            metadata={
                "library_node_metadata": NodeMetadata(
                    category="workflows",
                    description="Define the end of a workflow and return parameters from the flow",
                    display_name="End Flow",
                    tags=None,
                    icon=None,
                    color=None,
                    group="create",
                    deprecation=None,
                    is_node_group=None,
                ),
                "library": "Griptape Nodes Library",
                "node_type": "EndFlow",
                "showaddparameter": True,
                "position": {"x": 3124.417619119165, "y": 680},
                "size": {"width": 701, "height": 858},
            },
            initial_setup=True,
        )
    ).node_name
    with GriptapeNodes.ContextManager().node(node3_name):
        GriptapeNodes.handle_request(
            AddParameterToNodeRequest(
                parameter_name="image_url",
                default_value="",
                tooltip="New parameter",
                type="ImageUrlArtifact",
                input_types=["ImageUrlArtifact"],
                output_type="ImageUrlArtifact",
                ui_options={"pulse_on_run": True, "hide": False, "is_custom": True, "is_user_added": True},
                mode_allowed_input=True,
                mode_allowed_property=True,
                mode_allowed_output=True,
                parent_container_name="",
                initial_setup=True,
            )
        )
    node4_name = GriptapeNodes.handle_request(
        CreateNodeRequest(
            node_type="SeedreamImageGeneration",
            specific_library_name="Griptape Nodes Library",
            node_name="Seedream Image Generation",
            metadata={
                "library_node_metadata": NodeMetadata(
                    category="image",
                    description="Generate images using Seedream models (seedream-4.0, seedream-3.0-t2i) via Griptape model proxy",
                    display_name="Seedream Image Generation",
                    tags=None,
                    icon="Sparkles",
                    color=None,
                    group="create",
                    deprecation=None,
                    is_node_group=None,
                ),
                "library": "Griptape Nodes Library",
                "node_type": "SeedreamImageGeneration",
                "position": {"x": 2318.934686611417, "y": 680},
                "size": {"width": 600, "height": 928},
            },
            initial_setup=True,
        )
    ).node_name
    GriptapeNodes.handle_request(
        CreateConnectionRequest(
            source_node_name=node0_name,
            source_parameter_name="subject",
            target_node_name=node2_name,
            target_parameter_name="input_2",
            initial_setup=True,
        )
    )
    GriptapeNodes.handle_request(
        CreateConnectionRequest(
            source_node_name=node2_name,
            source_parameter_name="output",
            target_node_name=node1_name,
            target_parameter_name="prompt",
            initial_setup=True,
        )
    )
    GriptapeNodes.handle_request(
        CreateConnectionRequest(
            source_node_name=node1_name,
            source_parameter_name="output",
            target_node_name=node4_name,
            target_parameter_name="prompt",
            initial_setup=True,
        )
    )
    GriptapeNodes.handle_request(
        CreateConnectionRequest(
            source_node_name=node4_name,
            source_parameter_name="image_url",
            target_node_name=node3_name,
            target_parameter_name="image_url",
            initial_setup=True,
        )
    )
    with GriptapeNodes.ContextManager().node(node0_name):
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="subject",
                node_name=node0_name,
                value=top_level_unique_values_dict["04059676-ae2c-4583-8c5c-7ca425c08c82"],
                initial_setup=True,
                is_output=False,
            )
        )
    with GriptapeNodes.ContextManager().node(node1_name):
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="agent",
                node_name=node1_name,
                value=top_level_unique_values_dict["bfced1c7-e31a-45ad-afe7-72c5c7d15565"],
                initial_setup=True,
                is_output=True,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="model",
                node_name=node1_name,
                value=top_level_unique_values_dict["da9dce99-aad4-4210-904e-864b4a8e73c5"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="prompt",
                node_name=node1_name,
                value=top_level_unique_values_dict["92e4cbaf-854a-4059-a1e0-ecb7ab0f3f98"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="additional_context",
                node_name=node1_name,
                value=top_level_unique_values_dict["7436f412-acbe-4fbc-a993-4287bc56fc20"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="tools",
                node_name=node1_name,
                value=top_level_unique_values_dict["ce7b5b38-6317-499d-83eb-1806292a386d"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="rulesets",
                node_name=node1_name,
                value=top_level_unique_values_dict["d6bd2d35-1433-4280-98af-989a74591c66"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="output",
                node_name=node1_name,
                value=top_level_unique_values_dict["7436f412-acbe-4fbc-a993-4287bc56fc20"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="output",
                node_name=node1_name,
                value=top_level_unique_values_dict["f9dadf46-352f-4afe-8b9d-6c5c03d73eec"],
                initial_setup=True,
                is_output=True,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="include_details",
                node_name=node1_name,
                value=top_level_unique_values_dict["01ae91d6-6701-4bbf-a31c-8f5b6cf3db59"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="logs",
                node_name=node1_name,
                value=top_level_unique_values_dict["bb7ae55e-eefc-4937-9410-288b0093317c"],
                initial_setup=True,
                is_output=True,
            )
        )
    with GriptapeNodes.ContextManager().node(node2_name):
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="input_1",
                node_name=node2_name,
                value=top_level_unique_values_dict["94124382-734c-4dfc-a13f-480c96090f44"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="input_2",
                node_name=node2_name,
                value=top_level_unique_values_dict["04059676-ae2c-4583-8c5c-7ca425c08c82"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="input_4",
                node_name=node2_name,
                value=top_level_unique_values_dict["7436f412-acbe-4fbc-a993-4287bc56fc20"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="merge_string",
                node_name=node2_name,
                value=top_level_unique_values_dict["13f790ba-7c87-4600-8481-b7b29bc7fa14"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="whitespace",
                node_name=node2_name,
                value=top_level_unique_values_dict["01ae91d6-6701-4bbf-a31c-8f5b6cf3db59"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="output",
                node_name=node2_name,
                value=top_level_unique_values_dict["92e4cbaf-854a-4059-a1e0-ecb7ab0f3f98"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="output",
                node_name=node2_name,
                value=top_level_unique_values_dict["92e4cbaf-854a-4059-a1e0-ecb7ab0f3f98"],
                initial_setup=True,
                is_output=True,
            )
        )
    with GriptapeNodes.ContextManager().node(node3_name):
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="was_successful",
                node_name=node3_name,
                value=top_level_unique_values_dict["01ae91d6-6701-4bbf-a31c-8f5b6cf3db59"],
                initial_setup=True,
                is_output=False,
            )
        )
    with GriptapeNodes.ContextManager().node(node4_name):
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="model",
                node_name=node4_name,
                value=top_level_unique_values_dict["95560651-da51-46ca-a7fe-f162660e2290"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="prompt",
                node_name=node4_name,
                value=top_level_unique_values_dict["f9dadf46-352f-4afe-8b9d-6c5c03d73eec"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="images",
                node_name=node4_name,
                value=top_level_unique_values_dict["9d86cb66-5d80-40a1-a568-277e40c716a7"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="size",
                node_name=node4_name,
                value=top_level_unique_values_dict["e7f6e6e8-cee8-4791-9d2f-1a8bf1d0ca3a"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="seed",
                node_name=node4_name,
                value=top_level_unique_values_dict["fb70b008-7d9c-4e73-ae45-4a903199fe14"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="max_images",
                node_name=node4_name,
                value=top_level_unique_values_dict["70ae025e-d3e5-4164-a3f7-0bc47793124c"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="guidance_scale",
                node_name=node4_name,
                value=top_level_unique_values_dict["548956b9-e0b1-4186-b506-0db53b5bd71d"],
                initial_setup=True,
                is_output=False,
            )
        )
        GriptapeNodes.handle_request(
            SetParameterValueRequest(
                parameter_name="was_successful",
                node_name=node4_name,
                value=top_level_unique_values_dict["01ae91d6-6701-4bbf-a31c-8f5b6cf3db59"],
                initial_setup=True,
                is_output=False,
            )
        )


def _ensure_workflow_context():
    context_manager = GriptapeNodes.ContextManager()
    if not context_manager.has_current_flow():
        top_level_flow_request = GetTopLevelFlowRequest()
        top_level_flow_result = GriptapeNodes.handle_request(top_level_flow_request)
        if (
            isinstance(top_level_flow_result, GetTopLevelFlowResultSuccess)
            and top_level_flow_result.flow_name is not None
        ):
            flow_manager = GriptapeNodes.FlowManager()
            flow_obj = flow_manager.get_flow_by_name(top_level_flow_result.flow_name)
            context_manager.push_flow(flow_obj)


def execute_workflow(
    input: dict,
    storage_backend: str = "local",
    workflow_executor: WorkflowExecutor | None = None,
    pickle_control_flow_result: bool = False,
) -> dict | None:
    return asyncio.run(
        aexecute_workflow(
            input=input,
            storage_backend=storage_backend,
            workflow_executor=workflow_executor,
            pickle_control_flow_result=pickle_control_flow_result,
        )
    )


async def aexecute_workflow(
    input: dict,
    storage_backend: str = "local",
    workflow_executor: WorkflowExecutor | None = None,
    pickle_control_flow_result: bool = False,
) -> dict | None:
    _ensure_workflow_context()
    storage_backend_enum = StorageBackend(storage_backend)
    workflow_executor = workflow_executor or LocalWorkflowExecutor(storage_backend=storage_backend_enum)
    async with workflow_executor as executor:
        await executor.arun(flow_input=input, pickle_control_flow_result=pickle_control_flow_result)
    return executor.output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--storage-backend",
        choices=["local", "gtc"],
        default="local",
        help="Storage backend to use: 'local' for local filesystem or 'gtc' for Griptape Cloud",
    )
    parser.add_argument(
        "--json-input",
        default=None,
        help="JSON string containing parameter values. Takes precedence over individual parameter arguments if provided.",
    )
    parser.add_argument("--exec_out", default=None, help="Connection to the next node in the execution chain")
    parser.add_argument("--subject", default=None, help="Enter text/string for subject.")
    args = parser.parse_args()
    flow_input = {}
    if args.json_input is not None:
        flow_input = json.loads(args.json_input)
    if args.json_input is None:
        if "Start Flow" not in flow_input:
            flow_input["Start Flow"] = {}
        if args.exec_out is not None:
            flow_input["Start Flow"]["exec_out"] = args.exec_out
        if args.subject is not None:
            flow_input["Start Flow"]["subject"] = args.subject
    workflow_output = execute_workflow(input=flow_input, storage_backend=args.storage_backend)
    print(workflow_output)
