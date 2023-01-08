"""Entry point for this project, runs the project code based on the cli command
that invokes this script."""


from uiautomator import device

from src.apkcontroller.scripts.org_torproject_android.v16_6_3_RC_1 import (
    Apk_script,
)
from src.apkcontroller.verification.arg_verification import verify_args

from .arg_parser.arg_parser import parse_cli_args
from .arg_parser.process_args import process_args

# Parse command line interface arguments to determine what this script does.
args = parse_cli_args()
verify_args(
    args,
)
process_args(
    args,
)
apk_script = Apk_script(device=device)
