# /// script
# dependencies = []
# 
# [tool.griptape-nodes]
# name = "character_image_flow"
# schema_version = "0.14.0"
# engine_version_created_with = "0.65.3"
# node_libraries_referenced = [["Griptape Nodes Library", "0.52.3"]]
# node_types_used = [["Griptape Nodes Library", "Agent"], ["Griptape Nodes Library", "DictGetValueByKey"], ["Griptape Nodes Library", "EndFlow"], ["Griptape Nodes Library", "GoogleImageGeneration"], ["Griptape Nodes Library", "MergeTexts"], ["Griptape Nodes Library", "StartFlow"], ["Griptape Nodes Library", "ToDictionary"], ["Griptape Nodes Library", "ToText"]]
# is_griptape_provided = false
# creation_date = 2025-12-11T04:48:59.912027Z
# last_modified_date = 2025-12-11T04:53:25.353365Z
# workflow_shape = "{\"inputs\":{\"Start Flow\":{\"exec_out\":{\"name\":\"exec_out\",\"tooltip\":\"Connection to the next node in the execution chain\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Flow Out\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"character_dictionary\":{\"name\":\"character_dictionary\",\"tooltip\":\"New parameter\",\"type\":\"any\",\"input_types\":[\"any\"],\"output_type\":\"any\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":\"\",\"parent_element_name\":null}}},\"outputs\":{\"End Flow\":{\"exec_in\":{\"name\":\"exec_in\",\"tooltip\":\"Control path when the flow completed successfully\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Succeeded\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"failed\":{\"name\":\"failed\",\"tooltip\":\"Control path when the flow failed\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"display_name\":\"Failed\"},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"was_successful\":{\"name\":\"was_successful\",\"tooltip\":\"Indicates whether it completed without errors.\",\"type\":\"bool\",\"input_types\":[\"bool\"],\"output_type\":\"bool\",\"default_value\":false,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{},\"settable\":false,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"result_details\":{\"name\":\"result_details\",\"tooltip\":\"Details about the operation result\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"multiline\":true,\"placeholder_text\":\"Details about the completion or failure will be shown here.\"},\"settable\":false,\"is_user_defined\":true,\"parent_container_name\":null,\"parent_element_name\":null},\"image\":{\"name\":\"image\",\"tooltip\":\"New parameter\",\"type\":\"ImageUrlArtifact\",\"input_types\":[\"ImageUrlArtifact\"],\"output_type\":\"ImageUrlArtifact\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"ui_options\":{\"is_full_width\":true,\"pulse_on_run\":true,\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"parent_container_name\":\"\",\"parent_element_name\":null}}}}"
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
    context_manager.push_workflow(workflow_name='character_image_flow')

"""
1. We've collated all of the unique parameter values into a dictionary so that we do not have to duplicate them.
   This minimizes the size of the code, especially for large objects like serialized image files.
2. We're using a prefix so that it's clear which Flow these values are associated with.
3. The values are serialized using pickle, which is a binary format. This makes them harder to read, but makes
   them consistently save and load. It allows us to serialize complex objects like custom classes, which otherwise
   would be difficult to serialize.
"""
top_level_unique_values_dict = {'8c73633c-b969-40b5-acf2-059baf4acc04': pickle.loads(b'\x80\x04\x95\x04\x00\x00\x00\x00\x00\x00\x00\x8c\x00\x94.'), '0ac76194-6235-4e20-950c-5815d2f38e86': pickle.loads(b'\x80\x04}\x94.'), '366cca24-27d6-400b-aa54-af0a22d44627': pickle.loads(b'\x80\x04\x95\x18\x00\x00\x00\x00\x00\x00\x00\x8c\x14physical_description\x94.'), '98364002-048f-49ec-9543-7f68cf1aaf45': pickle.loads(b'\x80\x04\x89.'), '76ea7b9a-9070-403f-a2d0-c33a2f2dc63c': pickle.loads(b'\x80\x04\x95\r\x00\x00\x00\x00\x00\x00\x00\x8c\tlifestyle\x94.'), '8fb4e547-f2a0-4e19-8973-3aec552ee412': pickle.loads(b'\x80\x04\x95\n\x00\x00\x00\x00\x00\x00\x00\x8c\x06gpt-4o\x94.'), '44ba1ace-8ba8-46d8-a8fc-1f995eccc28b': pickle.loads(b'\x80\x04\x95\xbb\x00\x00\x00\x00\x00\x00\x00\x8c\xb7Given this description, generate an image generation prompt of this person. It should be a full body portrait of them doing an activity that fits their temperment, in a cartoon style.\x94.'), 'b8cb528e-e88f-4f72-b83e-53e822a7e679': pickle.loads(b'\x80\x04]\x94.'), '5e0b6758-efe4-44d0-8995-398536168f29': pickle.loads(b'\x80\x04]\x94.'), '4577d102-e304-4a98-a0d9-f8125c940020': pickle.loads(b'\x80\x04\x95\x08\x00\x00\x00\x00\x00\x00\x00\x8c\x04None\x94.'), 'a4eb254d-a28f-4ac4-83a4-d8a64272ebca': pickle.loads(b'\x80\x04\x95\x06\x00\x00\x00\x00\x00\x00\x00\x8c\x02\\n\x94.'), '80bec537-0c9a-4be0-ab5f-0e8eed97f3e2': pickle.loads(b'\x80\x04\x95\r\x00\x00\x00\x00\x00\x00\x00\x8c\tNone\nNone\x94.'), '73df6a22-f79d-4ea3-9202-a72216b9b934': pickle.loads(b'\x80\x04\x95\x15\x00\x00\x00\x00\x00\x00\x00\x8c\x11nano-banana-3-pro\x94.'), '810ecf5d-12ac-4c61-95c8-e0e0968e1923': pickle.loads(b'\x80\x04]\x94.'), '54dbfe2b-6094-4c44-9f48-fae896aeed59': pickle.loads(b'\x80\x04]\x94.'), 'c7415c75-0402-4093-92f0-2e0c21daa1d4': pickle.loads(b'\x80\x04]\x94.'), '24e5c261-c03b-4ff0-b58a-6020954f35e9': pickle.loads(b'\x80\x04\x88.'), '23b07a02-7d17-4efa-be33-199985267127': pickle.loads(b'\x80\x04\x95\x08\x00\x00\x00\x00\x00\x00\x00\x8c\x0416:9\x94.'), '5135fd12-a0ad-4832-a7d5-19aa291fb75d': pickle.loads(b'\x80\x04\x95\x06\x00\x00\x00\x00\x00\x00\x00\x8c\x021K\x94.'), 'dd1b6ac2-e144-42ea-9d0e-180aa3893fc6': pickle.loads(b'\x80\x04\x95\n\x00\x00\x00\x00\x00\x00\x00G?\xf0\x00\x00\x00\x00\x00\x00.')}

'# Create the Flow, then do work within it as context.'

flow0_name = GriptapeNodes.handle_request(CreateFlowRequest(parent_flow_name=None, flow_name='ControlFlow_1', set_as_new_context=False, metadata={})).flow_name

with GriptapeNodes.ContextManager().flow(flow0_name):
    node0_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='StartFlow', specific_library_name='Griptape Nodes Library', node_name='Start Flow', metadata={'position': {'x': 421.66954040527344, 'y': 610.0086784362793}, 'tempId': 'placing-1765428544311-9eyzch', 'library_node_metadata': {'category': 'workflows', 'description': 'Define the start of a workflow and pass parameters into the flow'}, 'library': 'Griptape Nodes Library', 'node_type': 'StartFlow', 'showaddparameter': True, 'size': {'width': 635, 'height': 448}, 'category': 'workflows'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node0_name):
        GriptapeNodes.handle_request(AddParameterToNodeRequest(parameter_name='character_dictionary', default_value='', tooltip='New parameter', type='any', input_types=['any'], output_type='any', ui_options={'is_custom': True, 'is_user_added': True}, mode_allowed_input=True, mode_allowed_property=True, mode_allowed_output=True, parent_container_name='', initial_setup=True))
    node1_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='ToDictionary', specific_library_name='Griptape Nodes Library', node_name='To Dictionary', metadata={'position': {'x': 1211.6695404052734, 'y': 751.6753451029459}, 'tempId': 'placing-1765428578055-c58lo9', 'library_node_metadata': {'category': 'convert', 'description': 'Converts incoming value to a dictionary'}, 'library': 'Griptape Nodes Library', 'node_type': 'ToDictionary', 'showaddparameter': False, 'size': {'width': 600, 'height': 435}, 'category': 'convert'}, initial_setup=True)).node_name
    node2_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='DictGetValueByKey', specific_library_name='Griptape Nodes Library', node_name='Get Dictionary Value by Key', metadata={'position': {'x': 2100.0028737386074, 'y': 625.0086784362792}, 'tempId': 'placing-1765428598058-iiipj4', 'library_node_metadata': {'category': 'dict', 'description': 'Get a value from a dictionary by key with optional default handling'}, 'library': 'Griptape Nodes Library', 'node_type': 'DictGetValueByKey', 'showaddparameter': False, 'size': {'width': 600, 'height': 372}, 'category': 'dict'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node2_name):
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='default_value_if_not_found', ui_options={'hide': True}, initial_setup=True))
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='value', type='all', input_types=['all'], output_type='all', initial_setup=True))
    node3_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='DictGetValueByKey', specific_library_name='Griptape Nodes Library', node_name='Get Dictionary Value by Key_1', metadata={'position': {'x': 2073.3362070719404, 'y': 1046.3420117696128}, 'tempId': 'placing-1765428598058-iiipj4', 'library_node_metadata': {'category': 'dict', 'description': 'Get a value from a dictionary by key with optional default handling'}, 'library': 'Griptape Nodes Library', 'node_type': 'DictGetValueByKey', 'showaddparameter': False, 'size': {'width': 600, 'height': 372}, 'category': 'dict'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node3_name):
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='default_value_if_not_found', ui_options={'hide': True}, initial_setup=True))
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='value', type='all', input_types=['all'], output_type='all', initial_setup=True))
    node4_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='Agent', specific_library_name='Griptape Nodes Library', node_name='Agent', metadata={'position': {'x': 4118.002873738607, 'y': 554.6753451029458}, 'tempId': 'placing-1765428618024-d9nmi', 'library_node_metadata': {'category': 'agents', 'description': 'Creates an AI agent with conversation memory and the ability to use tools'}, 'library': 'Griptape Nodes Library', 'node_type': 'Agent', 'showaddparameter': False, 'size': {'width': 662, 'height': 622}, 'category': 'agents'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node4_name):
        GriptapeNodes.handle_request(AlterParameterDetailsRequest(parameter_name='additional_context', mode_allowed_property=False, initial_setup=True))
    node5_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='MergeTexts', specific_library_name='Griptape Nodes Library', node_name='Merge Texts', metadata={'position': {'x': 3426.6695404052743, 'y': 595.0086784362793}, 'tempId': 'placing-1765428701094-ywky09', 'library_node_metadata': {'category': 'text', 'description': 'MergeTexts node'}, 'library': 'Griptape Nodes Library', 'node_type': 'MergeTexts', 'showaddparameter': False, 'size': {'width': 600, 'height': 500}, 'category': 'text', 'empty_merge_string_migrated': True}, initial_setup=True)).node_name
    node6_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='ToText', specific_library_name='Griptape Nodes Library', node_name='To Text', metadata={'position': {'x': 2753.3362070719404, 'y': 635.0086784362796}, 'tempId': 'placing-1765428706774-acvmda', 'library_node_metadata': {'category': 'convert', 'description': 'Converts incoming value to text'}, 'library': 'Griptape Nodes Library', 'node_type': 'ToText', 'showaddparameter': False, 'size': {'width': 600, 'height': 280}, 'category': 'convert'}, initial_setup=True)).node_name
    node7_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='ToText', specific_library_name='Griptape Nodes Library', node_name='To Text_1', metadata={'position': {'x': 2753.3362070719404, 'y': 1018.3420117696128}, 'tempId': 'placing-1765428706774-acvmda', 'library_node_metadata': {'category': 'convert', 'description': 'Converts incoming value to text'}, 'library': 'Griptape Nodes Library', 'node_type': 'ToText', 'showaddparameter': False, 'size': {'width': 600, 'height': 280}, 'category': 'convert'}, initial_setup=True)).node_name
    node8_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='GoogleImageGeneration', specific_library_name='Griptape Nodes Library', node_name='Google Nano Banana Image Generation', metadata={'position': {'x': 4958.33620707194, 'y': 635.0086784362796}, 'tempId': 'placing-1765428754093-obdxkn', 'library_node_metadata': {'category': 'image', 'description': 'Generate images using Google models via Griptape model proxy'}, 'library': 'Griptape Nodes Library', 'node_type': 'GoogleImageGeneration', 'showaddparameter': False, 'size': {'width': 600, 'height': 711}, 'category': 'image'}, initial_setup=True)).node_name
    node9_name = GriptapeNodes.handle_request(CreateNodeRequest(node_type='EndFlow', specific_library_name='Griptape Nodes Library', node_name='End Flow', metadata={'position': {'x': 5650.002873738608, 'y': 673.3420117696129}, 'tempId': 'placing-1765428765544-xn604t', 'library_node_metadata': {'category': 'workflows', 'description': 'Define the end of a workflow and return parameters from the flow'}, 'library': 'Griptape Nodes Library', 'node_type': 'EndFlow', 'showaddparameter': True, 'size': {'width': 600, 'height': 543}, 'category': 'workflows'}, initial_setup=True)).node_name
    with GriptapeNodes.ContextManager().node(node9_name):
        GriptapeNodes.handle_request(AddParameterToNodeRequest(parameter_name='image', default_value='', tooltip='New parameter', type='ImageUrlArtifact', input_types=['ImageUrlArtifact'], output_type='ImageUrlArtifact', ui_options={'is_full_width': True, 'pulse_on_run': True, 'is_custom': True, 'is_user_added': True}, mode_allowed_input=True, mode_allowed_property=True, mode_allowed_output=True, parent_container_name='', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node0_name, source_parameter_name='character_dictionary', target_node_name=node1_name, target_parameter_name='from', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node1_name, source_parameter_name='output', target_node_name=node2_name, target_parameter_name='dict', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node1_name, source_parameter_name='output', target_node_name=node3_name, target_parameter_name='dict', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node2_name, source_parameter_name='value', target_node_name=node6_name, target_parameter_name='from', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node5_name, source_parameter_name='output', target_node_name=node4_name, target_parameter_name='additional_context', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node6_name, source_parameter_name='output', target_node_name=node5_name, target_parameter_name='input_1', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node3_name, source_parameter_name='value', target_node_name=node7_name, target_parameter_name='from', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node7_name, source_parameter_name='output', target_node_name=node5_name, target_parameter_name='input_2', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node4_name, source_parameter_name='exec_out', target_node_name=node8_name, target_parameter_name='exec_in', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node4_name, source_parameter_name='output', target_node_name=node8_name, target_parameter_name='prompt', initial_setup=True))
    GriptapeNodes.handle_request(CreateConnectionRequest(source_node_name=node8_name, source_parameter_name='image', target_node_name=node9_name, target_parameter_name='image', initial_setup=True))
    with GriptapeNodes.ContextManager().node(node0_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='character_dictionary', node_name=node0_name, value=top_level_unique_values_dict['8c73633c-b969-40b5-acf2-059baf4acc04'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node1_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node1_name, value=top_level_unique_values_dict['8c73633c-b969-40b5-acf2-059baf4acc04'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node1_name, value=top_level_unique_values_dict['0ac76194-6235-4e20-950c-5815d2f38e86'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node2_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='dict', node_name=node2_name, value=top_level_unique_values_dict['0ac76194-6235-4e20-950c-5815d2f38e86'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='key', node_name=node2_name, value=top_level_unique_values_dict['366cca24-27d6-400b-aa54-af0a22d44627'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='supply_default_if_not_found', node_name=node2_name, value=top_level_unique_values_dict['98364002-048f-49ec-9543-7f68cf1aaf45'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node3_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='dict', node_name=node3_name, value=top_level_unique_values_dict['0ac76194-6235-4e20-950c-5815d2f38e86'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='key', node_name=node3_name, value=top_level_unique_values_dict['76ea7b9a-9070-403f-a2d0-c33a2f2dc63c'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='supply_default_if_not_found', node_name=node3_name, value=top_level_unique_values_dict['98364002-048f-49ec-9543-7f68cf1aaf45'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node4_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='model', node_name=node4_name, value=top_level_unique_values_dict['8fb4e547-f2a0-4e19-8973-3aec552ee412'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='prompt', node_name=node4_name, value=top_level_unique_values_dict['44ba1ace-8ba8-46d8-a8fc-1f995eccc28b'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='tools', node_name=node4_name, value=top_level_unique_values_dict['b8cb528e-e88f-4f72-b83e-53e822a7e679'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='rulesets', node_name=node4_name, value=top_level_unique_values_dict['5e0b6758-efe4-44d0-8995-398536168f29'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node4_name, value=top_level_unique_values_dict['8c73633c-b969-40b5-acf2-059baf4acc04'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='include_details', node_name=node4_name, value=top_level_unique_values_dict['98364002-048f-49ec-9543-7f68cf1aaf45'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node5_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_1', node_name=node5_name, value=top_level_unique_values_dict['4577d102-e304-4a98-a0d9-f8125c940020'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_2', node_name=node5_name, value=top_level_unique_values_dict['4577d102-e304-4a98-a0d9-f8125c940020'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='merge_string', node_name=node5_name, value=top_level_unique_values_dict['a4eb254d-a28f-4ac4-83a4-d8a64272ebca'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='whitespace', node_name=node5_name, value=top_level_unique_values_dict['98364002-048f-49ec-9543-7f68cf1aaf45'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node5_name, value=top_level_unique_values_dict['80bec537-0c9a-4be0-ab5f-0e8eed97f3e2'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node5_name, value=top_level_unique_values_dict['80bec537-0c9a-4be0-ab5f-0e8eed97f3e2'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node6_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node6_name, value=top_level_unique_values_dict['8c73633c-b969-40b5-acf2-059baf4acc04'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node6_name, value=top_level_unique_values_dict['4577d102-e304-4a98-a0d9-f8125c940020'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node7_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node7_name, value=top_level_unique_values_dict['8c73633c-b969-40b5-acf2-059baf4acc04'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='output', node_name=node7_name, value=top_level_unique_values_dict['4577d102-e304-4a98-a0d9-f8125c940020'], initial_setup=True, is_output=True))
    with GriptapeNodes.ContextManager().node(node8_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='model', node_name=node8_name, value=top_level_unique_values_dict['73df6a22-f79d-4ea3-9202-a72216b9b934'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='input_images', node_name=node8_name, value=top_level_unique_values_dict['810ecf5d-12ac-4c61-95c8-e0e0968e1923'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='object_images', node_name=node8_name, value=top_level_unique_values_dict['54dbfe2b-6094-4c44-9f48-fae896aeed59'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='human_images', node_name=node8_name, value=top_level_unique_values_dict['c7415c75-0402-4093-92f0-2e0c21daa1d4'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='auto_image_resize', node_name=node8_name, value=top_level_unique_values_dict['24e5c261-c03b-4ff0-b58a-6020954f35e9'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='aspect_ratio', node_name=node8_name, value=top_level_unique_values_dict['23b07a02-7d17-4efa-be33-199985267127'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='image_size', node_name=node8_name, value=top_level_unique_values_dict['5135fd12-a0ad-4832-a7d5-19aa291fb75d'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='temperature', node_name=node8_name, value=top_level_unique_values_dict['dd1b6ac2-e144-42ea-9d0e-180aa3893fc6'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='use_google_search', node_name=node8_name, value=top_level_unique_values_dict['98364002-048f-49ec-9543-7f68cf1aaf45'], initial_setup=True, is_output=False))
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='was_successful', node_name=node8_name, value=top_level_unique_values_dict['98364002-048f-49ec-9543-7f68cf1aaf45'], initial_setup=True, is_output=False))
    with GriptapeNodes.ContextManager().node(node9_name):
        GriptapeNodes.handle_request(SetParameterValueRequest(parameter_name='was_successful', node_name=node9_name, value=top_level_unique_values_dict['98364002-048f-49ec-9543-7f68cf1aaf45'], initial_setup=True, is_output=False))

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
    parser.add_argument('--character_dictionary', default=None, help='New parameter')
    args = parser.parse_args()
    flow_input = {}
    if args.json_input is not None:
        flow_input = json.loads(args.json_input)
    if args.json_input is None:
        if 'Start Flow' not in flow_input:
            flow_input['Start Flow'] = {}
        if args.exec_out is not None:
            flow_input['Start Flow']['exec_out'] = args.exec_out
        if args.character_dictionary is not None:
            flow_input['Start Flow']['character_dictionary'] = args.character_dictionary
    workflow_output = execute_workflow(input=flow_input, storage_backend=args.storage_backend)
    print(workflow_output)
