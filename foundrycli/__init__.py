# Welcome to foundrycli.py (🔥, 🐍)
# Add `from foundrycli import foundry_cli` to your script
# See`README.md` for examples

from decimal import Decimal
from subprocess import run, PIPE
from json import loads


def foundry_cli(command: str, force_string_output=False):
    # throw if cli is not forge or cast
    cli = command.split(" ")[0]
    err_msg = None
    if(cli not in ["forge", "cast"]):
        err_msg = "Unknown CLI. Make sure the command begins with `forge` or `cast`."
    elif(cli == "forge" and command.split(" ")[1] != "create"):
        err_msg = "[`forge` CLI] Unsupported subcommand. Only `forge create` is supported at the moment."
    if(err_msg != None):
        raise ValueError(err_msg)

    # modify command
    command = _mod_cmd(command)
    # run command
    out = _run_cmd(command)
    # convert output
    out = _cnv_out(out, force_string_output)
    # format output
    out = _fmt_out(command, out, force_string_output)
    return out


def _mod_cmd(cmd: str):
    # pass --json flag if output can be returned as json but not requested by user
    cmd_parts = cmd.split(" ")
    # determine cli
    cli = cmd_parts[0]
    if(cli == "forge"):
        cmd
    else:
        if(cmd_parts[1] in ["block", "tx"]):
            as_json = False
            for part in cmd_parts:
                if(part == "--json"):
                    as_json = True
            if (as_json == False):
                cmd += " --json"
    return cmd


def _run_cmd(cmd: str):
    cmd_parts = cmd.split(" ")
    # remove any quotes after splitting, e.g. "gm" --> gm
    i = 0
    while(i < len(cmd_parts)):
        part = cmd_parts[i]
        if(part[0] == "\"" and part[-1] == "\""):
            cmd_parts[i] = part[1:-1]
        i = i + 1
    # run command and grab output as string; throw on error
    return run(
        cmd_parts, stdout=PIPE, check=True).stdout.decode('utf-8').rstrip('\n')


def _cnv_out(out: str, force_str: bool):
    # return output as string if string output forced
    if(force_str == True):
        return out
    # return output as int or Decimal if output is decimal number
    simple_out = out.replace('.', '', 1)
    if(simple_out.isnumeric() or out[0] == '-' and simple_out[1:].isnumeric()):
        if(len(out) == len(simple_out)):
            out = int(out)
        else:
            out = Decimal(out)
    # return output as dict if output is valid json
    try:
        out = loads(out)
    # return output (defaults to string)
    finally:
        return out


def _fmt_out(cmd: str, out: str, force_str: bool):
    # determine cli
    cli = cmd.split(" ")[0]
    if(cli == "forge"):
        out = _forge_fmt_out(cmd, out, force_str)
    else:
        out = _cast_fmt_out(cmd, out, force_str)
    # return formated output
    return out


# function for extracting values from output fields
def _extr_from(out: str, field: str):
    # search for given field and grab value
    start = out.find(field+":") + len(field) + 2
    end = out.find('\n', start)
    if(end == -1):
        end = len(out)
    return out[start:end]


# function for forming dicts
def _form_dict(fields: list, vals: list):
    out = {}
    i = 0
    l = len(fields)
    while(i < l):
        # convert to camelCase
        key = ''.join(x for x in fields[i].title() if not x.isspace())
        key = key[0].lower() + key[1:]
        out[key] = vals[i]
        i += 1
    return out


# function for extracting output filed values and formatting as dict
def _extr_fmt_dict(out: str, fields: list):
    vals = []
    for field in fields:
        vals.append(_extr_from(out, field))
    return _form_dict(fields, vals)


# Note: Do not call directly; use _fmt_out instead
def _forge_fmt_out(cmd: str, out: str, force_str: bool):
    subcmd = cmd.split(" ")[1]
    # format create output
    if(subcmd == "create"):
        out = _extr_fmt_dict(
            out, ["Deployer", "Deployed to", "Transaction hash"])
    return out


# Note: Do not call directly; use _fmt_out instead
def _cast_fmt_out(cmd: str, out: str, force_str: bool):
    # function for formatting extracted wallet subcommands' output values as single value or json
    def wallet_subcmd_to_fmt():
        # switch-case behavior
        fmt = {
            "address": _extr_from(out, "Address"),
            "new": _extr_fmt_dict(out, ["Address", "Private Key"]),
            "sign": _extr_from(out, "Signature"),
            "vanity": _extr_fmt_dict(out, ["Address", "Private Key"]),
            "verify": True if out.find("Validation success.") != -1 else False
        }
        return fmt.get(cmd.split(" ")[2])

    # function for extracting 4byte-decode output values and formatting as json
    def four_byte_decode_extr_fmt(out: str):
        # go line by line and form json
        out_parts = out.split("\n")
        out = "{\"matches\":["
        last_sig_num = 0
        last_arg_num = 0
        for line in out_parts:
            match = str(last_sig_num + 1) + ") "
            sig_pos = len(match)
            # begin new entry if signature found
            if(line[0:sig_pos] == match):
                if(last_sig_num != 0):
                    out += "},"
                last_sig_num += 1
                out += "{\"signature\":" + line[sig_pos:]
                last_arg_num = 0
            # extract argument values otherwise
            else:
                last_arg_num += 1
                # convert value
                arg = _cnv_out(line, force_str)
                # add quotes if value is string
                if(type(arg) == str):
                    arg = "\"" + arg + "\""
                else:
                    arg = str(arg)
                out += ",\"argument" + str(last_arg_num) + "\":" + arg
        # finish json
        out += "}]}"
        # convert json to dict if string output not forced and return it
        return _cnv_out(out, force_str)

    subcmd = cmd.split(" ")[1]
    # format 4byte-decode output
    if(subcmd == "4byte-decode"):
        out = four_byte_decode_extr_fmt(out)
    # format wallet subcommands outputs
    elif(subcmd == "wallet"):
        out = wallet_subcmd_to_fmt()
    return out
