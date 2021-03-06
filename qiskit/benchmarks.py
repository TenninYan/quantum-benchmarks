import pytest
import mkl
import uuid
from qiskit import *
from qiskit.compiler import transpile, assemble
mkl.set_num_threads(1)

backend = Aer.get_backend('statevector_simulator')

def _execute(circuit):
    experiment = transpile(circuit)
    qobj = assemble(experiment)
    qobj_str = backend._format_qobj_str(qobj, None, None)
    return backend._controller(qobj_str)

def native_execute(benchmark, circuit):
    experiment = transpile(circuit)
    qobj = assemble(experiment)
    qobj_str = backend._format_qobj_str(qobj, None, None)
    benchmark(backend._controller, qobj_str)

def run_bench(benchmark, nqubits, gate, locs=(1, )):
    q = QuantumRegister(nqubits)
    qc = QuantumCircuit(q)
    getattr(qc, gate)(*locs)
    native_execute(benchmark, qc)

def first_rotation(circuit, qubits):
    for each in qubits:
        circuit.rx(1.0, each)
        circuit.rz(1.0, each)
    return circuit

def mid_rotation(circuit, qubits):
    for each in qubits:
        circuit.rz(1.0, each)
        circuit.rx(1.0, each)
        circuit.rz(1.0, each)
    return circuit

def last_rotation(circuit, qubits):
    for each in qubits:
        circuit.rz(1.0, each)
        circuit.rx(1.0, each)
    return circuit

def entangler(circuit, qubits, pairs):
    for a, b in pairs:
        circuit.cx(qubits[a], qubits[b])
    return circuit

def generate_qcbm_circuit(n, depth, pairs):
    qubits = QuantumRegister(n)
    circuit = QuantumCircuit(qubits)
    
    for each in qubits:
        circuit.rx(1.0, each)
        circuit.rz(1.0, each)

    circuit = entangler(circuit, qubits, pairs)
    for k in range(depth-1):
        circuit = mid_rotation(circuit, qubits)
        circuit = entangler(circuit, qubits, pairs)
    circuit = last_rotation(circuit, qubits)
    return circuit


nbit_list = range(4,26)

@pytest.mark.parametrize('nqubits', nbit_list)
def test_X(benchmark, nqubits):
    benchmark.group = "X"
    run_bench(benchmark, nqubits, 'x')

@pytest.mark.parametrize('nqubits', nbit_list)
def test_H(benchmark, nqubits):
    benchmark.group = "H"
    run_bench(benchmark, nqubits, 'h')

@pytest.mark.parametrize('nqubits', nbit_list)
def test_T(benchmark, nqubits):
    benchmark.group = "T"
    run_bench(benchmark, nqubits, 't')

@pytest.mark.parametrize('nqubits', nbit_list)
def test_CX(benchmark, nqubits):
    benchmark.group = "CNOT"
    run_bench(benchmark, nqubits, 'cx', (1, 2))

@pytest.mark.parametrize('nqubits', nbit_list)
def test_Toffoli(benchmark, nqubits):
    benchmark.group = "Toffoli"
    run_bench(benchmark, nqubits, 'ccx', (2, 3, 0))

# Rotation Z/X is not supported
# @pytest.mark.parametrize('nqubits', nbit_list)
# def test_qcbm(benchmark, nqubits):
#     benchmark.group = "QCBM"
#     circuit = generate_qcbm_circuit(nqubits, 9,
#         [(i, (i+1)%nqubits) for i in range(nqubits)])
#     native_execute(benchmark, circuit)
