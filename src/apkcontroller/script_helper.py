"""Functions to assist a script file for an arbitrary app."""
import time
from typing import TYPE_CHECKING, Dict, List, Tuple, Union

import networkx as nx
import xmltodict
from typeguard import typechecked
from uiautomator import AutomatorDevice

if TYPE_CHECKING:
    from src.apkcontroller.org_torproject_android.V16_6_3_RC_1.script import (
        Apk_script,
    )
    from src.apkcontroller.Screen import Screen
else:
    Screen = object
    Apk_script = object


@typechecked
def get_start_nodes(script_graph: nx.DiGraph) -> List[int]:
    """Sets the start_nodes attributes to True in the nodes that are start
    screens."""
    start_nodenames: List[int] = []
    for nodename in script_graph.nodes:
        if script_graph.nodes[nodename]["is_start"]:
            start_nodenames.append(nodename)
    return start_nodenames


@typechecked
def get_end_nodes(script_graph: nx.DiGraph) -> List[int]:
    """Sets the end_nodes attributes to True in the nodes that are end
    screens."""
    end_nodenames: List[int] = []
    for nodename in script_graph.nodes:
        if script_graph.nodes[nodename]["is_end"]:
            end_nodenames.append(nodename)
    return end_nodenames


@typechecked
def get_expected_screens(
    expected_screennames: List[int], script_graph: nx.DiGraph
) -> List[Screen]:
    """Determines whether the current screen is one of the expected screens."""
    expected_screens: List[Screen] = []
    for nodename in script_graph.nodes:
        if nodename in expected_screennames:
            expected_screens.append(script_graph.nodes[nodename]["Screen"])

    return expected_screens


@typechecked
def get_current_screen_unpacked(device: AutomatorDevice) -> Dict:
    """Returns the meaningful dict from the phone UI."""
    # Load and unpack the screen dict to get meaningful ui info.
    screen_dict: Dict = get_screen_as_dict(device)
    unpacked_screen_dict: Dict = screen_dict["hierarchy"]
    return unpacked_screen_dict


@typechecked
def current_screen_is_expected(
    expected_screennames: List[int],
    unpacked_screen_dict: Dict,
    script_graph: nx.DiGraph,
) -> Tuple[bool, int]:
    """Determines whether the current screen is one of the expected screens."""
    expected_screens: List[Screen] = get_expected_screens(
        expected_screennames, script_graph
    )
    for expected_screen in expected_screens:
        if is_expected_screen(
            unpacked_screen_dict=unpacked_screen_dict,
            expected_screen=expected_screen,
        ):

            return (True, int(expected_screen.script_description["screen_nr"]))
    return (False, -1)


@typechecked
def is_expected_screen(
    unpacked_screen_dict: Dict,
    expected_screen: Screen,
) -> bool:
    """Custom verification per screen based on the optional and required
    objects in screen.

    Raise error if verification fails.
    """
    # Preliminary check to see if the required objects are in.
    if not required_objects_in_screen(
        expected_screen.required_objects, unpacked_screen_dict
    ):
        # Retry and return True if the required objects were found.
        for _ in range(0, expected_screen.max_retries):
            time.sleep(expected_screen.wait_time_sec)
            if required_objects_in_screen(
                required_objects=expected_screen.required_objects,
                unpacked_screen_dict=unpacked_screen_dict,
            ):
                return True
        # Return false otherwise.
        return False
    # else:
    return True


@typechecked
def required_objects_in_screen(
    required_objects: List[Dict[str, Union[List, Dict, str]]],
    unpacked_screen_dict: Dict[str, Union[List, Dict, str]],
) -> bool:
    """Returns True if all required objects are found in the UI/screen.

    False otherwise.
    """
    for required_object in required_objects:
        if not required_object_in_screen(
            required_object=required_object,
            unpacked_screen_dict=unpacked_screen_dict,
        ):
            return False
    return True


@typechecked
def get_screen_as_dict(device: AutomatorDevice) -> Dict:
    """Loads the phone and shows the screen as a dict.

    from uiautomator import device as d
    """
    doc = xmltodict.parse(device.dump())
    return doc


@typechecked
def required_object_in_screen(
    required_object: Dict[str, Union[List, Dict, str]],
    unpacked_screen_dict: Dict[str, Union[List, Dict, str]],
) -> bool:
    """Returns True if all the keys and values in a dict are found within the
    same key or list of the xml of the ui."""
    if dict_contains_other_dict(required_object, unpacked_screen_dict):
        return True
    if "node" in unpacked_screen_dict.keys():
        if isinstance(unpacked_screen_dict["node"], Dict):
            if required_object_in_screen(
                required_object=required_object,
                unpacked_screen_dict=unpacked_screen_dict["node"],
            ):
                return True
        if isinstance(unpacked_screen_dict["node"], List):
            for node_elem in unpacked_screen_dict["node"]:
                if required_object_in_screen(
                    required_object=required_object,
                    unpacked_screen_dict=node_elem,
                ):
                    return True
        if not isinstance(unpacked_screen_dict["node"], Dict | List):
            raise TypeError("Node value of unexpected type.")
    return False


@typechecked
def dict_contains_other_dict(sub: Dict, main: Dict) -> bool:
    """Returns true if the sub dict is a subset of the main dict."""
    for sub_key, sub_val in sub.items():
        if sub_key not in main.keys():
            return False
        # An artifact like:
        # "@text": "VPN Mode \u200e\u200f\u200e\u200e\u200e\u200e\u200e\u200f
        # \u200e\u200f\u200f\u200f\u200e\u200e\u200e\u200e\u200e\u200e\u200f\
        # u200e\u200e\u200f\u200e\u200e\u200e\u200e\u200f\u200f\u200f\u200f\
        # u200f\u200e\u200e\u200f\u200f\u200e\u200e\u200e\u200f\u200e\u200e\
        # u200f\u200e\u200e\u200e\u200e\u200e\u200e\u200f\u200e\u200f\u200f\
        # u200f\u200e\u200e\u200e\u200e\u200e\u200e\u200f\u200e\u200f\u200e\
        # u200e\u200e\u200e\u200e\u200e\u200e\u200f\u200e\u200e\u200e\u200e\
        # u200f\u200e\u200e\u200e\u200f\u200f\u200f\u200f\u200f\u200e\u200e\
        # u200f\u200f\u200e\u200f\u200f\u200e\u200e\u200e\u200eON\u200e\u200f
        # \u200e\u200e\u200f\u200e",
        # may occur at random. Therefore, the "in" option is included.
        # TODO: determine why these artifacts may occur and/or remove them.
        if sub_val != main[sub_key] and sub_val not in main[sub_key]:
            return False
    return True


@typechecked
def can_proceed(
    device: AutomatorDevice,
    expected_screennames: List[int],
    script: Apk_script,
) -> Tuple[bool, int]:
    """Checks whether the screen is expected, raises an error if not.

    And it returns the current screen number.
    """
    # get current screen dict.
    unpacked_screen_dict: Dict = get_current_screen_unpacked(device)

    # verify current_screen in next_screens.
    is_expected, screen_nr = current_screen_is_expected(
        expected_screennames=expected_screennames,
        unpacked_screen_dict=unpacked_screen_dict,
        script_graph=script.script_graph,
    )

    # end_screens = get end_screens()
    if not is_expected:
        # TODO: Export the actual screen, screen data and expected screens in
        # specific error log folder.
        raise ReferenceError("Error, the expected screen was not found.")
    return is_expected, screen_nr