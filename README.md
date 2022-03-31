# foundrycli.py (🔥, 🐍)

**`foundrycli.py`** is a Python library I have made for personal use; now open source.

It let's you access `forge` and `cast` CLIs from Python scripts and correctly handles the output, with some handy features.

### Features

Run any command as if you were using the terminal

```python
# Get VB's address
vitalik = foundry_cli('cast resolve-name "vitalik.eth"')
```

Use in scripts with composable commands

```python
# Calculate VB's $$$ in stables
for coin in stables:
    sum += foundry_cli('cast call {coin} "balanceOf(address)(uint256)" {vitalik}')
```

Access anything, effortlessly

```python
# Get the hash of the 100th transaction from the latest block
foundry_cli('cast block latest').get("transactions")[100]
```

Automatic output conversion: `str`, `int`, `Decimal`, `dict`, JSON (`str`)

- Whole numbers will be returned as `int` and decimal as `Decimal`, for max precision
- Multiple values, such as `deployer`, `deployedTo`, `transactionHash` will be returned as `dict`
- JSON will be converted to `dict` for superior UX

### Coverage

- [ ] **`forge`** (`forge create` only)
- [x] **`cast`** (100% [`837209b`](https://github.com/onbjerg/foundry-book/blob/837209b68748a84930b8e713de13c3c2be04c850/src/reference/cast.md))

## Instructions

Clone repository

```bash
git clone https://github.com/ZeroEkkusu/foundrycli.py
```

Install libraray

```bash
pip install dist/foundrycli-0.1.0-py3-none-any.whl
```

### Usage

Import `foundry_cli` in your script

```python
from foundrycli import foundry_cli
```

Pass `command` and `force_string_output` (if you want to disable conversion)

```python
balance = foundry_cli('cast balance "vitalik.eth"')
```

Compose commands instead of hardcoding them

```python
ens_name = "vitalik.eth"
balance = foundry_cli(f'cast balance {ens_name}')
```