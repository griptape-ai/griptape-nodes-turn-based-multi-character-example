# /// script
# dependencies = []
# 
# [tool.griptape-nodes]
# name = "story_from_character"
# schema_version = "0.14.0"
# engine_version_created_with = "0.65.3"
# node_libraries_referenced = [["Griptape Nodes Library", "0.52.3"]]
# node_types_used = [["Griptape Nodes Library", "Agent"], ["Griptape Nodes Library", "DictGetValueByKey"], ["Griptape Nodes Library", "EndFlow"], ["Griptape Nodes Library", "MergeTexts"], ["Griptape Nodes Library", "StartFlow"], ["Griptape Nodes Library", "ToDictionary"], ["Griptape Nodes Library", "ToText"]]
# is_griptape_provided = false
# creation_date = 2025-12-11T05:00:00.040643Z
# last_modified_date = 2025-12-11T05:00:00.061123Z
# workflow_shape = "{\"inputs\":{\"Start Flow\":{\"exec_out\":{\"name\":\"exec_out\",\"tooltip\":\"Connection to the next node in the execution chain\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Flow Out\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"character\":{\"name\":\"character\",\"tooltip\":\"New parameter\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":\"\",\"parent_element_name\":null},\"situation\":{\"name\":\"situation\",\"tooltip\":\"New parameter\",\"type\":\"str\",\"input_types\":[\"any\"],\"output_type\":\"str\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"placeholder_text\":\"Input 2\",\"hide_label\":false,\"hide_property\":false,\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":\"\",\"parent_element_name\":null}}},\"outputs\":{\"End Flow\":{\"exec_in\":{\"name\":\"exec_in\",\"tooltip\":\"Control path when the flow completed successfully\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Succeeded\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"failed\":{\"name\":\"failed\",\"tooltip\":\"Control path when the flow failed\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Failed\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"was_successful\":{\"name\":\"was_successful\",\"tooltip\":\"Indicates whether it completed without errors.\",\"type\":\"bool\",\"input_types\":[\"bool\"],\"output_type\":\"bool\",\"default_value\":false,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{},\"settable\":false,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"result_details\":{\"name\":\"result_details\",\"tooltip\":\"Details about the operation result\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"multiline\":true,\"placeholder_text\":\"Details about the completion or failure will be shown here.\"},\"settable\":false,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"story\":{\"name\":\"story\",\"tooltip\":\"New parameter\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"multiline\":true,\"placeholder_text\":\"Agent response\",\"markdown\":false,\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":\"\",\"parent_element_name\":null}}}}"
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
from griptape_nodes.retained_mode.events.flow_events import CreateFlowRequest, GetTopLevelFlowRequest, GetTopLevelFlowResultSuccess
from griptape_nodes.retained_mode.events.library_events import LoadLibrariesRequest
from griptape_nodes.retained_mode.events.node_events import CreateNodeRequest
from griptape_nodes.retained_mode.events.parameter_events import AddParameterToNodeRequest, AlterParameterDetailsRequest, SetParameterValueRequest
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

GriptapeNodes.handle_request(LoadLibrariesRequest())

context_manager = GriptapeNodes.ContextManager()

if not context_manager.has_current_workflow():
    context_manager.push_workflow(workflow_name='story_from_character')

"""
1. We've collated all of the unique parameter values into a dictionary so that we do not have to duplicate them.
   This minimizes the size of the code, especially for large objects like serialized image files.
2. We're using a prefix so that it's clear which Flow these values are associated with.
3. The values are serialized using pickle, which is a binary format. This makes them harder to read, but makes
   them consistently save and load. It allows us to serialize complex objects like custom classes, which otherwise
   would be difficult to serialize.
"""
top_level_unique_values_dict = {'8a43a89a-dbb9-4579-8170-8faa1e51adf6': pickle.loads(b'\x80\x04\x95\x04\x00\x00\x00\x00\x00\x00\x00\x8c\x00\x94.'), '12d6b792-5c95-4c66-880c-c4633730df91': pickle.loads(b'\x80\x04\x95\n\x00\x00\x00\x00\x00\x00\x00\x8c\x06gpt-4o\x94.'), '947c8415-e154-4886-9c1a-32bac034d99d': pickle.loads(b'\x80\x04\x95b\x00\x00\x00\x00\x00\x00\x00\x8c^Given the description of the character, tell us what the character would do in this situation:\x94.'), 'c00e5ff0-8cf8-45bd-a8ec-34b624804343': pickle.loads(b'\x80\x04\x95`\x00\x00\x00\x00\x00\x00\x00\x8c\\Character name\nNone\ncharacter details\nCharacter Temperment:\n\nNone\n\nCharacter lifestyle\n\nNone\x94.'), 'c3d00f95-34aa-4e94-a535-3cb2ac38a45e': pickle.loads(b'\x80\x04]\x94.'), 'b0a604a6-2336-4896-9c7e-05a286952e9a': pickle.loads(b'\x80\x04]\x94.'), 'a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb': pickle.loads(b'\x80\x04\x89.'), '7e90f4b3-7df6-41b0-babc-82479157a4d7': pickle.loads(b'\x80\x04\x95\x0f\x00\x00\x00\x00\x00\x00\x00}\x94\x8c\x05value\x94\x8c\x00\x94s.'), '49918fee-a54e-4c37-82a4-6c6aeb86084a': pickle.loads(b'\x80\x04\x95\x0f\x00\x00\x00\x00\x00\x00\x00}\x94\x8c\x05value\x94\x8c\x00\x94s.'), '170784df-7644-424a-8d3b-66d3a2f96ca4': pickle.loads(b'\x80\x04\x95\x0e\x00\x00\x00\x00\x00\x00\x00\x8c\ntemperment\x94.'), '7f348f5a-2cd4-4c3b-a7e6-a6bbdfce0b8e': pickle.loads(b'\x80\x04\x95\r\x00\x00\x00\x00\x00\x00\x00\x8c\tlifestyle\x94.'), '5d3b2353-9537-426f-a9ae-6c1695e4d986': pickle.loads(b'\x80\x04\x95\x19\x00\x00\x00\x00\x00\x00\x00\x8c\x15Character Temperment:\x94.'), 'e2a95e1f-b829-4d05-ab42-8a3ea7ad0c49': pickle.loads(b'\x80\x04\x95\x08\x00\x00\x00\x00\x00\x00\x00\x8c\x04None\x94.'), 'b4c0655f-ecb3-492b-9745-a5b5a45743b2': pickle.loads(b'\x80\x04\x95\x17\x00\x00\x00\x00\x00\x00\x00\x8c\x13Character lifestyle\x94.'), 'ac44084a-9266-4ddf-b988-973f9f8f9c66': pickle.loads(b'\x80\x04\x95\x06\x00\x00\x00\x00\x00\x00\x00\x8c\x02\\n\x94.'), 'ac7183ac-7b9d-49e3-adc5-2b4a28c0d407': pickle.loads(b'\x80\x04\x957\x00\x00\x00\x00\x00\x00\x00\x8c3Character Temperment:\nNone\nCharacter lifestyle\nNone\x94.'), '82a86783-385d-4b0d-b2c3-ae9e6a7493a8': pickle.loads(b'\x80\x04\x95\x12\x00\x00\x00\x00\x00\x00\x00\x8c\x0eCharacter name\x94.'), '9926f1dd-e483-4e70-8eba-d5c9fd6e00f8': pickle.loads(b'\x80\x04\x95\x15\x00\x00\x00\x00\x00\x00\x00\x8c\x11character details\x94.'), '40dea8d4-2b66-45d3-9fe4-52ed59ed9ed7': pickle.loads(b'\x80\x04\x95:\x00\x00\x00\x00\x00\x00\x00\x8c6Character Temperment:\n\nNone\n\nCharacter lifestyle\n\nNone\x94.'), 'c68ba27a-10ea-4b3c-8641-7e8b5d0314ea': pickle.loads(b'\x80\x04\x95\x12\x00\x00\x00\x00\x00\x00\x00\x8c\x0echaracter_name\x94.')}

'# Create the Flow, then do work within it as context.'

flow0_name = GriptapeNodes.handle_request(CreateFlowRequest(parent_flow_name=None, flow_name='ControlFlow_1', set_as_new_context=False, metadata={})).flow_name

with GriptapeNodes.ContextManager().flow(flow0_name):
    node0_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='StartFlow', specific_library_name='Griptape Nodes Library', node_name='Start Flow', metadata={'position': {'x': 470.6679766669628, 'y': 697.8568929908799}, 'tempId': 'placing-1765428824618-r7d2ei', 'library_node_metadata': {'category': 'workflows', 'description': 'Define the start of a workflow and pass parameters into the flow'}, 'library': 'Griptape Nodes Library', 'node_type': 'StartFlow', 'showaddparameter': True, 'size': {'width': 704, 'height': 691}, 'category': 'workflows'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node0_name):
        GriptapeNodes.handle_request(AddParameterToNodeRequest(parameter_name='character', default_value='', tooltip='New parameter', type='str', input_types=['str'], output_type='str', ui_options={'is_custom': True, 'is_user_added': True}, mode_allowed_input=True, mode_allowed_property=True, mode_allowed_output=True, parent_container_name='', initial_setup=True))
        GriptapeNodes.handle_request(AddParameterToNodeRequest(parameter_name='situation', default_value='', tooltip='New parameter', type='str', input_types=['any'], output_type='str', ui_options={'placeholder_text': 'Input 2', 'hide_label': False, 'hide_property': False, 'is_custom': True, 'is_user_added': True}, mode_allowed_input=True, mode_allowed_property=True, mode_allowed_output=True, parent_container_name='', initial_setup=True))
    node1_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='Agent', specific_library_name='Griptape Nodes Library', node_name='Agent', metadata={'position': {'x': 5039.985001427942, 'y': 603.4778569625768}, 'tempId': 'placing-1765428930462-qwt3y', 'library_node_metadata': {'category': 'agents', 'description': 'Creates an AI agent with conversation memory and the ability to use tools'}, 'library': 'Griptape Nodes Library', 'node_type': 'Agent', 'showaddparameter': False, 'size': {'width': 600, 'height': 864}, 'category': 'agents'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node1_name):
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='additional_context', mode_allowed_property=False, initial_setup=True))
    node2_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='ToDictionary', specific_library_name='Griptape Nodes Library', node_name='To Dictionary', metadata={'position': {'x': 1254.0388369207224, 'y': 770.7704816852006}, 'tempId': 'placing-1765428960842-b7mkgn', 'library_node_metadata': {'category': 'convert', 'description': 'Converts incoming value to a dictionary'}, 'library': 'Griptape Nodes Library', 'node_type': 'ToDictionary', 'showaddparameter': False, 'size': {'width': 600, 'height': 240}, 'category': 'convert'}, initial_setup=True)).node_name
    node3_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='DictGetValueByKey', specific_library_name='Griptape Nodes Library', node_name='Get Dictionary Value by Key', metadata={'position': {'x': 1965.6506185026192, 'y': 723.6503252899752}, 'tempId': 'placing-1765428968993-potpc', 'library_node_metadata': {'category': 'dict', 'description': 'Get a value from a dictionary by key with optional default handling'}, 'library': 'Griptape Nodes Library', 'node_type': 'DictGetValueByKey', 'showaddparameter': False, 'size': {'width': 600, 'height': 372}, 'category': 'dict'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node3_name):
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='default_value_if_not_found', ui_options={'hide': True}, initial_setup=True))
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='value', type='all', input_types=['all'], output_type='all', initial_setup=True))
    node4_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='DictGetValueByKey', specific_library_name='Griptape Nodes Library', node_name='Get Dictionary Value by Key_1', metadata={'position': {'x': 1965.6506185026192, 'y': 1129.218070744477}, 'tempId': 'placing-1765428968993-potpc', 'library_node_metadata': {'category': 'dict', 'description': 'Get a value from a dictionary by key with optional default handling'}, 'library': 'Griptape Nodes Library', 'node_type': 'DictGetValueByKey', 'showaddparameter': False, 'size': {'width': 600, 'height': 372}, 'category': 'dict'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node4_name):
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='default_value_if_not_found', ui_options={'hide': True}, initial_setup=True))
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='value', type='all', input_types=['all'], output_type='all', initial_setup=True))
    node5_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='MergeTexts', specific_library_name='Griptape Nodes Library', node_name='Merge Texts', metadata={'position': {'x': 3384.273243423427, 'y': 770.7704816852006}, 'tempId': 'placing-1765429003616-cq38c', 'library_node_metadata': {'category': 'text', 'description': 'MergeTexts node'}, 'library': 'Griptape Nodes Library', 'node_type': 'MergeTexts', 'showaddparameter': False, 'size': {'width': 600, 'height': 500}, 'category': 'text', 'empty_merge_string_migrated': True}, initial_setup=True)).node_name
    node6_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='ToText', specific_library_name='Griptape Nodes Library', node_name='To Text', metadata={'position': {'x': 2712.5362599474124, 'y': 730.7704816852006}, 'tempId': 'placing-1765429010030-35v2w', 'library_node_metadata': {'category': 'convert', 'description': 'Converts incoming value to text'}, 'library': 'Griptape Nodes Library', 'node_type': 'ToText', 'showaddparameter': False, 'size': {'width': 600, 'height': 280}, 'category': 'convert'}, initial_setup=True)).node_name
    node7_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='ToText', specific_library_name='Griptape Nodes Library', node_name='To Text_1', metadata={'position': {'x': 2725.728754003521, 'y': 1221.218070744477}, 'tempId': 'placing-1765429010030-35v2w', 'library_node_metadata': {'category': 'convert', 'description': 'Converts incoming value to text'}, 'library': 'Griptape Nodes Library', 'node_type': 'ToText', 'showaddparameter': False, 'size': {'width': 600, 'height': 280}, 'category': 'convert'}, initial_setup=True)).node_name
    node8_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='MergeTexts', specific_library_name='Griptape Nodes Library', node_name='Merge Texts_1', metadata={'position': {'x': 4072.880333790392, 'y': 805.4152560155178}, 'tempId': 'placing-1765429054161-gswpcs', 'library_node_metadata': {'category': 'text', 'description': 'MergeTexts node'}, 'library': 'Griptape Nodes Library', 'node_type': 'MergeTexts', 'showaddparameter': False, 'size': {'width': 600, 'height': 500}, 'category': 'text', 'empty_merge_string_migrated': True}, initial_setup=True)).node_name
    node9_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='DictGetValueByKey', specific_library_name='Griptape Nodes Library', node_name='Get Dictionary Value by Key_2', metadata={'position': {'x': 2041.7226018795423, 'y': 275.21534896644823}, 'tempId': 'placing-1765428968993-potpc', 'library_node_metadata': {'category': 'dict', 'description': 'Get a value from a dictionary by key with optional default handling'}, 'library': 'Griptape Nodes Library', 'node_type': 'DictGetValueByKey', 'showaddparameter': False, 'size': {'width': 600, 'height': 372}, 'category': 'dict'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node9_name):
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='default_value_if_not_found', ui_options={'hide': True}, initial_setup=True))
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='value', type='all', input_types=['all'], output_type='all', initial_setup=True))
    node10_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='ToText', specific_library_name='Griptape Nodes Library', node_name='To Text_2', metadata={'position': {'x': 2725.728754003521, 'y': 250.12893766076888}, 'tempId': 'placing-1765429010030-35v2w', 'library_node_metadata': {'category': 'convert', 'description': 'Converts incoming value to text'}, 'library': 'Griptape Nodes Library', 'node_type': 'ToText', 'showaddparameter': False, 'size': {'width': 600, 'height': 280}, 'category': 'convert'}, initial_setup=True)).node_name
    node11_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='MergeTexts', specific_library_name='Griptape Nodes Library', node_name='Merge Texts_2', metadata={'position': {'x': 4272.254324319802, 'y': 211.21534896644823}, 'tempId': 'placing-1765429114075-pfgbhy', 'library_node_metadata': {'category': 'text', 'description': 'MergeTexts node'}, 'library': 'Griptape Nodes Library', 'node_type': 'MergeTexts', 'showaddparameter': False, 'size': {'width': 600, 'height': 500}, 'category': 'text', 'empty_merge_string_migrated': True}, initial_setup=True)).node_name
    node12_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='EndFlow', specific_library_name='Griptape Nodes Library', node_name='End Flow', metadata={'position': {'x': 5915.760212296291, 'y': 730.7704816852006}, 'tempId': 'placing-1765429183284-f49d4q', 'library_node_metadata': {'category': 'workflows', 'description': 'Define the end of a workflow and return parameters from the flow'}, 'library': 'Griptape Nodes Library', 'node_type': 'EndFlow', 'showaddparameter': True, 'size': {'width': 600, 'height': 300}, 'category': 'workflows'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node12_name):
        GriptapeNodes.handle_request(AddParameterToNodeRequest(parameter_name='story', default_value='', tooltip='New parameter', type='str', input_types=['str'], output_type='str', ui_options={'multiline': True, 'placeholder_text': 'Agent response', 'markdown': False, 'is_custom': True, 'is_user_added': True}, mode_allowed_input=True, mode_allowed_property=True, mode_allowed_output=True, parent_container_name='', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node2_name, source_parameter_name='output', target_node_name=node3_name, target_parameter_name='dict', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node2_name, source_parameter_name='output', target_node_name=node4_name, target_parameter_name='dict', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node4_name, source_parameter_name='value', target_node_name=node7_name, target_parameter_name='from', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node3_name, source_parameter_name='value', target_node_name=node6_name, target_parameter_name='from', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node7_name, source_parameter_name='output', target_node_name=node5_name, target_parameter_name='input_4', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node5_name, source_parameter_name='output', target_node_name=node8_name, target_parameter_name='input_4', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node2_name, source_parameter_name='output', target_node_name=node9_name, target_parameter_name='dict', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node9_name, source_parameter_name='value', target_node_name=node10_name, target_parameter_name='from', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node10_name, source_parameter_name='output', target_node_name=node8_name, target_parameter_name='input_2', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node8_name, source_parameter_name='output', target_node_name=node1_name, target_parameter_name='additional_context', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node11_name, source_parameter_name='output', target_node_name=node1_name, target_parameter_name='prompt', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node0_name, source_parameter_name='character', target_node_name=node2_name, target_parameter_name='from', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node6_name, source_parameter_name='output', target_node_name=node5_name, target_parameter_name='input_2', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node1_name, source_parameter_name='output', target_node_name=node12_name, target_parameter_name='story', initial_setup=True))
    with GriptapeNodes.ContextManager().node(node0_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='character', node_name=node0_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='situation', node_name=node0_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node1_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='model', node_name=node1_name, value=top_level_unique_values_dict['12d6b792-5c95-4c66-880c-c4633730df91'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='prompt', node_name=node1_name, value=top_level_unique_values_dict['947c8415-e154-4886-9c1a-32bac034d99d'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='additional_context', node_name=node1_name, value=top_level_unique_values_dict['c00e5ff0-8cf8-45bd-a8ec-34b624804343'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='tools', node_name=node1_name, value=top_level_unique_values_dict['c3d00f95-34aa-4e94-a535-3cb2ac38a45e'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='rulesets', node_name=node1_name, value=top_level_unique_values_dict['b0a604a6-2336-4896-9c7e-05a286952e9a'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node1_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='include_details', node_name=node1_name, value=top_level_unique_values_dict['a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node2_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='from', node_name=node2_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node2_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node2_name, value=top_level_unique_values_dict['7e90f4b3-7df6-41b0-babc-82479157a4d7'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node3_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='dict', node_name=node3_name, value=top_level_unique_values_dict['49918fee-a54e-4c37-82a4-6c6aeb86084a'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='key', node_name=node3_name, value=top_level_unique_values_dict['170784df-7644-424a-8d3b-66d3a2f96ca4'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='supply_default_if_not_found', node_name=node3_name, value=top_level_unique_values_dict['a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node4_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='dict', node_name=node4_name, value=top_level_unique_values_dict['49918fee-a54e-4c37-82a4-6c6aeb86084a'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='key', node_name=node4_name, value=top_level_unique_values_dict['7f348f5a-2cd4-4c3b-a7e6-a6bbdfce0b8e'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='supply_default_if_not_found', node_name=node4_name, value=top_level_unique_values_dict['a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node5_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_1', node_name=node5_name, value=top_level_unique_values_dict['5d3b2353-9537-426f-a9ae-6c1695e4d986'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_2', node_name=node5_name, value=top_level_unique_values_dict['e2a95e1f-b829-4d05-ab42-8a3ea7ad0c49'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_3', node_name=node5_name, value=top_level_unique_values_dict['b4c0655f-ecb3-492b-9745-a5b5a45743b2'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_4', node_name=node5_name, value=top_level_unique_values_dict['e2a95e1f-b829-4d05-ab42-8a3ea7ad0c49'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='merge_string', node_name=node5_name, value=top_level_unique_values_dict['ac44084a-9266-4ddf-b988-973f9f8f9c66'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='whitespace', node_name=node5_name, value=top_level_unique_values_dict['a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node5_name, value=top_level_unique_values_dict['ac7183ac-7b9d-49e3-adc5-2b4a28c0d407'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node5_name, value=top_level_unique_values_dict['ac7183ac-7b9d-49e3-adc5-2b4a28c0d407'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node6_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node6_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node6_name, value=top_level_unique_values_dict['e2a95e1f-b829-4d05-ab42-8a3ea7ad0c49'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node7_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node7_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node7_name, value=top_level_unique_values_dict['e2a95e1f-b829-4d05-ab42-8a3ea7ad0c49'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node8_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_1', node_name=node8_name, value=top_level_unique_values_dict['82a86783-385d-4b0d-b2c3-ae9e6a7493a8'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_2', node_name=node8_name, value=top_level_unique_values_dict['e2a95e1f-b829-4d05-ab42-8a3ea7ad0c49'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_3', node_name=node8_name, value=top_level_unique_values_dict['9926f1dd-e483-4e70-8eba-d5c9fd6e00f8'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_4', node_name=node8_name, value=top_level_unique_values_dict['40dea8d4-2b66-45d3-9fe4-52ed59ed9ed7'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='merge_string', node_name=node8_name, value=top_level_unique_values_dict['ac44084a-9266-4ddf-b988-973f9f8f9c66'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='whitespace', node_name=node8_name, value=top_level_unique_values_dict['a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node8_name, value=top_level_unique_values_dict['c00e5ff0-8cf8-45bd-a8ec-34b624804343'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node8_name, value=top_level_unique_values_dict['c00e5ff0-8cf8-45bd-a8ec-34b624804343'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node9_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='dict', node_name=node9_name, value=top_level_unique_values_dict['49918fee-a54e-4c37-82a4-6c6aeb86084a'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='key', node_name=node9_name, value=top_level_unique_values_dict['c68ba27a-10ea-4b3c-8641-7e8b5d0314ea'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='supply_default_if_not_found', node_name=node9_name, value=top_level_unique_values_dict['a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node10_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node10_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node10_name, value=top_level_unique_values_dict['e2a95e1f-b829-4d05-ab42-8a3ea7ad0c49'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node11_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_1', node_name=node11_name, value=top_level_unique_values_dict['947c8415-e154-4886-9c1a-32bac034d99d'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='merge_string', node_name=node11_name, value=top_level_unique_values_dict['ac44084a-9266-4ddf-b988-973f9f8f9c66'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='whitespace', node_name=node11_name, value=top_level_unique_values_dict['a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node11_name, value=top_level_unique_values_dict['947c8415-e154-4886-9c1a-32bac034d99d'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node11_name, value=top_level_unique_values_dict['947c8415-e154-4886-9c1a-32bac034d99d'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node12_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='was_successful', node_name=node12_name, value=top_level_unique_values_dict['a11e92ee-22af-4cf1-a28a-1f5ed1fc3afb'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='story', node_name=node12_name, value=top_level_unique_values_dict['8a43a89a-dbb9-4579-8170-8faa1e51adf6'], initial_setup=True, is_output=False))

def _ensure_workflow_context():
    context_manager = GriptapeNodes.ContextManager()
    if not context_manager.has_current_flow():
        top_level_flow_request = GetTopLevelFlowRequest()
        top_level_flow_result = GriptapeNodes.handle_request(top_level_flow_request)
        if isinstance(top_level_flow_result, GetTopLevelFlowResultSuccess) and top_level_flow_result.flow_name is not None:
            flow_manager = GriptapeNodes.FlowManager()
            flow_obj = flow_manager.get_flow_by_name(top_level_flow_result.flow_name)
            context_manager.push_flow(flow_obj)

def execute_workflow(input: dict, storage_backend: str='local', workflow_executor: WorkflowExecutor | None=None, pickle_control_flow_result: bool=False) -> dict | None:
    return asyncio.run(aexecute_workflow(input=input, storage_backend=storage_backend, workflow_executor=workflow_executor, pickle_control_flow_result=pickle_control_flow_result))

async def aexecute_workflow(input: dict, storage_backend: str='local', workflow_executor: WorkflowExecutor | None=None, pickle_control_flow_result: bool=False) -> dict | None:
    _ensure_workflow_context()
    storage_backend_enum = StorageBackend(storage_backend)
    workflow_executor = workflow_executor or LocalWorkflowExecutor(storage_backend=storage_backend_enum)
    async with workflow_executor as executor:
        await executor.arun(flow_input=input, pickle_control_flow_result=pickle_control_flow_result)
    return executor.output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--storage-backend', choices=['local', 'gtc'], default='local', help="Storage backend to use: 'local' for local filesystem or 'gtc' for Griptape Cloud")
    parser.add_argument('--json-input', default=None, help='JSON string containing parameter values. Takes precedence over individual parameter arguments if provided.')
    parser.add_argument('--exec_out', default=None, help='Connection to the next node in the execution chain')
    parser.add_argument('--character', default=None, help='New parameter')
    parser.add_argument('--situation', default=None, help='New parameter')
    args = parser.parse_args()
    flow_input = {}
    if args.json_input is not None:
        flow_input = json.loads(args.json_input)
    if args.json_input is None:
        if 'Start Flow' not in flow_input:
            flow_input['Start Flow'] = {}
        if args.exec_out is not None:
            flow_input['Start Flow']['exec_out'] = args.exec_out
        if args.character is not None:
            flow_input['Start Flow']['character'] = args.character
        if args.situation is not None:
            flow_input['Start Flow']['situation'] = args.situation
    workflow_output = execute_workflow(input=flow_input, storage_backend=args.storage_backend)
    print(workflow_output)
