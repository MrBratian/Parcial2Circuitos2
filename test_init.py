import builtins
from utils import init_components

# Sequence of simulated user inputs to cover both input capacitors and configs.
# Adjust values as needed.
inputs = iter([
    # Primer amplificador
    '10000',  # R1
    's',      # has_C_input1
    '1e-9',   # C_input1_val
    '2',      # config_input1: choose RC
    '1',      # rc_choice for input1: Serie
    '2',      # retroalimentación primer amplificador: choose RC
    '2',      # rc_choice for retroalimentacion: Paralelo
    '10000',  # R2
    '1e-9',   # C1
    # Segundo amplificador
    '10000',  # R3
    's',      # has_C_input2
    '2e-9',   # C_input2_val
    '2',      # config_input2: choose RC
    '2',      # rc_choice for input2: Paralelo
    '1',      # retroalimentación segundo amplificador: choose Solo R
    '10000'   # R4
])

original_input = builtins.input

def fake_input(prompt=''):
    try:
        val = next(inputs)
        print(prompt + val)
        return val
    except StopIteration:
        return original_input(prompt)

builtins.input = fake_input

try:
    result = init_components()
    print('\nReturned from init_components():')
    print(result)
finally:
    builtins.input = original_input
